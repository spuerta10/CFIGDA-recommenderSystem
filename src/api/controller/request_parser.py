"""
Module for parsing and validating incoming JSON requests for item recommendations.
"""

from typing import Optional

from pydantic import BaseModel


class RequestParser(BaseModel):
    """
    Parses and validates the input data for item recommendation requests.

    Attributes:
        customer_id (int): Unique identifier for the customer requesting recommendations.
        order_items (list): List of items associated with the customer's order.
        num_recommendations (Optional[int]): Desired number of recommendations, defaults to 3.
    """

    customer_id: int
    order_items: list
    num_recommendations: Optional[int] = 3
