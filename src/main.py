import sys

import uvicorn

from config.app import app
from config.settings import get_settings
from db.engine import get_engine
from seed import seed

accepted_command = ["seed"]

def parse_command(*args, **kwargs):
    if len(args) <= 1:
        return False
    else:
        command = args[1]
        if command not in accepted_command:
            raise Exception(
                f"Command does not exists, accepted command are {','.join(accepted_command)}"
            )
        else:
            seed(engine=get_engine())
        return True

if __name__ == "__main__":
    settings = get_settings()
    flag = parse_command(*sys.argv)
    if not flag:
        uvicorn.run("main:app", host=settings.app_host, port=settings.app_port, reload=settings.debug)
