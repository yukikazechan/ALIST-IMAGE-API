import os
import asyncio
import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timezone
import httpx
from sqlalchemy.orm import Session

from .. import models, crud
from ..database import SessionLocal
from .image_meta import get_image_info_from_bytes

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".svg"}

class AListSyncService:
    def __init__(self, source_id: int):
        self.source_id = source_id
        self.db: Session = SessionLocal()

    def close(self):
        self.db.close()

    async def _fetch_alist_dir(
        self, client: httpx.AsyncClient, base_url: str, path: str, token: Optional[str]
    ) -> List[Dict[str, Any]]:
        url = f"{base_url}/api/fs/list"
        headers = {}
        if token:
            headers["Authorization"] = token
            
        payload = {
            "path": path,
            "password": "",
            "page": 1,
            "per_page": 0,
            "refresh": True
        }
        
        try:
            resp = await client.post(url, json=payload, headers=headers, timeout=15.0)
            if resp.status_code != 200:
                logger.error(f"AList returned status {resp.status_code} for path {path}: {resp.text}")
                return []
            res_json = resp.json()
            if res_json.get("code") == 200 and res_json.get("data"):
                return res_json["data"].get("content", []) or []
            return []
        except Exception as e:
            logger.error(f"Failed to fetch AList path {path}: {e}")
            return []

    async def _fetch_file_direct_link(
        self, client: httpx.AsyncClient, base_url: str, file_path: str, token: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        url = f"{base_url}/api/fs/get"
        headers = {}
        if token:
            headers["Authorization"] = token
        payload = {"path": file_path, "password": ""}
        try:
            resp = await client.post(url, json=payload, headers=headers, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                return data
        except Exception as e:
            logger.error(f"Failed to get direct link for {file_path}: {e}")
        return None

    def _extract_tags_from_path(self, file_path: str, root_path: str) -> List[str]:
        rel_path = file_path
        if root_path and root_path != "/" and rel_path.startswith(root_path):
            rel_path = rel_path[len(root_path):]
        
        parts = [p.strip() for p in rel_path.strip("/").split("/")[:-1] if p.strip()]
        return list(set(parts))

    async def run_sync(self) -> Dict[str, Any]:
        source = self.db.query(models.StorageSource).filter(models.StorageSource.id == self.source_id).first()
        if not source:
            return {"success": False, "error": f"Source {self.source_id} not found"}

        source.sync_status = "syncing"
        source.sync_message = "Scanning directory recursively..."
        self.db.commit()

        base_url = source.base_url.rstrip("/")
        root_path = source.root_path.rstrip("/") if source.root_path != "/" else ""
        if not root_path:
            root_path = "/"
            
        token = source.token
        scanned_count = 0
        added_count = 0
        updated_count = 0
        current_file_paths: Set[str] = set()

        async with httpx.AsyncClient() as client:
            try:
                dir_queue = [root_path]
                while dir_queue:
                    curr_dir = dir_queue.pop(0)
                    items = await self._fetch_alist_dir(client, base_url, curr_dir, token)
                    
                    for item in items:
                        name = item.get("name", "")
                        is_dir = item.get("is_dir", False)
                        full_item_path = f"{curr_dir.rstrip('/')}/{name}" if curr_dir != "/" else f"/{name}"
                        
                        if is_dir:
                            dir_queue.append(full_item_path)
                            continue

                        # Image file processing
                        ext = os.path.splitext(name)[1].lower()
                        if ext not in IMAGE_EXTENSIONS:
                            continue

                        scanned_count += 1
                        current_file_paths.add(full_item_path)
                        
                        # Get direct raw url
                        raw_url = item.get("raw_url")
                        file_size = item.get("size", 0)
                        
                        if not raw_url:
                            file_info = await self._fetch_file_direct_link(client, base_url, full_item_path, token)
                            if file_info:
                                raw_url = file_info.get("raw_url")
                                file_size = file_size or file_info.get("size", 0)

                        if not raw_url:
                            # Fallback to standard AList direct stream pattern
                            raw_url = f"{base_url}/d{full_item_path}"

                        tags = self._extract_tags_from_path(full_item_path, root_path)
                        
                        # Check existing
                        existing_img = self.db.query(models.Image).filter(models.Image.file_path == full_item_path).first()
                        if existing_img:
                            existing_img.raw_url = raw_url
                            existing_img.file_size = file_size
                            # ensure tags
                            for tag_name in tags:
                                tag_obj = crud.get_or_create_tag(self.db, tag_name)
                                if tag_obj not in existing_img.tags:
                                    existing_img.tags.append(tag_obj)
                            updated_count += 1
                        else:
                            # Try to extract dimension from direct stream head/range if possible
                            w, h, orient = 0, 0, "landscape"
                            try:
                                # Fetch first 64KB to parse image header
                                img_resp = await client.get(
                                    raw_url,
                                    headers={"Range": "bytes=0-65535"},
                                    timeout=5.0,
                                    follow_redirects=True
                                )
                                if img_resp.status_code in (200, 206):
                                    w, h, orient = get_image_info_from_bytes(img_resp.content)
                            except Exception:
                                pass

                            tag_objs = [crud.get_or_create_tag(self.db, t) for t in tags]
                            new_img = models.Image(
                                source_id=source.id,
                                file_path=full_item_path,
                                raw_url=raw_url,
                                filename=name,
                                file_size=file_size,
                                mime_type=f"image/{ext.lstrip('.') if ext != '.jpg' else 'jpeg'}",
                                width=w,
                                height=h,
                                orientation=orient,
                                tags=tag_objs
                            )
                            self.db.add(new_img)
                            added_count += 1

                        if (added_count + updated_count) % 50 == 0:
                            self.db.commit()

                self.db.commit()

                # Sync status update
                total_in_source = self.db.query(models.Image).filter(models.Image.source_id == source.id).count()
                source.sync_status = "idle"
                source.last_sync_at = datetime.now(timezone.utc)
                source.total_images_indexed = total_in_source
                source.sync_message = f"Sync finished successfully. Scanned: {scanned_count}, Added: {added_count}, Updated: {updated_count}."
                self.db.commit()

                return {
                    "success": True,
                    "scanned": scanned_count,
                    "added": added_count,
                    "updated": updated_count,
                    "total": total_in_source
                }

            except Exception as e:
                logger.exception(f"Sync error for source {source.id}: {e}")
                self.db.rollback()
                source.sync_status = "error"
                source.sync_message = f"Sync failed: {str(e)}"
                self.db.commit()
                return {"success": False, "error": str(e)}
            finally:
                self.close()

async def trigger_source_sync(source_id: int):
    service = AListSyncService(source_id)
    return await service.run_sync()
