import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 

from libs.utils import date_extractor, shape_plotting, generic_plotting

def local_extrema(filtered: list, raw=False) -> dict:
    """
    Assuming a filtered list input, finds local minima and maxima
    Returns:
        extrema - dict() -> dictionary of lists of extrema indices of 'filtered'
            keys: 'min', 'max'
    """
    extrema = {}
    extrema['max'] = []
    extrema['min'] = []
    direct = 0
    if not raw:
        for i in range(1, len(filtered)):
            if direct == 0:
                if filtered[i] > filtered[i-1]:
                    direct = 1
                else:
                    direct = -1
            elif direct == 1:
                if filtered[i] < filtered[i-1]:
                    direct = -1
                    extrema['max'].append(i-1)
            else:
                if filtered[i] > filtered[i-1]:
                    direct = 1
                    extrema['min'].append(i-1)

    else:
        extrema = raw_signal_extrema(filtered)
        # print(f"extrema: {extrema}")
        # y = []
        # y2 = []
        # for max_ in extrema['max']:
        #     y.append(filtered[max_])
        # for min_ in extrema['min']:
        #     y2.append(filtered[min_])
        # generic_plotting([y,y2], x_=[extrema['max'], extrema['min']], legend=['max', 'min'])

    return extrema


def reconstruct_extrema(original: pd.DataFrame, extrema: dict, ma_size: int, ma_type='simple') -> dict:
    """ 
    Function to find true extrema on 'original', especially when 'extrema' is generated
    from a filtered / averaged signal (moving averages introduce time shifting). Uses 
    Args:
        original:   pd.DataFrame -> specifically of 'Close' key (so easily castable to type list)
        extrema:    dict -> keys: 'min', 'max' of filtered signal
        ma_size:    int -> moving average filter size (used for reconditioning)
        ma_type:    type of filter (matching for reconstruction is key)
    
    Returns:
        recon:      dict -> keys: 'min', 'max'; each key has a list of format:
                    [index_of_min_or_max, value]
    """

    recon = {}
    recon['max'] = []
    recon['min'] = []
    olist = list(original)

    if ma_type == 'simple':
        for _max in extrema['max']:
            start = _max - ma_size
            if start < 0:
                start = 0
            # Search for the maximum on the original signal between 'start' and '_max'.
            recon['max'].append([olist.index(np.max(olist[start:_max]), start, _max), np.max(olist[start:_max+1])])

        for _min in extrema['min']:
            start = _min - ma_size
            if start < 0:
                start = 0
            # Search for the maximum on the original signal between 'start' and '_min'.
            recon['min'].append([olist.index(np.min(olist[start:_min]), start, _min), np.min(olist[start:_min+1])])

    if ma_type == 'windowed':
        ma_size_adj = int(np.floor(float(ma_size)/2.0))
        for _max in extrema['max']:
            start = _max - ma_size_adj
            end = _max + ma_size_adj
            if start == end:
                end += 1
            if start < 0:
                start = 0
            if end > len(olist):
                end = len(olist)
            # Search for the maximum on the original signal between 'start' and 'end'.
            recon['max'].append([olist.index(np.max(olist[start:end]), start, end), np.max(olist[start:end])])

        for _min in extrema['min']:
            start = _min - ma_size_adj
            end = _min + ma_size_adj
            if start == end:
                end += 1
            if start < 0:
                start = 0
            if end > len(olist):
                end = len(olist)
            # Search for the maximum on the original signal between 'start' and 'end'.
            recon['min'].append([olist.index(np.min(olist[start:end]), start, end), np.min(olist[start:end])])
    
    return recon



def remove_duplicates(recon: dict, method='threshold', threshold=0.01) -> dict:

    """ Removes duplicates of extrema (due to equal tops/bottoms, errors, those w/in a threshold of its neighbor) """
    if method == 'threshold':
        most_recent = 0
        newlist = []
        for i in range(len(recon['max'])):
            if (recon['max'][i][0] != most_recent) and ((recon['max'][i][1] > recon['max'][i-1][1] * (1+threshold)) or (recon['max'][i][1] < recon['max'][i-1][1] * (1-threshold))):
                most_recent = recon['max'][i][0]
                newlist.append(recon['max'][i])
        recon['max'] = newlist
        newlist = []
        most_recent = 0
        for i in range(len(recon['min'])):
            if (recon['min'][i][0] != most_recent) and ((recon['min'][i][1] > recon['min'][i-1][1] * (1+threshold)) or (recon['min'][i][1] < recon['min'][i-1][1] * (1-threshold))):
                most_recent = recon['min'][i][0]
                newlist.append(recon['min'][i])
        recon['min'] = newlist
    
    """ In some extrema dicts, we want granularity but not duplicated points. If an x-axis value matches one in the list, do not add it.  Simple! """
    if method == 'point':
        most_recent = 0
        newlist = []
        for i in range(len(recon['max'])):
            if (recon['max'][i][0] != most_recent):
                most_recent = recon['max'][i][0]
                newlist.append(recon['max'][i])
        recon['max'] = newlist
        newlist = []
        most_recent = 0
        for i in range(len(recon['min'])):
            if (recon['min'][i][0] != most_recent):
                most_recent = recon['min'][i][0]
                newlist.append(recon['min'][i])
        recon['min'] = newlist

    return recon 



