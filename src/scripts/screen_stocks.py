from collections import defaultdict
import json
from os.path import join

from src.definitions.config import PROCESSED_DATA_DIR
from src.definitions.stats import KeyStat
from src.utils.file_utils import save_json


def screen_stocks(stock_data_file):
    with open(stock_data_file, 'r') as f:
        stock_data = json.load(f)
        stat_tuples = list(filter(lambda t: t[1]['KEY_STATS'].get(KeyStat.MARKET_CAP.value, 0) > 300000000,
                                  [(k, v) for k, v in stock_data.items()]))

        stock_ranks = defaultdict(lambda: defaultdict(int))
        for ks in KeyStat:
            if ks == KeyStat.MARKET_CAP:
                continue

            sorted_st = sorted(stat_tuples, key=lambda t: t[1]['KEY_STATS'].get(ks.value, 0),
                               reverse=ks != KeyStat.PE_RATIO)

            for i, st in enumerate(sorted_st):
                symbol = st[0]
                stock_ranks[symbol][ks.value] = i
                stock_ranks[symbol]['Overall Rank'] = 0
                stock_ranks[symbol]['Overall Rank'] = int(sum(stock_ranks[symbol].values()) / float(
                    len(stock_ranks[symbol]) - 1))

        save_json(PROCESSED_DATA_DIR, 'stock_screen_rankings.json', stock_ranks, True)

        ranked_stocks = sorted([(k, v) for k, v in stock_ranks.items()], key=lambda t:
                               float(t[1]['Overall Rank']) / float(len(t[1].values()) - 1))
        output = ['\t\t\t\t'.join(['Rank', 'Symbol', 'Dividend Yield', '6-Month Price Growth', 'P /E Ratio', 'TTM EPS'])]
        for rs in ranked_stocks:
            symbol = rs[0]
            ranks = rs[1]
            row = '\t\t\t\t'.join([str(ranks['Overall Rank']), symbol] +
                                  [str(ranks[x.value]) for x in [KeyStat.DIVIDEND_YIELD, KeyStat.MONTH_6_CHANGE_PERCENT,
                                                                 KeyStat.PE_RATIO, KeyStat.TTM_EPS]])
            output.append(row)

        print('\n'.join(output))


if __name__ == '__main__':
    screen_stocks(join(PROCESSED_DATA_DIR, '20210201_partials_stock_data.json'))











