import pandas as pd 
import numpy as np 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os 
import shutil
import glob
import time
import json 

def start_header(update_release: str='2019-06-04', version: str='0.1.01', default='VTI', options: str=None) -> dict:
    print(" ")
    print("----------------------------------")
    print("-   Securities Analysis Tools    -")
    print("-                                -")
    print("-            nga-27              -")
    print("-                                -")
    print(f"-       version: {version}          -")
    print(f"-       updated: {update_release}      -")
    print("----------------------------------")
    print(" ")

    time.sleep(1)
    config = dict()

    if options is not None:
        input_str = input("Enter ticker symbols (e.g. 'aapl MSFT') and tags (see --options): ")
    else:
        input_str = input("Enter ticker symbols (e.g. 'aapl MSFT'): ")

    config['version'] = version
    config['date_release'] = update_release

    config['state'] = 'run'
    config['period'] = '2y'
    config['interval'] = '1d'
    config['properties'] = {}
    config['core'] = False
    config['tickers'] = ''

    config, list_of_tickers = header_options_parse(input_str, config)
    
    if config['state'] == 'halt':
        return config
    if config['state'] == 'function':
        return config

    if (len(list_of_tickers) == 0) and (config['core'] == False):
        # Default (hitting enter)
        config['tickers'] = default

    else:
        if config['core'] == False:
            config['tickers'] = ticker_list_to_str(list_of_tickers)
            config['tickers'] = config['tickers'].strip()        
    
    config['tickers'] = config['tickers'].upper()
    ticker_print = ''

    # whitespace fixing on input strings
    t, config = remove_whitespace(config, default=default)

    if len(t) < 2:
        if 'no_index' not in config['state']:
            ticker_print += t[0] + ' and S&P500'
        else:
            ticker_print += t[0]
    else:
        for i in range(len(t)):
            if ('no_index' in config['state']) and (i == len(t)-1):
                ticker_print += t[i]
            else:
                if t[i] != '':
                    ticker_print += t[i] + ', '
        if 'no_index' not in config['state']:
            ticker_print += 'and S&P500'
    config['ticker print'] = ticker_print
    print(" ")
    return config 



def remove_whitespace(config: dict, default: str) -> list:
    # Remove '' entries in list
    t2 = config['tickers'].split(' ')
    t = []
    for t1 in t2:
        if t1 != '':
            t.append(t1)
    if len(t) == 0:
        config['tickers'] = default
        t = config['tickers'].split(' ')
    return t, config


def remove_whitespace_str(input_str: str) -> str:
    s = input_str.split(' ')
    s1 = []
    for s2 in s:
        if s2 != '':
            s1.append(s2)
    if len(s1) == 0:
        return ''
    s = ' '.join(s1)
    return s


def header_json_parse(key: str) -> list:
    json_path = ''
    if key == '--core':
        json_path = 'core.json'
    if key == '--test':
        json_path = 'test.json'

    if os.path.exists(json_path):
        tickers = ''
        with open(json_path) as json_file:
            core = json.load(json_file)
            for i in range(len(core['Ticker Symbols'])-1):
                tickers += core['Ticker Symbols'][i] + ' '
            tickers += core['Ticker Symbols'][len(core['Ticker Symbols'])-1]
            props = core['Properties']
            interval = props['Interval']
            period = props['Period']
    
    else:
        return None

    return [tickers, period, interval, props]


def key_parser(input_str: str) -> list:
    keys = input_str.split(' ')
    i_keys = []
    o_keys = []
    for key in keys:
        if key != '':
            o_keys.append(key)
    ticks = []
    for key in o_keys:
        if '--' not in key:
            ticks.append(key)
        else:
            i_keys.append(key)

    return i_keys, ticks


def ticker_list_to_str(ticker_list: list) -> str:
    tick_str = ''
    for tick in ticker_list:
        tick_str += tick + ' '
    return tick_str


