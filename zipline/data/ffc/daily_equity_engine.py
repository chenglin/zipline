import numpy as np

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

    def __init__(self, daily_bar_path):
        self.daily_bar_table = bcolz.open(daily_bar_path)

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

        return[
            adjusted_array(
                data_arrays[col],
                NOMASK,
                {})
            for col in columns]


if __name__ == "__main__":
    import zipline.finance.trading
    loader = DailyEquityLoader("./equity_daily_bars.bcolz")

    env = zipline.finance.trading.TradingEnvironment.instance()

    # use trading calendar instead
    td = env.trading_days
    mask = (td > '2014-01-01') & (td < '2014-02-01')

    dates = env.trading_days[mask]
    result = loader.load_adjusted_array(
        ['close', 'volume'],
        dates,
        [2, 24],
    )

    import pprint; import nose; nose.tools.set_trace()
    assert True
