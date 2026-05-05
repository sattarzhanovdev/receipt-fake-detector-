import io
import os

import httpx
from PIL import Image, ImageEnhance, ImageOps


def extract_text(image: Image.Image) -> tuple[str, str | None, str | None]:
    image = _preprocess_image(image)

    text, backend, error = _extract_text_remote(image)
    if text:
        return text, backend, error
    
    remote_error = error

    text, backend, error = _extract_text_easyocr(image)
    if text:
        return text, backend, error
    
    easy_error = error

    text, backend, error = _extract_text_pytesseract(image)
    if text:
        return text, backend, error
    
    if remote_error:
        return "", "ocr_space", remote_error
    if easy_error:
        return "", "easyocr", easy_error
    return "", None, error


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


def _extract_text_remote(image: Image.Image) -> tuple[str, str | None, str | None]:
    api_key = os.getenv("OCR_SPACE_API_KEY", "helloworld")
    try:
        with io.BytesIO() as buffer:
            image.save(buffer, format="PNG")
            buffer.seek(0)
            files = {"file": ("receipt.png", buffer, "image/png")}
            data = {"apikey": api_key, "isOverlayRequired": False}
            response = httpx.post(
                "https://api.ocr.space/parse/image",
                data=data,
                files=files,
                timeout=60.0,
            )
            response.raise_for_status()
            result = response.json()
    except Exception as exc:
        return "", "ocr_space", f"ocr_space request failed: {exc}"

    if result.get("IsErroredOnProcessing"):
        error = result.get("ErrorMessage")
        if isinstance(error, list):
            error = "; ".join(str(item) for item in error)
        return "", "ocr_space", error or "ocr_space returned error"

    parsed = result.get("ParsedResults")
    if not parsed:
        return "", "ocr_space", "ocr_space returned no parsed results"

    text = parsed[0].get("ParsedText", "").strip()
    return text, "ocr_space", None


def _extract_text_easyocr(image: Image.Image) -> tuple[str, str | None, str | None]:
    try:
        import easyocr
    except ImportError as exc:
        return "", None, f"easyocr import failed: {exc}"

    try:
        import numpy as np
    except ImportError as exc:
        return "", None, f"numpy import failed: {exc}"

    try:
        reader = easyocr.Reader(["ru", "en"], gpu=False)
        result = reader.readtext(np.array(image))
        text = "\n".join([item[1] for item in result]).strip()
        return text, "easyocr", None
    except Exception as exc:
        return "", None, f"easyocr failed: {exc}"


def _extract_text_pytesseract(image: Image.Image) -> tuple[str, str | None, str | None]:
    try:
        import pytesseract
    except ImportError as exc:
        return "", None, f"pytesseract import failed: {exc}"

    try:
        text = pytesseract.image_to_string(image, lang="rus+eng", config="--psm 6").strip()
        if text:
            return text, "pytesseract", None
        return "", None, "pytesseract returned empty text"
    except Exception as exc:
        return "", None, f"pytesseract failed: {exc}"
