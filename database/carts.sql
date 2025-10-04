CREATE TABLE carts (
    id Int64,
    user_id Int64,
    product_id Int64,
    quantity Int64,
    date DateTime
) ENGINE = MergeTree
ORDER BY (id, user_id, product_id);