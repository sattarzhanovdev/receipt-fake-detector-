from datetime import date, datetime


RISK_THRESHOLD = 60


def calculate_risk(
    data: dict[str, str | None],
    qr_data: str | None,
    image_risks: list[str],
    extracted_text: str,
) -> dict[str, object]:
    risk_score = 0
    reasons: list[str] = []

    risk_score = _add_missing_field_risks(data, risk_score, reasons)
    risk_score = _add_status_risk(data.get("status"), risk_score, reasons)
    risk_score = _add_date_risk(data.get("date"), risk_score, reasons)
    risk_score = _add_text_quality_risk(extracted_text, risk_score, reasons)
    risk_score = _add_qr_risk(qr_data, data, risk_score, reasons)

    for risk in image_risks:
        risk_score += 15
        reasons.append(risk)

    risk_score = min(risk_score, 100)
    is_fake = risk_score >= RISK_THRESHOLD
    confidence = round(max(0.01, min(0.99, risk_score / 100 if is_fake else 1 - risk_score / 100)), 2)

    if not reasons:
        reasons.append("Критичных признаков подделки не найдено")

    return {
        "is_fake": is_fake,
        "confidence": confidence,
        "risk_score": risk_score,
        "reason": ", ".join(reasons),
    }


def _add_missing_field_risks(data: dict[str, str | None], risk_score: int, reasons: list[str]) -> int:
    required_fields = {
        "amount": ("нет суммы платежа", 25),
        "date": ("нет даты платежа", 20),
        "transaction_id": ("нет номера операции", 25),
        "status": ("нет статуса платежа", 30),
        "currency": ("нет валюты", 10),
    }

    for field, (reason, risk) in required_fields.items():
        if not data.get(field):
            risk_score += risk
            reasons.append(reason)

    return risk_score


def _add_status_risk(status: str | None, risk_score: int, reasons: list[str]) -> int:
    if status and status.lower() != "успешно":
        risk_score += 35
        reasons.append("статус платежа не подтверждает успешную оплату")
    return risk_score


def _add_date_risk(raw_date: str | None, risk_score: int, reasons: list[str]) -> int:
    if not raw_date:
        return risk_score

    parsed_date = _parse_date(raw_date)
    if not parsed_date:
        risk_score += 20
        reasons.append("некорректный формат даты")
    elif parsed_date > date.today():
        risk_score += 35
        reasons.append("дата платежа находится в будущем")

    return risk_score


def _add_text_quality_risk(text: str, risk_score: int, reasons: list[str]) -> int:
    if not text.strip():
        risk_score += 35
        reasons.append("OCR не смог извлечь текст")
        return risk_score

    suspicious_chars = sum(1 for char in text if ord(char) > 1103)
    if suspicious_chars > 5:
        risk_score += 15
        reasons.append("найдены странные символы в тексте")

    return risk_score


def _add_qr_risk(
    qr_data: str | None,
    data: dict[str, str | None],
    risk_score: int,
    reasons: list[str],
) -> int:
    if not qr_data:
        risk_score += 10
        reasons.append("QR-код отсутствует или не считывается")
        return risk_score

    amount = data.get("amount")
    transaction_id = data.get("transaction_id")
    if amount and amount not in qr_data:
        risk_score += 25
        reasons.append("сумма из QR не совпадает с OCR")
    if transaction_id and transaction_id.lower() not in qr_data.lower():
        risk_score += 25
        reasons.append("номер операции из QR не совпадает с OCR")

    return risk_score


def _parse_date(raw_date: str) -> date | None:
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw_date, fmt).date()
        except ValueError:
            continue

    month_numbers = {
        "января": 1,
        "февраля": 2,
        "марта": 3,
        "апреля": 4,
        "мая": 5,
        "июня": 6,
        "июля": 7,
        "августа": 8,
        "сентября": 9,
        "октября": 10,
        "ноября": 11,
        "декабря": 12,
    }
    parts = raw_date.lower().split()
    if len(parts) == 3 and parts[1] in month_numbers:
        try:
            return date(int(parts[2]), month_numbers[parts[1]], int(parts[0]))
        except ValueError:
            return None

    return None
