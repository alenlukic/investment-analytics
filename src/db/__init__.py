from SQLAlchemyDB import Database

from src.definitions.config import DB_CONFIG


database = Database(DB_CONFIG)
metadata = database.get_metadata()

Base = database.get_base()
