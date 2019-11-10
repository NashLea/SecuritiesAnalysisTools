import pandas as pd 
import numpy as np 

from libs.utils import download_data, has_critical_error
from libs.metrics import market_composite_index, bond_composite_index, correlation_composite_index
from libs.metrics import metadata_to_dataset
from libs.tools import get_trendlines, find_resistance_support_lines, cluster_oscs
from libs.features import feature_detection_head_and_shoulders

def only_functions_handler(config: dict):
    print(f"Running functions: '{config['run_functions']}' for {config['tickers']}")

    if 'mci' in config['run_functions']:
        mci_function(config)

    if 'bci' in config['run_functions']:
        bci_function(config)

    if 'trend' in config['run_functions']:
        trends_function(config)
    
    if 'support_resistance' in config['run_functions']:
        support_resistance_function(config)

    if 'clustered_oscs' in config['run_functions']:
        cluster_oscs_function(config)

    if 'head_shoulders' in config['run_functions']:
        head_and_shoulders_function(config)

    if 'correlation' in config['run_functions']:
        correlation_index_function(config)

    if 'export' in config['run_functions']:
        export_function(config)


###############################################################################

def mci_function(config: dict):
    config['properties'] = config.get('properties', {})
    config['properties']['Indexes'] = config['properties'].get('Indexes', {})
    config['properties']['Indexes']['Market Sector'] = config['properties']['Indexes'].get('Market Sector', True)
    market_composite_index(config=config, plot_output=True)


def bci_function(config: dict):
    config['properties'] = config.get('properties', {})
    config['properties']['Indexes'] = config['properties'].get('Indexes', {})
    config['properties']['Indexes']['Treasury Bond'] = True
    config['properties']['Indexes']['Corporate Bond'] = True
    config['properties']['Indexes']['International Bond'] = True
    bond_composite_index(config, plot_output=True)


def trends_function(config: dict):
    data, fund_list = download_data(config=config)
    e_check = {'tickers': config['tickers']}
    if has_critical_error(data, 'download_data', misc=e_check):
        return None
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Trends of {fund}...")
            get_trendlines(data[fund], plot_output=True, name=fund)


def support_resistance_function(config: dict):
    data, fund_list = download_data(config=config)
    e_check = {'tickers': config['tickers']}
    if has_critical_error(data, 'download_data', misc=e_check):
        return None
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Support & Resistance of {fund}...")
            find_resistance_support_lines(data[fund], plot_output=True, name=fund)


def cluster_oscs_function(config: dict):
    data, fund_list = download_data(config=config)
    e_check = {'tickers': config['tickers']}
    if has_critical_error(data, 'download_data', misc=e_check):
        return None
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Clustered Oscillators of {fund}...")
            cluster_oscs(data[fund], name=fund, plot_output=True, function='all')


def head_and_shoulders_function(config: dict):
    data, fund_list = download_data(config=config)
    e_check = {'tickers': config['tickers']}
    if has_critical_error(data, 'download_data', misc=e_check):
        return None
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"Head and Shoulders feature detection of {fund}...")
            feature_detection_head_and_shoulders(data[fund], name=fund, plot_output=True)


def correlation_index_function(config: dict):
    config['properties'] = config.get('properties', {})
    config['properties']['Indexes'] = config['properties'].get('Indexes', {})

    timeframe = config.get('duration', 'long')
    temp = {"run": True, "type": timeframe}
    config['properties']['Indexes']['Correlation'] = config['properties']['Indexes'].get('Correlation', temp)
    correlation_composite_index(config=config)


def export_function(config: dict):
    print(f"export_function")
    metadata_to_dataset(config)