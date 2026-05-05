from PIL import Image

from app.services import fraud_service, image_analysis_service, ocr_service, parser_service, qr_service


def analyze_receipt(image: Image.Image) -> dict:
    ocr_result = ocr_service.extract_text(image)
    text = ""
    ocr_backend = None
    ocr_error = None

    if isinstance(ocr_result, tuple):
        if len(ocr_result) == 3:
            text, ocr_backend, ocr_error = ocr_result
        elif len(ocr_result) == 2:
            text, ocr_backend = ocr_result
    else:
        text = ocr_result

    data = parser_service.parse_receipt_text(text)
    qr_data = qr_service.extract_qr_payload(image)
    image_risks = image_analysis_service.detect_tampering(image)

    result = fraud_service.calculate_risk(
        data=data,
        qr_data=qr_data,
        image_risks=image_risks,
        extracted_text=text,
    )

    return {
        "is_fake": result["is_fake"],
        "confidence": result["confidence"],
        "risk_score": result["risk_score"],
        "reason": result["reason"],
        "ocr_text": text,
        "ocr_backend": ocr_backend,
        "ocr_error": ocr_error,
        "qr_payload": qr_data,
        "extracted_data": data,
    }

    return {
        "is_fake": result["is_fake"],
        "confidence": result["confidence"],
        "risk_score": result["risk_score"],
        "reason": result["reason"],
        "ocr_text": text,
        "ocr_backend": ocr_backend,
        "qr_payload": qr_data,
        "extracted_data": data,
    }
