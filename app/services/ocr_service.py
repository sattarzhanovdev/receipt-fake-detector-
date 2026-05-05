from PIL import Image


def extract_text(image: Image.Image) -> str:
    try:
        import pytesseract
    except ImportError:
        return ""

    try:
        return pytesseract.image_to_string(image, lang="rus+eng").strip()
    except Exception:
        return ""
