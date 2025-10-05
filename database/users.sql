CREATE TABLE users (
    id Int64,
    email String,
    username String,
    password String,
    name String,
    phone String,
    city String,
    street String,
    number Int32,
    zipcode String
) ENGINE = MergeTree
ORDER BY id;