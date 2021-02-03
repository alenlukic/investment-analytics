from sqlalchemy import Column, Integer, Sequence

from src.db import Base, metadata


class StockData(Base):
    """
    Represents stock table in the DB. Postgres schema:

                               Table "public.stock_data"
         Column     |            Type             | Collation | Nullable | Default
    ----------------+-----------------------------+-----------+----------+---------
     id             | integer                     |           | not null |
     symbol         | character varying           |           | not null |
     key_stats      | json                        |           |          |
     advanced_stats | json                        |           |          |
     cash_flow      | json                        |           |          |
     timestamp      | timestamp without time zone |           |          | now()
     price          | numeric(15,2)               |           |          |
    Indexes:
        "ix_stock_data_id" UNIQUE, btree (id)
    """

    __tablename__ = 'stock_data'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, Sequence('stock_data_seq', metadata=metadata), index=True, unique=True)

    def __eq__(self, other):
        return self.id == other.id and self.__class__.__name__ == other.__class__.__name__

    def __hash__(self):
        return hash(self.__class__.__name__ + str(self.id))
