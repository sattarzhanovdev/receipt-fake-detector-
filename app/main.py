from flask import Flask

from app.api.receipts import receipts_bp

app = Flask(__name__)
app.register_blueprint(receipts_bp, url_prefix="/api")


@app.route("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