def key_match(key: str, key_list: list) -> bool:
    for k in key_list:
        if k == key:
            return True 
    return False

####################################################################

def header_options_parse(input_str: str, config: dict) -> list:
    """ Input flag handling """

    config['state'] = ''
    config['run_functions'] = ''
    i_keys, ticker_keys = key_parser(input_str)

    if key_match('--options', i_keys):
        options_file = 'resources/header_options.txt'
        if os.path.exists(options_file):
            fs = open(options_file, 'r')
            options_read = fs.read()
            fs.close()
            print(" ")
            print(options_read)
            print(" ")
        else:
            print(f"ERROR - NO {options_file} found.")
            print(" ")
        config['state'] = 'halt'
        return config, ticker_keys

    # Configuration flags that append to states but do not return / force them
    if key_match('--core', i_keys):
        core = header_json_parse('--core')
        if core is not None:
            config['tickers'] = core[0]
            config['period'] = core[1]
            config['interval'] = core[2]
            config['properties'] = core[3]
            config['core'] = True

    if key_match('--test', i_keys):
        core = header_json_parse('--test')
        if core is not None:
            config['tickers'] = core[0]
            config['period'] = core[1]
            config['interval'] = core[2]
            config['properties'] = core[3]
            config['core'] = True

    if key_match('--noindex', i_keys):
        config = add_str_to_dict_key(config, 'state', 'no_index')


    # Configuration flags that append functions (requires '--function' flag)
    if key_match('--mci', i_keys):
        config = add_str_to_dict_key(config, 'run_functions', 'mci')

    if key_match('--bci', i_keys):
        config = add_str_to_dict_key(config, 'run_functions', 'bci')

    if key_match('--trend', i_keys):
        config['tickers'] = ticker_list_to_str(ticker_keys)
        config = add_str_to_dict_key(config, 'run_functions', 'trend')

    if key_match('--support_resistance', i_keys):
        config['tickers'] = ticker_list_to_str(ticker_keys)
        config = add_str_to_dict_key(config, 'run_functions', 'support_resistance')
    
    if key_match('--sr', i_keys) or key_match('--rs', i_keys):
        config['tickers'] = ticker_list_to_str(ticker_keys)
        config = add_str_to_dict_key(config, 'run_functions', 'support_resistance')

    if key_match('--clustered', i_keys) or key_match('--clustered_osc', i_keys):
        config['tickers'] = ticker_list_to_str(ticker_keys)
        config = add_str_to_dict_key(config, 'run_functions', 'clustered_oscs')

    if key_match('--head_shoulders', i_keys) or key_match('--hs', i_keys):
        config['tickers'] = ticker_list_to_str(ticker_keys)
        config = add_str_to_dict_key(config, 'run_functions', 'head_shoulders')
    
    if key_match('--corr', i_keys) or key_match('--correlation', i_keys):
        config = add_str_to_dict_key(config, 'run_functions', 'correlation')


    # Configuration flags that control state outcomes and return immediately after setting
    if key_match('--dev', i_keys):
        config['state'] = 'dev'
        return config, ticker_keys

    if key_match('--function', i_keys):
        config = add_str_to_dict_key(config, 'state', 'function run')
        return config, ticker_keys

    if key_match('--prod', i_keys):
        # default behavior
        config = add_str_to_dict_key(config, 'state', 'run')
        return config, ticker_keys

    if key_match('--r1', i_keys):
        config = add_str_to_dict_key(config, 'state', 'r1')
        return config, ticker_keys

    if key_match('--r2', i_keys):
        config = add_str_to_dict_key(config, 'state', 'r2')
        return config, ticker_keys
        
    config = add_str_to_dict_key(config, 'state', 'run')
    return config, ticker_keys


def add_str_to_dict_key(content: dict, key: str, item: str):
    if len(content[key]) > 0:
        content[key] += f", {item}"
    else:
        content[key] += item 
    return content
    