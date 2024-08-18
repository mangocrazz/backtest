import pandas as pd
import numpy as np
import math
from sklearn.linear_model import LinearRegression
from .data_processing.py import generate_etime_close_data_divd_time

def backtest(original_data, index_code, frequency, n_days):
    position_size = 1 
    final_frame = original_data[['tdate', 'etime', 'close', 'fct']].dropna(axis=0).reset_index(drop=True)

    if frequency == 'd':
        t_delta = int(1 * n_days)
    else:
        t_delta = int(int(240 / int(frequency)) * n_days) 

    for i in range(0, len(final_frame) - t_delta, 1):
        final_frame.loc[i, 'ret'] = final_frame.loc[i + t_delta, 'close'] / final_frame.loc[i, 'close'] - 1

    final_frame = final_frame.dropna(axis=0).reset_index(drop=True)

    data_for_model = final_frame[['etime', 'close', 'fct', 'ret']]
    train_set_end_index = data_for_model[(data_for_model['etime'].dt.year == 2019) & (data_for_model['etime'].dt.month == 12) & (data_for_model['etime'].dt.day == 31)].index.values[0]

    model = LinearRegression(fit_intercept=True)
    X_train = data_for_model.loc[: train_set_end_index, 'fct'].values.reshape(-1, 1)
    y_train = data_for_model.loc[: train_set_end_index, 'ret'].values.reshape(-1, 1)
    X_test = data_for_model.loc[train_set_end_index + 1: , 'fct'].values.reshape(-1, 1)
    etime_train = data_for_model.loc[: train_set_end_index, 'etime'].values  
    etime_test = data_for_model.loc[train_set_end_index + 1: , 'etime'].values  
    etime_train_test = data_for_model.loc[:, 'etime'].values  

    model.fit(X_train, y_train)
    y_test_hat = model.predict(X_test)
    y_test_hat = [i[0] for i in y_test_hat]
    y_train_hat = model.predict(X_train)
    y_train_hat = [i[0] for i in y_train_hat]

    begin_date_train = pd.to_datetime(str(etime_train[0])).strftime('%Y-%m-%d %H:%M:%S')
    end_date_train = pd.to_datetime(str(etime_train[-1])).strftime('%Y-%m-%d %H:%M:%S')
    ret_frame_train_total = generate_etime_close_data_divd_time(begin_date_train, end_date_train, index_code, frequency)

    dt = pd.to_datetime(ret_frame_train_total['etime'], format='%Y-%m-%d %H:%M:%S.%f')
    ret_frame_train_total['etime'] = pd.Series([pd.Timestamp(x).round('s').to_pydatetime() for x in dt])

    start_index = ret_frame_train_total[ret_frame_train_total['etime'] == etime_train[0]].index.values[0]
    end_index = ret_frame_train_total[ret_frame_train_total['etime'] == etime_train[-1]].index.values[0]

    ret_frame_train_total = ret_frame_train_total.loc[start_index: end_index, :].reset_index(drop=True)
    ret_frame_train_total['position'] = [(i / 0.0005) * position_size for i in y_train_hat]
    
    for i in range(0, len(ret_frame_train_total), 1):
        if ret_frame_train_total.loc[i, 'position'] > 1:
            ret_frame_train_total.loc[i, 'position'] = 1
        elif ret_frame_train_total.loc[i, 'position'] < -1:
            ret_frame_train_total.loc[i, 'position'] = -1

    ret_frame_train = ret_frame_train_total
    ret_frame_train.loc[0, '持仓净值'] = 1
    
    for i in range(0, len(ret_frame_train), 1):
        if i == 0 or ret_frame_train.loc[i - 1, 'position'] == 0:
            ret_frame_train.loc[i, '持仓净值'] = 1
        else:
            close_2 = ret_frame_train.loc[i, 'close']
            close_1 = ret_frame_train.loc[i - 1, 'close']
            position = abs(ret_frame_train.loc[i - 1, 'position'])

            if ret_frame_train.loc[i - 1, 'position'] > 0:
                ret_frame_train.loc[i, '持仓净值'] = 1 * (close_2 / close_1) * position + 1 * (1 - position)
            elif ret_frame_train.loc[i - 1, 'position'] < 0:
                ret_frame_train.loc[i, '持仓净值'] = 1 * (1 - (close_2 / close_1 - 1)) * position + 1 * (1 - position)

    ret_frame_train.loc[0, '持仓净值（累计）'] = 1
    for i in range(1, len(ret_frame_train), 1):
        ret_frame_train.loc[i, '持仓净值（累计）'] = ret_frame_train.loc[i - 1, '持仓净值（累计）'] * ret_frame_train.loc[i, '持仓净值']

    # 后续代码根据需求进一步拆分或保留在此模块中
    # ...
    
    return ret_frame_train
