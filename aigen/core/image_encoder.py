import base64
import mimetypes

class ImageEncoder:
    """Encodes images to base64 strings."""
    @staticmethod
    def encode_image(image_path: str) -> str:
        with open(image_path, "rb") as img:
            return base64.b64encode(img.read()).decode("utf-8")
    
    @staticmethod
    def get_mime_type(image_path):
        mime_type, _ = mimetypes.guess_type(image_path)
        # Fallback if not recognized
        return mime_type or "application/octet-stream"
