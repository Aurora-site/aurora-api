from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cities" ADD "name_cn" VARCHAR(255);
        ALTER TABLE "cities" ADD "name_ru" VARCHAR(255);
        ALTER TABLE "cities" ADD "name_en" VARCHAR(255);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cities" DROP COLUMN "name_cn";
        ALTER TABLE "cities" DROP COLUMN "name_ru";
        ALTER TABLE "cities" DROP COLUMN "name_en";"""
