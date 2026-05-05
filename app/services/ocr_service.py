from PIL import Image


def extract_text(image: Image.Image) -> str:
    try:
        import easyocr
    except ImportError:
        return ""

    try:
        reader = easyocr.Reader(['ru', 'en'], gpu=False)
        result = reader.readtext(image)
        text = "\n".join([item[1] for item in result])
        return text.strip()
    except Exception:
        return ""
