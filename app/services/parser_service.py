import re


SUCCESS_STATUSES = (
    "успешно",
    "оплачено",
    "выполнен",
    "выполнено",
    "платеж выполнен",
    "платёж выполнен",
    "success",
    "successful",
    "completed",
    "paid",
)
KNOWN_BANKS = ("mbank", "optima", "bakai", "demir", "kicb", "kompanion", "elsom", "odengi")


def parse_receipt_text(text: str) -> dict[str, str | None]:
    normalized = _normalize_text(text)

    return {
        "amount": _find_amount(normalized),
        "currency": _find_currency(normalized),
        "date": _find_date(normalized),
        "time": _find_time(normalized),
        "recipient": _find_labeled_value(normalized, ("получатель", "recipient", "кому")),
        "sender": _find_labeled_value(normalized, ("отправитель", "sender", "от кого")),
        "transaction_id": _find_transaction_id(normalized),
        "status": _find_status(normalized),
        "bank": _find_bank(normalized),
    }


def _normalize_text(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text or "").strip()


def _find_amount(text: str) -> str | None:
    patterns = (
        r"(?:сумма|amount|итого|total)\D{0,24}(\d[\d\s.,]*(?:[.,]\d{1,2})?)",
        r"(\d[\d\s.,]*(?:[.,]\d{1,2})?)\s*(?:kgs|сом|с|€|k\u0111|usd|eur)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return _normalize_amount(match.group(1))
    return None


def _normalize_amount(raw_amount: str) -> str:
    amount = raw_amount.replace(" ", "")
    if "," in amount and "." in amount:
        if amount.rfind(".") > amount.rfind(","):
            amount = amount.replace(",", "")
        else:
            amount = amount.replace(".", "").replace(",", ".")
    else:
        amount = amount.replace(",", ".")
    return amount


def _find_currency(text: str) -> str | None:
    match = re.search(r"\b(KGS|USD|EUR|RUB)\b|(?:сом|с\b|€)", text, re.IGNORECASE)
    if not match:
        return None
    value = match.group(0).lower()
    if value in {"сом", "с", "€"}:
        return "KGS"
    return value.upper()


def _find_date(text: str) -> str | None:
    match = re.search(
        r"\b(\d{4}-\d{2}-\d{2}|\d{2}[./-]\d{2}[./-]\d{4}|\d{1,2}\s+[а-яё]+\s+\d{4})\b",
        text,
        re.IGNORECASE,
    )
    return match.group(1) if match else None


def _find_time(text: str) -> str | None:
    match = re.search(r"\b([01]?\d|2[0-3]):[0-5]\d(?::[0-5]\d)?\b", text)
    return match.group(0) if match else None


def _find_labeled_value(text: str, labels: tuple[str, ...]) -> str | None:
    labels_pattern = "|".join(re.escape(label) for label in labels)
    match = re.search(rf"(?:{labels_pattern})\s*:?\s*(.+)", text, re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).splitlines()[0].strip()
    return value[:120] or None


def _find_transaction_id(text: str) -> str | None:
    patterns = (
        r"(?:номер операции|операция|квитанция|transaction id|txn|id)\s*:?\s*([A-ZА-Я0-9/-]{6,})",
        r"\b([A-Z]{1,6}\d{6,}(?:/\d{6,})?)\b",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def _find_status(text: str) -> str | None:
    lowered = text.lower()
    for status in SUCCESS_STATUSES:
        if status in lowered:
            return "Успешно"
    failed = ("отклонено", "ошибка", "failed", "declined", "cancelled", "canceled")
    for status in failed:
        if status in lowered:
            return status
    return None


def _find_bank(text: str) -> str | None:
    lowered = text.lower()
    for bank in KNOWN_BANKS:
        if bank in lowered:
            return bank.upper() if bank == "kicb" else bank.title()
    return None
