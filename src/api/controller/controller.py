"""
API module providing an endpoint for item recommendations based on customer 
purchase history. Uses KNN modeling to analyze and suggest items for users.
"""

from flask import Blueprint, Response, request, jsonify
from flask_wtf.csrf import generate_csrf

from api.knn_model import KNNModel
from api.controller.request_parser import RequestParser


controller_bp = Blueprint("controller", __name__)
knn_model = KNNModel(r"src/api/conf/knn_model_conf.json")


@controller_bp.route("/get-csrf-token", methods=["GET"])
def get_csrf_token():
    """
    Generates a CSRF token and returns it as part of a JSON response.

    Returns:
        Response: A Flask response containing the CSRF token in JSON format.
        The CSRF token is also set as a cookie in the response.
    """
    csrf_token = generate_csrf()
    response = jsonify({"csrf_token": csrf_token})
    response.set_cookie("csrf_token", csrf_token, httponly=True, secure=True, samesite="Lax")
    return response


@controller_bp.route("/items/recommend", methods=["POST"])
def recommend_items() -> Response:
    """Endpoint to recommend items for a specific customer based on their purchase history.

    Raises:
        ValueError: If the JSON request is empty or missing required fields.

    Returns:
        Response: JSON response containing recommended items 
        or an error message if an exception occurs.
    """
    try:
        json_request = request.get_json(silent=True)
        if json_request is None:
            raise ValueError("The given request is empty!")
        RequestParser(**json_request)
        recommended_items: list[int] = knn_model.recommend(
            customer_id=json_request["customer_id"],
            order_items=json_request["order_items"],
            num_recommendations=(
                json_request["num_recommendations"]
                if json_request.get("num_recommendations")
                else 3
            ),
        )
        return jsonify({"recommended_items": recommended_items})
    except Exception as e:
        return jsonify({"Exception": str(e)}), 400
