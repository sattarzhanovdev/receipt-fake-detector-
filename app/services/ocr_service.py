from PIL import Image


def extract_text(image: Image.Image) -> str:
    text = _extract_text_easyocr(image)
    if text:
        return text

    return _extract_text_pytesseract(image)


def _extract_text_easyocr(image: Image.Image) -> str:
    try:
        import easyocr
    except ImportError:
        return ""

    try:
        reader = easyocr.Reader(["ru", "en"], gpu=False)
        result = reader.readtext(image)
        return "\n".join([item[1] for item in result]).strip()
    except Exception:
        return ""


def _extract_text_pytesseract(image: Image.Image) -> str:
    try:
        import pytesseract
    except ImportError:
        return ""

    try:
        return pytesseract.image_to_string(image, lang="rus+eng").strip()
    except Exception:
        return ""
