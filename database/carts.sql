CREATE TABLE carts (
    id UInt32,
    user_id UInt32,
    product_id UInt32,
    quantity UInt32,
    date DateTime
) ENGINE = MergeTree
ORDER BY (id, user_id, product_id);