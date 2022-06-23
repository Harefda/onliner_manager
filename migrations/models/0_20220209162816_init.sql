-- upgrade --
CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password" VARCHAR(255) NOT NULL,
    "client_id" VARCHAR(255),
    "client_secret" VARCHAR(255),
    "setup_complete" BOOL   DEFAULT False
);
CREATE TABLE IF NOT EXISTS "onlinerproduct" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "product_id" BIGINT NOT NULL,
    "category" VARCHAR(256) NOT NULL,
    "vendor" VARCHAR(256) NOT NULL,
    "model" VARCHAR(256) NOT NULL,
    "article" VARCHAR(256),
    "price" VARCHAR(10) NOT NULL,
    "stockStatus" VARCHAR(30),
    "termHalva" VARCHAR(10) NOT NULL,
    "priceHalva" VARCHAR(128) NOT NULL,
    "hasOnlinerPrime" VARCHAR(10) NOT NULL,
    "courierDeliveryPrices" VARCHAR(256) NOT NULL,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "productoptions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "currency" VARCHAR(3),
    "price_in_currency" DECIMAL(11,4),
    "in_stock" BOOL,
    "onliner_product_id" INT NOT NULL UNIQUE REFERENCES "onlinerproduct" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "useroptions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "old_eur_rate" DOUBLE PRECISION NOT NULL,
    "old_usd_rate" DOUBLE PRECISION NOT NULL,
    "vendors_eur" VARCHAR(500),
    "vendors_usd" VARCHAR(500),
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
