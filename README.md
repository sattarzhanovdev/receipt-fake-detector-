# AI Receipt Fraud Detection API

MVP-сервис на Flask, который принимает изображение чека, извлекает данные через OCR-адаптер, применяет антифрод-правила и возвращает риск подделки.

## Запуск

```bash
cd receipt_ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.main
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=8000
```

API будет доступен по адресу:

```text
http://127.0.0.1:8000
```

## Endpoint

```http
POST /api/receipts/check/
Content-Type: multipart/form-data
```

Поле:

```text
image: file
```

Пример ответа:

```json
{
  "is_fake": true,
  "confidence": 0.85,
  "risk_score": 85,
  "reason": "нет номера операции, QR-код отсутствует или не считывается",
  "extracted_data": {
    "amount": "1200",
    "currency": "KGS",
    "date": "2026-05-05",
    "time": "14:32",
    "recipient": null,
    "sender": null,
    "transaction_id": null,
    "status": "Успешно",
    "bank": "Mbank"
  }
}
```

## Тесты

```bash
pytest
```

## Развёртывание на PythonAnywhere

1. Залейте проект на GitHub или загрузите файлы через вкладку `Files`.
2. В PythonAnywhere откройте консоль и клонируйте/перейдите в папку проекта:

```bash
cd ~/your-project-folder/receipt_ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. В разделе `Web` укажите путь к файлу WSGI и модуль приложения:

- `Working directory`: `/home/yourusername/your-project-folder/receipt_ai`
- `WSGI configuration file`: оставьте стандартный, отредактируйте его

В файле WSGI замените содержимое на:

```python
import sys
import os

project_home = '/home/yourusername/your-project-folder/receipt_ai'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from wsgi import application
```

4. Перезагрузите веб-приложение.

> Путь к приложению на PythonAnywhere — `app.main:app` или `wsgi:application`.

## Примечания

`pytesseract` и `pyzbar` подключены как optional-интеграции. Если они не установлены, сервис всё равно работает, но OCR/QR вернут пустой результат и risk score будет выше.
