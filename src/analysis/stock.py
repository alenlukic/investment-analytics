from src.utils.data_utils import deep_get
from src.utils.math_utils import is_close_to_zero, MAX_VALUE


class Stock:
    """ Contains stock data and methods for calculating stock metrics. """

    def __init__(self, symbol, stock_data):
        """ Stock class constructor.

        :param symbol: stock's ticker symbol.
        :param stock_data: dictionary containing stock data/metrics.
        """

        self.symbol = symbol
        self.stock_data = stock_data

    def get_company_name(self):
        """ :returns: Company's name. """
        return deep_get(self.stock_data, ['ADVANCED_STATS', 'companyName'], '(N/A)')

    def get_symbol(self):
        """ :returns: Company's ticker symbol. """
        return self.symbol

    # Metric calculation functions below.

    def dividend_yield(self):
        """ :returns: Dividend yield. """
        return deep_get(self.stock_data, ['ADVANCED_STATS', 'dividendYield'])

    def ebdita(self):
        """ :returns: EBIDTA (earnings before interest, tax, depreciation & amoritzation)."""
        return deep_get(self.stock_data, ['ADVANCED_STATS', 'EBITDA'])

    def enterprise_value(self):
        """ :returns Enterprise value. """
        return deep_get(self.stock_data, ['ADVANCED_STATS', 'enterpriseValue'])

    def price(self):
        """ :returns: Stock price. """
        return self.stock_data['PRICE']

    def price_to_book_ratio(self):
        """ :returns: P/B ratio. """
        return deep_get(self.stock_data, ['ADVANCED_STATS', 'priceToBook'])

    def price_to_earnings_ratio(self):
        """ :returns: P/E ratio. """
        return deep_get(self.stock_data, ['ADVANCED_STATS', 'peRatio'])

    def price_to_sales_ratio(self):
        """ :returns: P/S ratio. """
        return deep_get(self.stock_data, ['ADVANCED_STATS', 'priceToSales'])

    def six_month_percent_delta(self):
        """ :returns: Six month % change in price. """
        return deep_get(self.stock_data, ['ADVANCED_STATS', 'month6ChangePercent'])

    def cash_flow(self):
        """ :returns: Company cash flow. """

        cash_flow_array = deep_get(self.stock_data, ['CASH_FLOW', 'cashflow'])
        if cash_flow_array is None or len(cash_flow_array) == 0:
            return None

        return cash_flow_array[0].get('cashFlow', None)

    def earnings_yield(self):
        """ :returns: Earnings yield (EBIDTA / EV). """

        ebidta = self.ebdita()
        if ebidta is None:
            return None

        ev = self.enterprise_value()
        if ev is None or ev <= 0:
            ev = 1

        return ebidta / float(ev)

    def price_to_cash_flow_ratio(self):
        """ :returns: P/CF ratio. """

        price = self.price()
        if price is None:
            return None

        cash_flow = self.cash_flow()
        if cash_flow is None or is_close_to_zero(cash_flow):
            return None

        return price / float(cash_flow)


class RankedStock(Stock):
    """ Represents a stock ranked by some investment strategy. """

    def __init__(self, symbol, stock_data):
        """ Constructor. Initializes the rank. """

        Stock.__init__(self, symbol, stock_data)
        self.rank_factors = {}
        self.comparison_metrics = {}
        self.comparison_value = MAX_VALUE

    def get_rank_factors(self):
        """ :returns: dictionary of rank factors. """
        return self.rank_factors

    def set_comparison_metrics(self, comparison_metrics):
        """ Set the dictionary of comparison metrics (and also set the rank as the sum of these factors).

        :param comparison_metrics: dictionary mapping metric name to value.
        """

        self.comparison_metrics = comparison_metrics
        self.set_comparison_value(sum(comparison_metrics.values()))

    def set_comparison_value(self, comparison_value):
        """ Set comparison value.

        :param comparison_value: comparison value to set.
        """
        self.comparison_value = comparison_value

    def set_rank_factors(self, rank_factors):
        """ Set the dictionary of rank factors.

        :param rank_factors: dictionary mapping rank factor name to value.
        """

        self.rank_factors = rank_factors

    def update_rank_factors(self, rank_factors_update):
        """ Update dictionary of rank factors.

        :param rank_factors_update: dictionary of additional rank factors.
        """

        self.rank_factors.update(rank_factors_update)

    def __eq__(self, other):
        return self.comparison_value == other.comparison_value

    def __lt__(self, other):
        return self.comparison_value < other.comparison_value
