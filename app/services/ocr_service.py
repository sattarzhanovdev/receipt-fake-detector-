from PIL import Image, ImageEnhance, ImageOps


def extract_text(image: Image.Image) -> tuple[str, str | None]:
    image = _preprocess_image(image)

    text, backend = _extract_text_easyocr(image)
    if text:
        return text, backend

    text, backend = _extract_text_pytesseract(image)
    return text, backend


def _preprocess_image(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    grayscale = image.convert("L")
    image = ImageOps.autocontrast(grayscale)

    width, height = image.size
    min_size = 1200
    if width < min_size or height < min_size:
        ratio = max(min_size / width, min_size / height)
        image = image.resize((int(width * ratio), int(height * ratio)), Image.LANCZOS)

    image = ImageEnhance.Contrast(image).enhance(1.5)
    image = ImageEnhance.Sharpness(image).enhance(1.3)
    return image


def _extract_text_easyocr(image: Image.Image) -> tuple[str, str | None]:
    try:
        import easyocr
    except ImportError:
        return "", None

    try:
        import numpy as np
        reader = easyocr.Reader(["ru", "en"], gpu=False)
        result = reader.readtext(np.array(image))
        text = "\n".join([item[1] for item in result]).strip()
        return text, "easyocr"
    except Exception:
        return "", None


def _extract_text_pytesseract(image: Image.Image) -> tuple[str, str | None]:
    try:
        import pytesseract
    except ImportError:
        return "", None

    try:
        text = pytesseract.image_to_string(image, lang="rus+eng", config="--psm 6").strip()
        return text, "pytesseract" if text else ("", None)[1]
    except Exception:
        return "", None
