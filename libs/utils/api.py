import yfinance as yf 
import pandas as pd 
import numpy as np 

from datetime import datetime
from dateutil.relativedelta import relativedelta

import libs.utils.stable_yf as styf

"""
    Utilizes advanced api calls of 'yfinance==0.1.50' as of 2019-11-21
"""

def get_dividends(ticker):
    div = dict()
    try:
        t = ticker.dividends
        div['dates'] = [date.strftime("%Y-%m-%d") for date in t.keys()]
        div['dividends'] = [t[date] for date in t.keys()]
    except:
        div['dividends'] = []
        div['dates'] = []
    return div

def get_info(ticker, st):
    try:
        info = ticker.info
    except:
        try:
            info = st.info
        except:
            info = dict()
    return info

def get_financials(ticker, st):
    try:
        t = ticker.financials
        fin = {index: list(row) for index, row in t.iterrows()}
        fin['dates'] = [col.strftime('%Y-%m-%d') for col in t.columns]
    except:
        try:
            t = st.financials
            fin = {index: list(row) for index, row in t.iterrows()}
            fin['dates'] = [col.strftime('%Y-%m-%d') for col in t.columns]
        except:
            fin = dict()
    return fin

def get_balance_sheet(ticker, st):
    try:
        t = ticker.balance_sheet
        bal = {index: list(row) for index, row in t.iterrows()}
        bal['dates'] = [col.strftime('%Y-%m-%d') for col in t.columns]
    except:
        try:
            t = st.balance_sheet
            bal = {index: list(row) for index, row in t.iterrows()}
            bal['dates'] = [col.strftime('%Y-%m-%d') for col in t.columns]
        except:
            bal = dict()
    return bal
        
def get_cashflow(ticker, st):
    try:
        t = ticker.cashflow
        cash = {index: list(row) for index, row in t.iterrows()}
        cash['dates'] = [col.strftime('%Y-%m-%d') for col in t.columns]
    except:
        try:
            t = st.balance_sheet
            cash = {index: list(row) for index, row in t.iterrows()}
            cash['dates'] = [col.strftime('%Y-%m-%d') for col in t.columns]
        except:
            cash = dict()
    return cash

def get_earnings(ticker, st):
    earn = dict()
    try:
        t = ticker.earnings 
        ey = dict()
        ey['period'] = list(t.index)
        ey['revenue'] = [r for r in t['Revenue']]
        ey['earnings'] = [e for e in t['Earnings']]
        earn['yearly'] = ey
        q = ticker.quarterly_earnings
        eq = dict()
        eq['period'] = list(q.index)
        eq['revenue'] = [r for r in q['Revenue']]
        eq['earnings'] = [e for e in t['Earnings']]
        earn['quarterly'] = eq
    except:
        try:
            t = st.earnings 
            ey = dict()
            ey['period'] = list(t.index)
            ey['revenue'] = [r for r in t['Revenue']]
            ey['earnings'] = [e for e in t['Earnings']]
            earn['yearly'] = ey
            q = st.quarterly_earnings
            eq = dict()
            eq['period'] = list(q.index)
            eq['revenue'] = [r for r in q['Revenue']]
            eq['earnings'] = [e for e in t['Earnings']]
            earn['quarterly'] = eq 
        except:
            earn['yearly'] = {}
            earn['quarterly'] = {}
    return earn

def get_recommendations(ticker, st):
    recom = dict()
    try:
        t = ticker.recommendations
        recom['dates'] = [date.strftime('%Y-%m-%d') for date in t.index]
        recom['firms'] = [f for f in t['Firm']]
        recom['grades'] = [g for g in t['To Grade']]
        recom['actions'] = [a for a in t['Action']]
    except:
        try:
            t = st.recommendations
            recom['dates'] = [date.strftime('%Y-%m-%d') for date in t.index]
            recom['firms'] = [f for f in t['Firm']]
            recom['grades'] = [g for g in t['To Grade']]
            recom['actions'] = [a for a in t['Action']]
        except:
            recom = {'dates': [], 'firms': [], 'grades': [], 'actions': []}
    return recom


