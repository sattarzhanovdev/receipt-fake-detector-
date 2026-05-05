from PIL import Image


def extract_qr_payload(image: Image.Image) -> str | None:
    try:
        from pyzbar.pyzbar import decode
    except ImportError:
        return None

    try:
        decoded = decode(image)
    except Exception:
        return None

    if not decoded:
        return None

    return decoded[0].data.decode("utf-8", errors="replace")