def add_daterange(original: pd.DataFrame, extrema: dict, num_feature_points: int) -> dict:
    """
    Looks at index ranges of 'extrema' and adds actual dates from 'original' to 'extrema'
    """
    for feat in extrema['features']:
        if feat:
            first_ind = feat['indexes'][0][0]
            last_ind = feat['indexes'][num_feature_points-1][0]
            start = date_extractor(original.index[first_ind], _format='str')
            end = date_extractor(original.index[last_ind], _format='str')
            feat['daterange'] = start + ' : ' + end

    return extrema


def remove_empty_keys(dictionary: dict) -> dict:
    """ 
    Cleans and removes empty dictionary or list parameters for concise structuring
    """
    new_dict = {}
    new_dict['min'] = dictionary['min']
    new_dict['max'] = dictionary['max']
    new_dict['features'] = []
    for feat in dictionary['features']:
        if feat:
            # essentially, if not empty
            new_dict['features'].append(feat)

    return new_dict        


def feature_plotter(fund: pd.DataFrame, shapes: list, name='',  feature='head_and_shoulders', plot_output=True):
    """
    Plots a rectangle of where the feature was detected overlayed on the ticker signal.
    """
    filename = name + f'/{feature}_{name}.png'
    title = f'{name} Feature Detection: '
    if feature == 'head_and_shoulders':
        title += 'Head and Shoulders'

    saveFig = not plot_output

    shape_plotting( fund['Close'], 
                    shapeXY=shapes, 
                    feature=feature, 
                    saveFig=saveFig, 
                    title=title,
                    filename=filename)


def raw_signal_extrema(signal: list, threshold_start=0.01) -> dict:
    extrema = {}
    extrema['max'] = []
    extrema['min'] = []
    sig_len = len(signal)

    for threshold in [0.01, 0.015, 0.02, 0.025, 0.03, 0.035]:
        i = 0
        temp = [{"index": i, "value": signal[i], "type": 0}]
        if signal[1] > signal[0]:
            temp[0]['type'] = -1
            direct = 1
        else:
            temp[0]['type'] = 1
            direct = -1
        
        i = 2
        need_to_pop = False
        was_max = False
        while (i < sig_len):
            if len(temp) > 0:
                if temp[0]['type'] == -1:
                    # We have a potential local max
                    if signal[i] > temp[0]['value'] * (1.0 + threshold):
                        # Valid minima, remove from list
                        extrema['min'].append(temp[0]['index'])
                        need_to_pop = True
                        was_max = False
                    if signal[i] < temp[0]['value'] * (1.0 - threshold):
                        # Was not valid by threshold, so remove and wait
                        need_to_pop = True
                if temp[0]['type'] == 1:
                    # We have a potential local max
                    if signal[i] < temp[0]['value'] * (1.0 - threshold):
                        # Valid minima, remove from list
                        extrema['max'].append(temp[0]['index'])
                        need_to_pop = True
                        was_max = True
                    if signal[i] > temp[0]['value'] * (1.0 + threshold):
                        # Was not valid by threshold, so remove and wait
                        need_to_pop = True

                if direct == 1:
                    if signal[i] < signal[i-1]:
                        direct = -1
                else:
                    if signal[i] > signal[i-1]:
                        direct = 1

            else:
                if direct == 1:
                    if signal[i] < signal[i-1]:
                        if not was_max:
                            temp.append({"index": i-1, "value": signal[i-1], "type": direct})
                        direct = -1
                else:
                    if signal[i] > signal[i-1]:
                        if was_max:
                            temp.append({"index": i-1, "value": signal[i-1], "type": direct})
                        direct = 1

            if need_to_pop:
                need_to_pop = False
                temp.pop(0)

            i += 1

    return extrema


def cleanse_to_json(content: dict) -> dict:
    for i in range(len(content['content']['features'])):
        for j in range(len(content['content']['features'][i]['indexes'])):
            vol = content['content']['features'][i]['indexes'][j][2]
            vol = float(vol)/1000
            content['content']['features'][i]['indexes'][j][2] = vol


    return content
