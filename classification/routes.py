"""API Flask untuk Load Classification (Random Forest)."""
from flask import Blueprint, jsonify, request

from . import service

bp = Blueprint("classification_api", __name__, url_prefix="/api/classification")


@bp.get("/status")
def status():
    return jsonify(service.status())


@bp.post("/reload")
def reload_model():
    service.load_model(force=True)
    return jsonify(service.status())


@bp.post("/predict")
def predict():
    body = request.get_json(silent=True) or {}
    try:
        row = service.parse_features(body)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    try:
        return jsonify(service.predict(row))
    except service.ModelUnavailable as exc:
        return jsonify(error=str(exc)), 503
