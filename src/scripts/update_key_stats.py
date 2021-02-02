from src.api.stock_data_api import IEXCloudAPI
from src.definitions.routes import IEXStockDataEndpoint
from src.utils.file_utils import load_stock_symbols


def update_key_stats(is_prod):
    api = IEXCloudAPI(is_prod)
    all_symbols = load_stock_symbols()

    api.update_stock_data(all_symbols, [IEXStockDataEndpoint.KEY_STATS.name])


if __name__ == '__main__':
    update_key_stats(True)
