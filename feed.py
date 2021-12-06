from cryptofeed import FeedHandler
from cryptofeed.backends.influxdb import FundingInflux, TradeInflux, OpenInterestInflux, CandlesInflux, LiquidationsInflux
from cryptofeed.defines import FUNDING, TRADES, OPEN_INTEREST, CANDLES, LIQUIDATIONS
from cryptofeed.exchanges import Bitmex, Coinbase, BinanceFutures, FTX, Bybit, Huobi, HuobiDM, HuobiSwap, OKEx

import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

INFLUX_ADDR = os.getenv('INFLUX_ADDR')
ORG = os.getenv('INFLUX_ORG')
BUCKET = os.getenv('INFLUX_BUCKET')
TOKEN = 'INFLUX_TOKEN'

all_callbacks = {
            OPEN_INTEREST: OpenInterestInflux(INFLUX_ADDR, ORG, BUCKET, TOKEN),
            TRADES: TradeInflux(INFLUX_ADDR, ORG, BUCKET, TOKEN),
            LIQUIDATIONS: LiquidationsInflux(INFLUX_ADDR, ORG, BUCKET, TOKEN),
            CANDLES: CandlesInflux(INFLUX_ADDR, ORG, BUCKET, TOKEN),
            FUNDING: FundingInflux(INFLUX_ADDR, ORG, BUCKET, TOKEN)
        }


def sort_instruments(exchange):
    data = exchange.info()['instrument_type']
    spot = []
    perp = []
    future = []
    option = []
    for k, v in data.items():
        if v == 'spot':
            spot.append(k)
        elif v == 'perpetual':
            perp.append(k)
        elif v == 'futures':
            future.append(k)
        elif v == 'option':
            option.append(k)
    return spot, perp, future, option


def main():

    f = FeedHandler()

    # BINANCE -----------------------------------------------------
    binance_spot, binance_perp, binance_future, binance_option = sort_instruments(BinanceFutures)

    f.add_feed(BinanceFutures(
        channels=[FUNDING],
        symbols=binance_perp,
        callbacks=all_callbacks
    ))

    f.add_feed(BinanceFutures(
        channels=[TRADES, OPEN_INTEREST, LIQUIDATIONS],
        symbols=binance_perp + binance_future,
        callbacks=all_callbacks
    ))

    # COINBASE -----------------------------------------------------
    f.add_feed(Coinbase(
        channels=[TRADES],
        symbols=Coinbase.symbols(),
        callbacks=all_callbacks
    ))

    # BITMEX -----------------------------------------------------
    bitmex_spot, bitmex_perp, bitmex_future, bitmex_option = sort_instruments(Bitmex)

    f.add_feed(Bitmex(
        channels=[FUNDING],
        symbols=bitmex_perp,
        callbacks=all_callbacks
    ))

    f.add_feed(Bitmex(
        channels=[TRADES, OPEN_INTEREST, LIQUIDATIONS],
        symbols=bitmex_perp + binance_future,
        callbacks=all_callbacks
    ))

    # FTX ----------------------------------------------------------
    f.add_feed(FTX(
        channels=[TRADES, OPEN_INTEREST, LIQUIDATIONS, FUNDING],
        symbols=FTX.symbols(),
        callbacks=all_callbacks
    ))

    # BYBIT ----------------------------------------------------------
    f.add_feed(Bybit(
        channels=[TRADES, OPEN_INTEREST, LIQUIDATIONS, FUNDING],
        symbols=Bybit.symbols(),
        callbacks=all_callbacks
    ))

    # HUOBI ----------------------------------------------------------
    # pprint(Huobi.symbols())
    pprint(HuobiDM.symbols())
    # pprint(HuobiSwap.symbols())
    f.add_feed(HuobiDM(
        channels=[TRADES],
        symbols=HuobiDM.symbols(),
        callbacks=all_callbacks
    ))

    # OKEX ----------------------------------------------------------
    okex_spot, okex_perp, okex_future, okex_option = sort_instruments(OKEx)

    f.add_feed(OKEx(
        channels=[TRADES, OPEN_INTEREST, LIQUIDATIONS, FUNDING],
        symbols=okex_perp,
        callbacks=all_callbacks
    ))

    f.add_feed(OKEx(
        channels=[TRADES, OPEN_INTEREST, LIQUIDATIONS],
        symbols=okex_future,
        callbacks=all_callbacks
    ))

    f.run()


if __name__ == '__main__':
    main()
