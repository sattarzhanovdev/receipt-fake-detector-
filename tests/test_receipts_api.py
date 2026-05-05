from io import BytesIO

from PIL import Image

from app.main import app
from app.services import ocr_service, qr_service


client = app.test_client()


def _png_bytes() -> bytes:
    image = Image.new("RGB", (800, 600), color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_check_receipt_returns_low_risk_for_complete_receipt(monkeypatch):
    monkeypatch.setattr(
        ocr_service,
        "extract_text",
        lambda image: """
        MBank
        Статус: Успешно
        Сумма: 1200 KGS
        Дата: 05.05.2026
        Время: 14:32
        Номер операции: A92839102
        """,
    )
    monkeypatch.setattr(qr_service, "extract_qr_payload", lambda image: "A92839102 1200 KGS")

    response = client.post(
        "/api/receipts/check/",
        data={"image": (BytesIO(_png_bytes()), "receipt.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["is_fake"] is False
    assert payload["risk_score"] < 60
    assert payload["extracted_data"]["amount"] == "1200"
    assert payload["extracted_data"]["transaction_id"] == "A92839102"


def test_check_receipt_returns_high_risk_when_ocr_fails(monkeypatch):
    monkeypatch.setattr(ocr_service, "extract_text", lambda image: "")
    monkeypatch.setattr(qr_service, "extract_qr_payload", lambda image: None)

    response = client.post(
        "/api/receipts/check/",
        data={"image": (BytesIO(_png_bytes()), "receipt.png")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["is_fake"] is True
    assert payload["risk_score"] >= 60
    assert "OCR не смог извлечь текст" in payload["reason"]


def test_check_receipt_rejects_non_image_upload():
    response = client.post(
        "/api/receipts/check/",
        data={"image": (BytesIO(b"not image"), "receipt.txt")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
