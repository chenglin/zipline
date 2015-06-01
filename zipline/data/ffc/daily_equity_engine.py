import shelve

import numpy as np
import pandas as pd

import bcolz

from zipline.data.baseloader import DataLoader

from zipline.data.adjusted_array import (
    adjusted_array,
    NOMASK,
)

COLUMN_TYPES = {
    'open': np.float64,
    'high': np.float64,
    'low': np.float64,
    'close': np.float64,
    'volume': np.uint32,
}


class DailyEquityLoader(DataLoader):

    def __init__(self, daily_bar_path, daily_index_path, trading_days):
        self.daily_bar_table = bcolz.open(daily_bar_path)
        self.daily_bar_index = shelve.open(daily_index_path)
        self.trading_days = trading_days

    def load_adjusted_array(self, columns, dates, assets):
        """
        Load each column with self.make_column.
        """
        nrows = len(dates)
        ncols = len(assets)

        data_arrays = {}
        for col in columns:
            data_arrays[col] = np.ndarray(
                shape=(nrows, ncols),
                dtype=COLUMN_TYPES[col])

        raw_data = {}
        for col in columns:
            raw_data[col] = self.daily_bar_table[col][:]

        start_pos = self.daily_bar_index['start_pos']
        start_day_offset = self.daily_bar_index['start_day_offset']

        date_offset = self.trading_days.searchsorted(dates[0])
        date_len = dates.shape[0]

        for col in columns:
            # doing this is repetitive
            for i, asset in enumerate(assets):
                start = start_pos[asset] - start_day_offset[asset] + \
                    date_offset
                # what if negative?
                # or handle case goes over
                # may need end_day_offset
                end = start + date_len
                asset_data = raw_data[col][start:end]

                if col != 'volume':
                    asset_data = asset_data * 0.001

                data_arrays[col][:, i] = asset_data

        return[
            adjusted_array(
                data_arrays[col],
                NOMASK,
                {})
            for col in columns]


if __name__ == "__main__":
    import zipline.finance.trading
    env = zipline.finance.trading.TradingEnvironment.instance()

    # use trading calendar instead
    min_date = pd.Timestamp('2002-01-02', tz='UTC')
    td = env.trading_days

    mask = (td > '2014-01-01') & (td < '2014-12-31')

    dates = env.trading_days[mask]

    loader = DailyEquityLoader("./equity_daily_bars.bcolz",
                               "./daily_equity_index.shelf",
                               trading_days=td[td >= min_date])

    result = loader.load_adjusted_array(
        ['close', 'volume'],
        dates,
        [2, 24],
    )

    assert True
