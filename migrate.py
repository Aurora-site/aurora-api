import asyncio
import sys

from aerich import Command  # type: ignore
from tortoise import Tortoise

from internal.db.config import TORTOISE_ORM


async def main():

    args = dict(enumerate(sys.argv))
    try:
        command = Command(tortoise_config=TORTOISE_ORM)
        await command.init()
        if args.get(1) == "upgrade":
            res = await command.upgrade()
            if res:
                for version_file in res:
                    print(f"Success upgrading to {version_file}")
            else:
                print("No upgrade items found")
        elif args.get(1) == "migrate":
            res = await command.migrate(args.get(2, "update"))
            if res:
                print(f"Success creating migration file {res}")
            else:
                print("No changes detected")
        else:
            print("Unknown command")
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
