CREATE TABLE products (
    id UInt32,
    title String,
    price_usd Float64,
    description String,
    category String,
    image String,
    rate Float32,
    count UInt32
) ENGINE = MergeTree
ORDER BY id;