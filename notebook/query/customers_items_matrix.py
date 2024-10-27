"""
This query finds the customer_item_matrix to train the KNN ML model.
It's intended for being executed in BigQuery platform.
"""

QUERY = """

    WITH exploded_orders AS (
        SELECT
            o.customer_id,
            i.item_id
        FROM `ing-datos-avanzado.main_data.orders` AS o,
        UNNEST(o.order_items) AS i
    ),

    all_combinations AS (
        SELECT
            c.customer_id,
            i.item_id
        FROM
            (SELECT customer_id FROM `ing-datos-avanzado.main_data.customer`) AS c
        CROSS JOIN
            (SELECT item_id FROM `ing-datos-avanzado.main_data.item`) AS i
    ),

    customer_product_interactions AS (
        SELECT
            ac.customer_id,
            ac.item_id,
        CASE
            WHEN eo.item_id IS NOT NULL THEN 1
            ELSE 0
        END AS interaction
        FROM
            all_combinations AS ac
        LEFT JOIN
            exploded_orders AS eo
        ON
            ac.customer_id = eo.customer_id
            AND ac.item_id = eo.item_id
    )

    SELECT
        customer_id,
        item_id,
        COUNT(interaction) AS interaction
    FROM
        customer_product_interactions
    GROUP BY
        customer_id,
        item_id

"""