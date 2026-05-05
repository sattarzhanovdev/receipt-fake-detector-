from io import BytesIO

from PIL import Image, UnidentifiedImageError


def read_image_upload(image_bytes: bytes) -> Image.Image:
    try:
        image = Image.open(BytesIO(image_bytes))
        return image.convert("RGB")
    except UnidentifiedImageError as exc:
        raise ValueError("Invalid image file") from exc
