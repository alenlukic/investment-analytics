import json
from os.path import join

from src.db import database
from src.db.entities.stock import StockData
from src.definitions.config import PROCESSED_DATA_DIR
from src.utils.data_utils import compact_object, deep_get


def migrate_stock_data():
    mj_file = join(PROCESSED_DATA_DIR, 'stock_data_master.json')
    ks_file = join(PROCESSED_DATA_DIR, '20210201_partials_stock_data.json')

    with open(mj_file, 'r') as mjf, open(ks_file, 'r') as ksf:
        master_json = json.load(mjf)
        ks_json = json.load(ksf)
        symbols = set(master_json.keys()).union(set(ks_json.keys()))

        session = database.create_session()
        existing_rows = set([r.symbol for r in session.query(StockData).all()])
        for symbol in symbols:
            if symbol in existing_rows:
                continue

            price = deep_get(master_json, [symbol, 'PRICE'])
            key_stats = deep_get(ks_json, [symbol, 'KEY_STATS'])
            advanced_stats = deep_get(master_json, [symbol, 'ADVANCED_STATS'])
            cash_flow = deep_get(master_json, [symbol, 'CASH_FLOW', 'cashflow'], [])

            row = compact_object(
                {
                    'symbol': symbol,
                    'price': price,
                    'key_stats': key_stats,
                    'advanced_stats': advanced_stats,
                    'cash_flow': None if len(cash_flow) == 0 else cash_flow[0]

                }
            )
            session.guarded_add(StockData(**row))
            session = database.recreate_session_contingent(session)


if __name__ == '__main__':
    migrate_stock_data()
