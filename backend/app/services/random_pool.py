import time
import secrets
import threading
from typing import Dict, Set, List, Optional, Tuple
from collections import deque
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from .. import models
from ..database import SessionLocal

@dataclass
class CachedImage:
    id: int
    raw_url: str
    file_path: str
    filename: str
    width: int
    height: int
    orientation: str
    mime_type: str
    file_size: int
    tags: Set[str] = field(default_factory=set)

class InMemoryRandomPool:
    """
    High-Performance In-Memory Tagged Image Pool.
    Provides sub-millisecond random sampling with zero database queries.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(InMemoryRandomPool, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._rw_lock = threading.RLock()
        self.images: Dict[int, CachedImage] = {}
        self.tag_index: Dict[str, Set[int]] = {}
        self.orient_index: Dict[str, Set[int]] = {
            "landscape": set(),
            "portrait": set(),
            "square": set()
        }
        self.all_ids: Set[int] = set()
        
        # Anti-repeat LRU: client_id -> deque of recent image IDs
        self.recent_served: Dict[str, deque] = {}
        self.max_history = 20
        self._initialized = True

    def reload_from_db(self, db: Optional[Session] = None):
        """Warm up / Refresh in-memory indexes from database."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            db_images = db.query(models.Image).filter(models.Image.is_active == True).all()
            with self._rw_lock:
                self.images.clear()
                self.tag_index.clear()
                self.orient_index = {"landscape": set(), "portrait": set(), "square": set()}
                self.all_ids.clear()

                for img in db_images:
                    tag_set = {t.name for t in img.tags}
                    cached = CachedImage(
                        id=img.id,
                        raw_url=img.raw_url,
                        file_path=img.file_path,
                        filename=img.filename,
                        width=img.width,
                        height=img.height,
                        orientation=img.orientation or "landscape",
                        mime_type=img.mime_type or "image/jpeg",
                        file_size=img.file_size or 0,
                        tags=tag_set
                    )
                    self.images[img.id] = cached
                    self.all_ids.add(img.id)

                    # Orientation index
                    if cached.orientation in self.orient_index:
                        self.orient_index[cached.orientation].add(img.id)
                    else:
                        self.orient_index["landscape"].add(img.id)

                    # Tag index
                    for t in tag_set:
                        if t not in self.tag_index:
                            self.tag_index[t] = set()
                        self.tag_index[t].add(img.id)
        finally:
            if close_db:
                db.close()

    def sample_random(
        self,
        allowed_tags_and: Optional[List[str]] = None,
        allowed_tags_or: Optional[List[str]] = None,
        blocked_tags: Optional[List[str]] = None,
        orientation: Optional[str] = None,
        min_width: int = 0,
        min_height: int = 0,
        client_fingerprint: Optional[str] = None
    ) -> Optional[CachedImage]:
        with self._rw_lock:
            if not self.all_ids:
                return None

            # 1. Start with orientation filter
            if orientation and orientation in self.orient_index:
                candidate_ids = set(self.orient_index[orientation])
            else:
                candidate_ids = set(self.all_ids)

            if not candidate_ids:
                return None

            # 2. AND Tags (intersection)
            if allowed_tags_and:
                for t in allowed_tags_and:
                    t_clean = t.strip()
                    if t_clean:
                        t_ids = self.tag_index.get(t_clean, set())
                        candidate_ids &= t_ids
                        if not candidate_ids:
                            return None

            # 3. OR Tags (union)
            if allowed_tags_or:
                or_pool = set()
                has_valid_or = False
                for t in allowed_tags_or:
                    t_clean = t.strip()
                    if t_clean:
                        has_valid_or = True
                        or_pool |= self.tag_index.get(t_clean, set())
                if has_valid_or:
                    candidate_ids &= or_pool
                    if not candidate_ids:
                        return None

            # 4. Blocked Tags (difference)
            if blocked_tags:
                for t in blocked_tags:
                    t_clean = t.strip()
                    if t_clean and t_clean in self.tag_index:
                        candidate_ids -= self.tag_index[t_clean]
                if not candidate_ids:
                    return None

            # 5. Resolution filter
            if min_width > 0 or min_height > 0:
                candidate_ids = {
                    img_id for img_id in candidate_ids
                    if self.images[img_id].width >= min_width and self.images[img_id].height >= min_height
                }
                if not candidate_ids:
                    return None

            # 6. Anti-repeat selection
            id_list = list(candidate_ids)
            chosen_id = None
            
            if client_fingerprint:
                recent = self.recent_served.get(client_fingerprint)
                if recent and len(id_list) > len(recent):
                    unseen_candidates = [x for x in id_list if x not in recent]
                    if unseen_candidates:
                        chosen_id = secrets.choice(unseen_candidates)
                
                if chosen_id is None:
                    chosen_id = secrets.choice(id_list)

                # Record in history
                if client_fingerprint not in self.recent_served:
                    self.recent_served[client_fingerprint] = deque(maxlen=self.max_history)
                self.recent_served[client_fingerprint].append(chosen_id)
            else:
                chosen_id = secrets.choice(id_list)

            return self.images.get(chosen_id)

random_pool = InMemoryRandomPool()
