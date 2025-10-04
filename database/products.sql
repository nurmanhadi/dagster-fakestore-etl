CREATE TABLE products (
    id Int64,
    title String,
    price_usd Float64,
    description String,
    category String,
    image String,
    rate Float64,
    count UInt32,
    price_idr Float64
) ENGINE = MergeTree
ORDER BY id;