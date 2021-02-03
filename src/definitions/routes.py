from enum import Enum


class FinancialContentEndpoint(Enum):
    DETAILED_QUOTE = 'quote/detailedquote'
    HISTORICAL_DATA = 'action/gethistoricaldata'


class IEXStockDataEndpoint(Enum):
    ADVANCED_STATS = 'stock/%s/advanced-stats'
    CASH_FLOW = 'stock/%s/cash-flow'
    KEY_STATS = 'stock/%s/stats'
    PRICE = 'stock/%s/price'


class IEXRefDataEndpoint(Enum):
    SYMBOLS = 'ref-data/symbols'
