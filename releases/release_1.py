"""
release_1.py

Main release for milestone/release 1.
    > Technical analysis tools:
        > MACD
        > Clustered Oscillators
        > Moving Averages
        > Relative Strength (vs. S&P500)
        > Head & Shoulders feature detection
        > On-Balance Volume
    > Reporting outputs per security analyzed:
        > JSON with details
        > Powerpoint with plotting and summaries
    > Progress bar for analysis

Nick Amell
May 10, 2019
"""

import pandas as pd 
import numpy as np 
import pprint 

import yfinance as yf 

from libs.tools import full_stochastic, ultimate_oscillator, cluster_oscs, RSI
from libs.tools import relative_strength, triple_moving_average, moving_average_swing_trade
from libs.features import feature_head_and_shoulders

from libs.tools import get_trend_analysis, mov_avg_convergence_divergence, on_balance_volume
from libs.utils import name_parser, fund_list_extractor, index_extractor, index_appender, date_extractor, get_daterange
from libs.utils import configure_temp_dir, remove_temp_dir, create_sub_temp_dir

from libs.utils import ProgressBar, start_header
from libs.outputs import slide_creator, output_to_json
from libs.metrics import market_composite_index


################################
_VERSION_ = '0.1.00'
_DATE_REVISION_ = '2019-06-04'
################################

def release_1():

    print(" ")
    print("~~~~ RELEASE 1 ~~~~ [deprecated but supported]")
    
    config = start_header(update_release=_DATE_REVISION_, version=_VERSION_)
    tickers = config['tickers']
    ticker_print = config['ticker print']
    period = config['period']
    interval = config['interval']

    PROCESS_STEPS = 9

    # DO NOT INCLUDE ^GSPC IN 'tickers' STRING

    tickers = index_appender(tickers)
    sp500_index = index_extractor(tickers)

    remove_temp_dir()
    configure_temp_dir()

    daterange = get_daterange()
    period = '1y'
    interval = '1d'

    if daterange[0] is None:
        print(f'Fetching data for {ticker_print} for {period} at {interval} intervals...')
        data = yf.download(tickers=tickers, period=period, interval=interval, group_by='ticker')
    else: 
        print(f'Fetching data for {ticker_print} from dates {daterange[0]} to {daterange[1]}...')
        data = yf.download(tickers=tickers, period=period, interval=interval, group_by='ticker', start=daterange[0], end=daterange[1])
    print(" ")
        
    funds = fund_list_extractor(data)

    # Start of automated process
    analysis = {}

    for fund_name in funds:

        name = fund_name
        
        create_sub_temp_dir(name)
        analysis[name] = {}

        p = ProgressBar(PROCESS_STEPS, name=name)
        p.start()

        fund = data[fund_name]
        p.uptick()
        p.uptick()

        start = date_extractor(fund.index[0], _format='str')
        end = date_extractor(fund.index[len(fund['Close'])-1], _format='str')

        analysis[name]['dates_covered'] = {'start': str(start), 'end': str(end)} 
        analysis[name]['name'] = name

        chart, dat = cluster_oscs(fund, function='all', filter_thresh=3, name=name, plot_output=False)
        analysis[name]['clustered_osc'] = dat
        p.uptick()

        on_balance_volume(fund, plot_output=False, name=name)
        p.uptick()

        triple_moving_average(fund, plot_output=False, name=name)
        p.uptick()

        moving_average_swing_trade(fund, plot_output=False, name=name)
        p.uptick()

        analysis[name]['macd'] = mov_avg_convergence_divergence(fund, plot_output=False, name=name)
        p.uptick()

        analysis[name]['relative_strength'] = relative_strength(fund_name, fund_name, tickers=data, sector='', plot_output=False)
        analysis[name]['features'] = {}

        p.uptick()

        hs, ma, shapes = feature_head_and_shoulders(fund, shapes=[])
        analysis[name]['features']['head_shoulders'] = hs
        p.uptick()


    market_composite_index(period=period) 

    slide_creator(year='2019', analysis=analysis, version=_VERSION_)
    output_to_json(analysis)

    remove_temp_dir()
    # print('Done.')
