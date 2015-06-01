import shelve

import numpy as np
import pandas as pd

import bcolz

def build_daily_equity_index(table, trading_days):
    sids = table['sid'][:]
    days = table['day'][:]

    start_pos = {}
    start_day_offset = {}

    curr_sid = 0

    for i in xrange(sids.shape[0]):
        sid = sids[i]
        if curr_sid != sid:
            start_pos[sid] = i
            day = pd.Timestamp(days[i], unit='s', tz='UTC')
            offset = trading_days.searchsorted(day)
            start_day_offset[sid] = offset
            curr_sid = sid

    d = shelve.open('./daily_equity_index.shelf')
    d['start_pos'] = start_pos
    d['start_day_offset'] = start_day_offset

    d.close()


if __name__ == "__main__":
    import zipline.finance.trading
    table = bcolz.open("./equity_daily_bars.bcolz")

    env = zipline.finance.trading.TradingEnvironment.instance()

    days = table['day'][:]

    # Can get this from other places.
    min_day_s = np.amin(days)

    min_day = pd.Timestamp(min_day_s, unit='s', tz='UTC')

    # use trading calendar instead
    td = env.trading_days
    td = td[td >= min_day]

    build_daily_equity_index(table, td)
