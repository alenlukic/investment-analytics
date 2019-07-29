# Reading:
#
# https://www.moneycrashers.com/types-stock-market-investment-strategies/
# https://www.investopedia.com/investing/investing-strategies/
# https://www.quantopian.com/lectures
# https://www.wallstreetoasis.com/forums/on-the-job-with-simple-as%E2%80%A6-my-research-process


# Data sources:


# Historical price data (content type: CSV)
# http://markets.financialcontent.com/stocks/action/gethistoricaldata?Month={MONTH_NUMBER}&Year={YEAR_NUMBER}&Symbol=NQ%3A{SYMBOL}&Range={NUM_MONTHS}
# CSV columns (skip 1st row): symbol, date, open, high, low, close, volume, # stocks exchanged, % change

# Detailed quote (content type: HTML)
# http://markets.financialcontent.com/stocks/quote/detailedquote?Symbol={SYMBOL}
# Rekevant HTML elements: row_price, row_eps, row_pe, row_dividendyield, row_sharesoutstanding, row_volume
