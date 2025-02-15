from functools import partial

from tortoise.contrib.fastapi import RegisterTortoise

from internal.settings import DB_URL

ORM_MODELS = ["internal.db.models", "aerich.models"]

register_orm = partial(
    RegisterTortoise,
    db_url=DB_URL,
    modules={"models": ORM_MODELS},
    generate_schemas=True,
    add_exception_handlers=True,
)

TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ORM_MODELS,
            "default_connection": "default",
        },
    },
}
