from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cities" ADD "time" VARCHAR(255);
        ALTER TABLE "tours" ADD "text_erid" VARCHAR(255);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "cities" DROP COLUMN "time";
        ALTER TABLE "tours" DROP COLUMN "text_erid";"""
