import io
import struct
from typing import Tuple, Optional

def get_image_info_from_bytes(data: bytes) -> Tuple[int, int, str]:
    """
    Extract width, height, and orientation from image bytes (first few KB is often enough).
    Returns: (width, height, orientation)
    """
    try:
        from PIL import Image as PILImage
        img = PILImage.open(io.BytesIO(data))
        w, h = img.size
        
        if w > h:
            orientation = "landscape"
        elif h > w:
            orientation = "portrait"
        else:
            orientation = "square"
            
        return w, h, orientation
    except Exception:
        return 0, 0, "landscape"
