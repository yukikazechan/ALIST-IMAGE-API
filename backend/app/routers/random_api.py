import json
import io
import httpx
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request, Query, Header, status
from fastapi.responses import RedirectResponse, StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, crud
from ..services.random_pool import random_pool
from ..services.rate_limiter import security_governor

router = APIRouter(tags=["Public Random API"])

@router.get("/api/v1/random/{key}")
async def get_random_image(
    key: str,
    request: Request,
    format: str = Query("redirect", regex="^(redirect|proxy|json)$", description="Output mode"),
    tag: Optional[str] = Query(None, description="Comma separated tags to filter"),
    orientation: Optional[str] = Query(None, regex="^(landscape|portrait|square)$"),
    min_w: int = Query(0, ge=0),
    min_h: int = Query(0, ge=0),
    webp: bool = Query(False, description="Convert to webp on proxy mode"),
    referer: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    # 1. Resolve API Key
    api_key_obj = crud.get_api_key_by_key(db, key)
    if not api_key_obj:
        raise HTTPException(status_code=403, detail="Invalid or deactivated API Key")

    client_ip = request.client.host if request.client else "unknown"

    # 2. Rate Limit & Whitelist Check
    if not security_governor.check_rate_limit(key, api_key_obj.rate_limit_qpm):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please slow down.")

    # Referer whitelist
    ref_whitelist = json.loads(api_key_obj.referer_whitelist or "[]")
    if ref_whitelist and not security_governor.check_referer(referer or "", ref_whitelist):
        raise HTTPException(status_code=403, detail="Referer not allowed by API Key whitelist.")

    # IP whitelist
    ip_whitelist = json.loads(api_key_obj.ip_whitelist or "[]")
    if ip_whitelist and not security_governor.check_ip(client_ip, ip_whitelist):
        raise HTTPException(status_code=403, detail="IP address not authorized.")

    # 3. Build Tags and Filter constraints
    allowed_and = json.loads(api_key_obj.allowed_tags_and or "[]")
    allowed_or = json.loads(api_key_obj.allowed_tags_or or "[]")
    blocked = json.loads(api_key_obj.blocked_tags or "[]")

    if tag:
        custom_tags = [t.strip() for t in tag.split(",") if t.strip()]
        allowed_and = list(set(allowed_and + custom_tags))

    orient = orientation or (api_key_obj.orientation_filter if api_key_obj.orientation_filter != "all" else None)

    # 4. In-Memory Fast Sample
    client_fp = f"{key}:{client_ip}"
    sampled = random_pool.sample_random(
        allowed_tags_and=allowed_and,
        allowed_tags_or=allowed_or,
        blocked_tags=blocked,
        orientation=orient,
        min_width=min_w,
        min_height=min_h,
        client_fingerprint=client_fp
    )

    if not sampled:
        raise HTTPException(status_code=404, detail="No matching images found for the given criteria.")

    # Async increment counter
    api_key_obj.total_calls = (api_key_obj.total_calls or 0) + 1
    db.commit()

    # 5. Output Response Dispatch
    if format == "json":
        return {
            "code": 200,
            "data": {
                "id": sampled.id,
                "url": sampled.raw_url,
                "filename": sampled.filename,
                "width": sampled.width,
                "height": sampled.height,
                "orientation": sampled.orientation,
                "mime_type": sampled.mime_type,
                "file_size": sampled.file_size,
                "tags": list(sampled.tags)
            }
        }

    if format == "proxy":
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                img_resp = await client.get(sampled.raw_url, timeout=15.0)
                if img_resp.status_code != 200:
                    return RedirectResponse(url=sampled.raw_url, status_code=302)

                content = img_resp.content
                content_type = sampled.mime_type

                if webp and content_type != "image/webp":
                    try:
                        from PIL import Image as PILImage
                        pil_img = PILImage.open(io.BytesIO(content))
                        out_buf = io.BytesIO()
                        pil_img.save(out_buf, format="WEBP", quality=85)
                        content = out_buf.getvalue()
                        content_type = "image/webp"
                    except Exception:
                        pass

                return StreamingResponse(
                    io.BytesIO(content),
                    media_type=content_type,
                    headers={
                        "Cache-Control": "public, max-age=3600",
                        "Content-Disposition": f'inline; filename="{sampled.filename}"'
                    }
                )
            except Exception:
                return RedirectResponse(url=sampled.raw_url, status_code=302)

    # Default: 302 Redirect
    return RedirectResponse(
        url=sampled.raw_url,
        status_code=302,
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )
