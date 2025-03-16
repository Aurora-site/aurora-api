from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "banners" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(255) NOT NULL  DEFAULT '',
    "url" VARCHAR(2000) NOT NULL
);
CREATE TABLE IF NOT EXISTS "cities" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "name_ru" VARCHAR(255),
    "name_en" VARCHAR(255),
    "name_cn" VARCHAR(255),
    "lat" REAL NOT NULL,
    "long" REAL NOT NULL,
    "time" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "customers" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "current_geo_lat" REAL,
    "current_geo_long" REAL,
    "selected_geo_lat" REAL,
    "selected_geo_long" REAL,
    "locale" VARCHAR(2) NOT NULL  DEFAULT 'ru',
    "token" VARCHAR(255) NOT NULL,
    "hobo" INT NOT NULL  DEFAULT 0,
    "hobo_at" TIMESTAMP,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "city_id" INT NOT NULL REFERENCES "cities" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "subscriptions" (
    "id" CHAR(36) NOT NULL  PRIMARY KEY,
    "email" VARCHAR(255),
    "cust_name" VARCHAR(255),
    "cust_surname" VARCHAR(255),
    "cust_patronymic" VARCHAR(255),
    "alert_probability" INT NOT NULL,
    "sub_type" INT NOT NULL,
    "geo_push_type" VARCHAR(255) NOT NULL,
    "active" INT NOT NULL  DEFAULT 0,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "cust_id" INT NOT NULL REFERENCES "customers" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "tours" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(2000) NOT NULL,
    "text_mini" VARCHAR(2000) NOT NULL,
    "text" TEXT NOT NULL,
    "text_head" VARCHAR(2000) NOT NULL,
    "text_erid" VARCHAR(255),
    "price" REAL NOT NULL,
    "url" VARCHAR(2000) NOT NULL,
    "image" VARCHAR(2000) NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
