from app.services.parser_service import parse_receipt_text


def test_parse_amount_with_thousands_space():
    data = parse_receipt_text("Итого 1 000,00 с")

    assert data["amount"] == "1000.00"
    assert data["currency"] == "KGS"


def test_parse_amount_with_thousands_comma_and_kgs():
    data = parse_receipt_text("Сумма 1,000.00 KGS")

    assert data["amount"] == "1000.00"
    assert data["currency"] == "KGS"
