"""
#   Technical Analysis Tools
#
#   by: nga-27
#
#   A program that outputs a graphical and a numerical analysis of
#   securities (stocks, bonds, equities, and the like). Analysis 
#   includes use of oscillators (Stochastic, RSI, and Ultimate), 
#   momentum charting (Moving Average Convergence Divergence, 
#   Simple and Exponential Moving Averages), trend analysis (Bands, 
#   Support and Resistance, Channels), and some basic feature 
#   detection (Head and Shoulders, Pennants).
#   
"""

# https://stackoverflow.com/questions/6323860/sibling-package-imports

# Use only after release!
################################
# _VERSION_ = '0.1.13'
# _DATE_REVISION_ = '2019-08-18'
################################

# Imports that are custom tools that are the crux of this program
from libs.tools import full_stochastic, ultimate_oscillator, cluster_oscs, RSI
from libs.tools import relative_strength, triple_moving_average, moving_average_swing_trade
from libs.tools import get_trend_analysis, mov_avg_convergence_divergence, on_balance_volume
from libs.tools import find_resistance_support_lines

# Imports that support functions doing feature detection
from libs.features import feature_head_and_shoulders, feature_plotter

# Imports that are generic file/string/object/date utility functions
from libs.utils import name_parser, fund_list_extractor, index_extractor, index_appender, date_extractor
from libs.utils import configure_temp_dir, remove_temp_dir, create_sub_temp_dir, download_data, data_nan_fix

# Imports that plot (many are imported in functions)
from libs.utils import candlestick

# Imports that drive custom metrics for market analysis
from libs.metrics import market_composite_index, bond_composite_index

# Imports that create final products and show progress doing so
from libs.utils import ProgressBar, start_header
from libs.outputs import slide_creator, output_to_json

# Imports in development / non-final "public" calls
from test import test_competitive
from libs.tools import get_maxima_minima, get_trendlines

####################################################################
####################################################################
PROCESS_STEPS = 13


def technical_analysis(config: dict):


    if config['state'] != 'run_no_index':
        config['tickers'] = index_appender(config['tickers'])
        # sp500_index = index_extractor(config['tickers'])

    # Temporary directories to save graphs as images, etc.
    remove_temp_dir()
    configure_temp_dir()

    data = download_data(config=config)
        
    funds = fund_list_extractor(data, config=config)

    # Start of automated process
    analysis = {}

    for fund_name in funds:
        
        print(f"~~{fund_name}~~")
        create_sub_temp_dir(fund_name)
        analysis[fund_name] = {}

        p = ProgressBar(PROCESS_STEPS, name=fund_name)
        p.start()

        if len(funds) > 1:
            fund = data[fund_name]
        else:
            fund = data

        fund = data_nan_fix(fund)
        p.uptick()

        start = date_extractor(fund.index[0], _format='str')
        end = date_extractor(fund.index[len(fund['Close'])-1], _format='str')

        analysis[fund_name]['dates_covered'] = {'start': str(start), 'end': str(end)} 
        analysis[fund_name]['name'] = fund_name

        chart, dat = cluster_oscs(fund, function='all', filter_thresh=3, name=fund_name, plot_output=False)
        analysis[fund_name]['clustered_osc'] = dat
        p.uptick()

        on_balance_volume(fund, plot_output=False, name=fund_name)
        p.uptick()

        triple_moving_average(fund, plot_output=False, name=fund_name)
        p.uptick()

        moving_average_swing_trade(fund, plot_output=False, name=fund_name)
        p.uptick()

        analysis[fund_name]['macd'] = mov_avg_convergence_divergence(fund, plot_output=False, name=fund_name)
        p.uptick()

        if config['state'] != 'run_no_index':
            analysis[fund_name]['relative_strength'] = relative_strength(   fund_name, fund_name, config=config, 
                                                                            tickers=data, sector='', plot_output=False)
        p.uptick()

        # Support and Resistance Analysis
        analysis[fund_name]['support_resistance'] = find_resistance_support_lines(fund, name=fund_name, plot_output=False)
        p.uptick()

        # Feature Detection Block
        shapes = []
        analysis[fund_name]['features'] = {}

        hs2, ma, shapes = feature_head_and_shoulders(fund, FILTER_SIZE=2, name=fund_name, shapes=shapes)
        analysis[fund_name]['features']['head_shoulders_2'] = hs2
        p.uptick()

        hs, ma, shapes = feature_head_and_shoulders(fund, FILTER_SIZE=4, name=fund_name, shapes=shapes)
        analysis[fund_name]['features']['head_shoulders_4'] = hs
        p.uptick()

        hs3, ma, shapes = feature_head_and_shoulders(fund, FILTER_SIZE=8, name=fund_name, shapes=shapes)
        analysis[fund_name]['features']['head_shoulders_8'] = hs3
        p.uptick()

        feature_plotter(fund, shapes, name=fund_name, feature='head_and_shoulders')
        p.uptick()

        filename = f"{fund_name}/candlestick_{fund_name}"
        candlestick(fund, title=fund_name, filename=filename, saveFig=True)
        p.uptick()

        # get_trendlines(fund)


    # test_competitive(data, analysis)

    market_composite_index(config=config)

    bond_composite_index(config=config)

    slide_creator(analysis, config=config)
    output_to_json(analysis)

    remove_temp_dir()

