CREATE TABLE users (
    id INT,
    email String,
    username String,
    password String,
    name String,
    phone INT,
    city String,
    street String,
    number INT,
    zipcode String
) ENGINE = MergeTree
ORDER BY id;