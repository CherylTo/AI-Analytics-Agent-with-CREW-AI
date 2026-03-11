CREATE
OR REPLACE VIEW analytics_orders AS (
    SELECT
        -- orders
        o.order_id,
        o.order_purchase_timestamp,
        DATE_TRUNC(
            'month',
            o.order_purchase_timestamp
        ) AS purchase_month,
        o.order_status,
        -- customers
        C.customer_id,
        C.customer_state,
        -- order items
        oi.product_id,
        p.product_category_name_english,
        -- seller
        oi.seller_id,
        -- price
        oi.price,
        oi.freight_value,
        (
            oi.price + oi.freight_value
        ) AS order_item_value,
        -- payment
        pay.payment_type,
        pay.payment_value,
        -- reviews
        r.review_score,
        -- delivery
        DATEDIFF(
            'day',
            o.order_purchase_timestamp,
            o.order_delivered_customer_date
        ) AS delivery_days
    FROM
        orders o
        JOIN order_items oi
        ON o.order_id = oi.order_id
        JOIN customers C
        ON o.customer_id = C.customer_id
        JOIN product_english p
        ON oi.product_id = p.product_id
        LEFT JOIN order_payments pay
        ON o.order_id = pay.order_id
        LEFT JOIN order_reviews r
        ON o.order_id = r.order_id
);
