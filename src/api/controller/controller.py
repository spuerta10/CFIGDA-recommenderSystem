from api.knn_model import KNNModel
from api.controller.request_parser import RequestParser

from flask import (
    Blueprint,
    Response,
    request,
    jsonify
)


controller_bp = Blueprint("controller", __name__)
knn_model = KNNModel(r"src/api/conf/knn_model_conf.json")

@controller_bp.route("/items/recommend", methods=["POST"])
def recommend_items() -> Response:
    """Endpoint to recommend items for a specific customer based on their purchase history.

    Raises:
        ValueError: If the JSON request is empty or missing required fields.

    Returns:
        Response: JSON response containing recommended items or an error message if an exception occurs.
    """
    try:
        json_request = request.get_json(silent=True)
        if json_request is None: 
            raise ValueError("The given request is empty!")
        RequestParser(**json_request)
        recommended_items: list[int] = knn_model.recommend(
            customer_id= json_request["customer_id"],
            order_items= json_request["order_items"],
            num_recommendations= json_request["num_recommendations"] \
                if json_request.get("num_recommendations") else 3
        )
        return jsonify({"recommended_items": recommended_items})
    except Exception as e:
        return jsonify({"Exception": str(e)}), 400