import pandas as pd 
import numpy as np 
import yfinance as yf 

from .formatting import get_daterange

def download_data(config: dict) -> list:
    period = config['period']
    interval = config['interval']
    tickers = config['tickers']
    ticker_print = config['ticker print']

    if period is None:
        period = '2y'
    if interval is None:
        interval = '1d'
    
    daterange = get_daterange(period=period)
    
    if daterange[0] is None:
        print(f'Fetching data for {ticker_print} for {period} at {interval} intervals...')
        data = yf.download(tickers=tickers, period=period, interval=interval, group_by='ticker')
    else: 
        print(f'Fetching data for {ticker_print} from dates {daterange[0]} to {daterange[1]}...')
        data = yf.download(tickers=tickers, period=period, interval=interval, group_by='ticker', start=daterange[0], end=daterange[1])
    print(" ")

    return data


def data_nan_fix(fund_df1: pd.DataFrame) -> pd.DataFrame:
    """ Data sent via provider sometimes has NaN in spots, which breaks many algorithms. This patches some of those glitches. """

    fund_df = fund_df1.copy()
    close = list(np.where(pd.isna(fund_df['Close']) == True))[0]
    adjclose = list(np.where(pd.isna(fund_df['Adj Close']) == True))[0]
    vol = list(np.where(pd.isna(fund_df['Volume']) == True))[0]
    op = list(np.where(pd.isna(fund_df['Open']) == True))[0]
    high = list(np.where(pd.isna(fund_df['High']) == True))[0]
    low = list(np.where(pd.isna(fund_df['Low']) == True))[0]

    if len(close) > 0:
        for e, cl in enumerate(close):
            if (fund_df['Close'].isna()[cl-1] == False) and (cl != 0) and (cl + 1 != len(fund_df['Close'])) and (fund_df['Close'].isna()[cl+1] == False):
                fund_df['Close'][cl] = np.mean([fund_df['Close'][cl-1], fund_df['Close'][cl+1]])
    if len(adjclose) > 0:
        for e, cl in enumerate(adjclose):
            if (fund_df['Adj Close'].isna()[cl-1] == False) and (cl != 0) and (cl + 1 != len(fund_df['Adj Close'])) and (fund_df['Adj Close'].isna()[cl+1] == False):
                fund_df['Adj Close'][cl] = np.mean([fund_df['Adj Close'][cl-1], fund_df['Adj Close'][cl+1]])
    if len(vol) > 0:
        for e, cl in enumerate(vol):
            if (fund_df['Volume'].isna()[cl-1] == False) and (cl != 0) and (cl + 1 != len(fund_df['Volume'])) and (fund_df['Volume'].isna()[cl+1] == False):
                fund_df['Volume'][cl] = np.mean([fund_df['Volume'][cl-1], fund_df['Volume'][cl+1]])
    if len(op) > 0:
        for e, cl in enumerate(op):
            if (fund_df['Open'].isna()[cl-1] == False) and (cl != 0) and (cl + 1 != len(fund_df['Open'])) and (not fund_df['Open'].isna()[cl+1] == False):
                fund_df['Open'][cl] = np.mean([fund_df['Open'][cl-1], fund_df['Open'][cl+1]])
    if len(high) > 0:
        for e, cl in enumerate(high):
            if (fund_df['High'].isna()[cl-1] == False) and (cl != 0) and (cl + 1 != len(fund_df['High'])) and (fund_df['High'].isna()[cl+1] == False):
                fund_df['High'][cl] = np.mean([fund_df['High'][cl-1], fund_df['High'][cl+1]])
    if len(low) > 0:
        for e, cl in enumerate(low):
            if (fund_df['Low'].isna()[cl-1] == False) and (cl != 0) and (cl + 1 != len(fund_df['Low'])) and (fund_df['Low'].isna()[cl+1] == False):
                fund_df['Low'][cl] = np.mean([fund_df['Low'][cl-1], fund_df['Low'][cl+1]])

    return fund_df