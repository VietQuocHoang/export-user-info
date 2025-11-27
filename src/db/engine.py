from urllib.parse import quote

from sqlalchemy import URL, Engine, create_engine

from config.settings import get_settings

settings = get_settings()

url_object = URL.create(
    "postgresql+psycopg2",
    username=settings.db_user,
    password=quote(settings.db_password),
    host=settings.db_host,
    database=settings.db_name,
)


def get_engine() -> Engine:
    return create_engine(url=url_object)
