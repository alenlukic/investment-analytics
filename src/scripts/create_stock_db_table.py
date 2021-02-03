from sqlalchemy import Integer, JSON, String
from SQLAlchemyDB import DBColumn, Table as DBTable

from src.db import metadata


def create_table():
    json_columns = ['price', 'key_stats', 'advanced_stats', 'cash_flow']
    table = 'stock_data'

    columns = [
        DBColumn('id', Integer).as_index().as_primary_key().as_unique().create(metadata, table),
        DBColumn('symbol', String).as_index().as_primary_key().as_unique().create(
            metadata, table)
    ]
    columns.extend([DBColumn(jc, JSON).as_nullable().create(metadata, table) for jc in json_columns])

    DBTable(table, metadata, columns)
    metadata.create_all()


if __name__ == '__main__':
    create_table()
