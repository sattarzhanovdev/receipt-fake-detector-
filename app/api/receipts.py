from flask import Blueprint, jsonify, request

from app.services.receipt_analyzer import analyze_receipt
from app.utils.image_utils import read_image_upload


receipts_bp = Blueprint("receipts", __name__)


@receipts_bp.route("/receipts/check/", methods=["POST"])
def check_receipt():
    image = request.files.get("image")
    if image is None:
        return jsonify({"detail": "File must be an image"}), 400

    if not image.mimetype or not image.mimetype.startswith("image/"):
        return jsonify({"detail": "File must be an image"}), 400

    image_bytes = image.read()
    if not image_bytes:
        return jsonify({"detail": "Image file is empty"}), 400

    try:
        pil_image = read_image_upload(image_bytes)
    except ValueError as exc:
        return jsonify({"detail": str(exc)}), 400

    result = analyze_receipt(pil_image)
    return jsonify(result)
