CREATE
OR REPLACE VIEW product_english AS (
    SELECT
        product_id,
        product_category_name_english,
        product_name_lenght product_name_length,
        product_description_lenght product_description_length,
        product_photos_qty,
        product_weight_g,
        product_length_cm,
        product_height_cm,
        product_width_cm
    FROM
        products A
        LEFT JOIN product_category_name_translation A USING (product_category_name)
);
