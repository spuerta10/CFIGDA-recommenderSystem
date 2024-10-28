from typing import Optional

from pydantic import BaseModel


class RequestParser(BaseModel):
    customer_id: int
    order_items: list
    num_recommendations: Optional[int] = 3