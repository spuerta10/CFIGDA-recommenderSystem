"""
This query fetches the n most sell products for given customers.
It's intended for being executed in BigQuery platform.
"""

QUERY = """
  SELECT 
    item_id,
    COUNT(item_id) AS total_purchases
  FROM 
    `ing-datos-avanzado.main_data.orders` AS orders,
  UNNEST(orders.order_items) AS items
  WHERE
    orders.customer_id IN {}  -- similar customers ids
    AND items.item_id NOT IN {}  -- excluded items, already in purchase order
  GROUP BY
    items.item_id,
    orders.customer_id
  ORDER BY
    total_purchases DESC
  LIMIT
    {}  -- wanted number of recomendations
"""