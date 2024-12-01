import logging

from connectors.binance_futures import BinanceFuturesClient
from connectors.bitmex import BitmexClient

from interface.root_component import Root

# import csv


logger = logging.getLogger()

logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)


# def save_candles_to_csv(candles, filename):
#     """Save the list of candles to a CSV file."""
#     keys = candles[0].__dict__.keys() if candles else []
#
#     with open(filename, 'w', newline='') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=keys)
#         writer.writeheader()
#         for candle in candles:
#             writer.writerow(candle.__dict__)

if __name__ == '__main__':

    binance = BinanceFuturesClient("", "", True)
    bitmex = BitmexClient("", "", True)

    # contract = binance.contracts['BTCUSDT']
    # candles = binance.get_historical_candles(contract, '1m')
    # save_candles_to_csv(candles, 'historical_candles.csv')
    # logger.info(f"Saved {len(candles)} candles to historical_candles.csv")

    root = Root(binance, bitmex)
    root.mainloop()