AVAILABLE_KEYS = {
    "dividends": get_dividends,
    "info": get_info,
    "financials": get_financials,
    "balance": get_balance_sheet,
    "cashflow": get_cashflow,
    "earnings": get_earnings,
    "recommendations": get_recommendations
}

def get_api_metadata(fund_ticker: str):
    metadata = {}
    ticker = yf.Ticker(fund_ticker)
    st_tick = styf.Ticker(fund_ticker)

    metadata['dividends'] = AVAILABLE_KEYS.get('dividends')(ticker)
    metadata['info'] = AVAILABLE_KEYS.get('info')(ticker, st_tick)
    metadata['financials'] = AVAILABLE_KEYS.get('financials')(ticker, st_tick)
    metadata['balance_sheet'] = AVAILABLE_KEYS.get('balance')(ticker, st_tick)
    metadata['cashflow'] = AVAILABLE_KEYS.get('cashflow')(ticker, st_tick)
    metadata['earnings'] = AVAILABLE_KEYS.get('earnings')(ticker, st_tick)
    metadata['recommendations'] = AVAILABLE_KEYS.get('recommendations')(ticker, st_tick)
    
    metadata['recommendations']['tabular'] = calculate_recommendation_curve(metadata['recommendations'])
    # EPS needs some other figures to make it correct, but ok for now.
    metadata['eps'] = calculate_eps(metadata)

    return metadata


def calculate_recommendation_curve(recoms: dict) -> dict:
    tabular = dict()
    tabular['dates'] = []
    tabular['grades'] = []

    if len(recoms['dates']) > 0:
        firms = {}
        dates = []
        grades = []
        dates_x = recoms.get('dates', [])
        grades_x = grade_to_number(recoms.get('grades', []))
        firms_x = recoms.get('firms', [])

        i = 0
        while i < len(dates_x):
            date = dates_x[i]
            dates.append(date)
            while (i < len(dates_x)) and (date == dates_x[i]):
                firms[firms_x[i]] = {}
                firms[firms_x[i]]['grade'] = grades_x[i]
                firms[firms_x[i]]['date'] = date
                i += 1
            firms = prune_ratings(firms, date)
            sum_ = [firms[key]['grade'] for key in firms.keys()]
            grades.append(np.mean(sum_))

        tabular['grades'] = grades 
        tabular['dates'] = dates

    return tabular


def grade_to_number(grades: list) -> list:
    GRADES = {
        "Strong Buy": 1.0,
        "Buy": 2.0,
        "Overweight": 2.0,
        "Outperform": 2.0,
        "Neutral": 3.0,
        "Hold": 3.0,
        "Market Perform": 3.0,
        "Equal-Weight": 3.0,
        "Sector Perform": 3.0,
        "Underperform": 4.0,
        "Underweight": 4.0,
        "Sell": 5.0
    }

    val_grad = []
    for grade in grades:
        val_grad.append(GRADES.get(grade, 3.0))
    return val_grad


def prune_ratings(firms: dict, date: str) -> dict:
    td = datetime.strptime(date, '%Y-%m-%d')
    for firm in list(firms):
        td2 = datetime.strptime(firms[firm]['date'], '%Y-%m-%d')
        td2 = td2 + relativedelta(years=2)
        if td > td2:
            firms.pop(firm)
    return firms


def calculate_eps(meta: dict) -> dict:
    eps = dict()
    q_earnings = meta.get('earnings', {}).get('quarterly', {})
    shares = meta.get('info', {}).get('sharesOutstanding')

    if shares and q_earnings:
        eps['period'] = []
        eps['eps'] = []
        for i,earn in enumerate(q_earnings['earnings']):
            eps['period'].append(q_earnings['period'][i])
            eps['eps'].append(np.round(earn / shares, 3))

    return eps
    