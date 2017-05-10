import datetime
import json

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import tushare as ts
from dateutil.relativedelta import relativedelta

import utils

#T日涨停板，T+1日、T+2日小幅调整不超过2个点，两天总幅度不超过两个点
def ztb_2day(code,T):
    try:
        T_date = datetime.datetime.strptime(T, "%Y-%m-%d")
        T_before = (T_date - relativedelta(days=10)).strftime("%Y-%m-%d")
        T_after = (T_date + relativedelta(days=10)).strftime("%Y-%m-%d")
        kdata = ts.get_k_data(code, index=False, start=T_before, end=T_after)
        #T日数据
        T_data=kdata.loc[kdata.date==T]
        #得到T日K线数据在DataFrame中的索引
        T_index=T_data.index[0]
        if T_index-1 in kdata.index:
            T_yest_data=kdata.loc[T_index-1]
        else:
            return False
        threshold=0.025
        #如果T日是涨停板
        if utils.is_ztb(T_yest_data, T_data.iloc[0]):
            T_after1_lift=utils.cal_uplift(T_data.iloc[0],kdata.loc[T_index+1])
            #如果T+2的数据没有更新，name这天的涨幅当做0计算
            if T_index + 2 in kdata.index:
                T_after2_lift = utils.cal_uplift(kdata.loc[T_index+1], kdata.loc[T_index + 2])
            else:
                T_after2_lift = 0

            if abs(T_after1_lift+T_after2_lift)<threshold and abs(T_after1_lift)<threshold and abs(T_after2_lift)<threshold :
                return True
    except IndexError:
        #print(code+'k线数据不足')
        pass
    except KeyError:
        #print(code+'KeyError')
        pass
    return False

#T日最近20天资金流入是流出两倍
def money_in_double(code,T):
    resp_all = utils.get_money_flow(code)
    Date=resp_all['Date']
    try:
        index=Date.index(T.replace('-',''))
    except ValueError:
        print(code+T+'数据不足')
        return False
    TDJL=resp_all['TDJL']
    in_amount=0
    out_amount=0
    length=20 if len(TDJL) >20+index else len(TDJL)-index
    for i in range(length):
        amount=TDJL[i+index]
        if amount>0:
            in_amount+=TDJL[i]
        else:
            out_amount+=TDJL[i]
    if abs(in_amount)>abs(out_amount)*5:
        return True
    return False





#当天涨停板，且资金净流入
def money_in_ztb(code,T):
    try:
        T_date = datetime.datetime.strptime(T, "%Y-%m-%d")
        T_before = (T_date - relativedelta(days=10)).strftime("%Y-%m-%d")
        T_after = (T_date + relativedelta(days=10)).strftime("%Y-%m-%d")
        kdata = ts.get_k_data(code, index=False, start=T_before, end=T_after)
        # T日数据
        T_data = kdata.loc[kdata.date == T]
        # 得到T日K线数据在DataFrame重的索引
        T_index = T_data.index[0]
        if T_index - 1 in kdata.index:
            T_before_1_data = kdata.loc[T_index - 1]
        else:
            return False

        # 如果T日是涨停板
        if utils.is_ztb(T_before_1_data, T_data.iloc[0]):
            resp_all = utils.get_money_flow(code)
            Date=resp_all['Date']
            try:
                index=Date.index(T.replace('-',''))
            except ValueError:
                print(code+T+'资金净额数据不足')
                return False
            #特大资金
            td_amount=resp_all['TDJL'][index]
            #大单资金
            dd_amount = resp_all['DDJL'][index]
            if td_amount>0 :
                if dd_amount>0:
                    return True
                elif dd_amount*3<td_amount:
                    return True
            return False
    except IndexError:
        #print(code+'k线数据不足')
        pass
    except KeyError:
        #print(code+'KeyError')
        pass
    return False

def dtb_2day(code,T):
    try:
        T_date = datetime.datetime.strptime(T, "%Y-%m-%d")
        T_before = (T_date - relativedelta(days=10)).strftime("%Y-%m-%d")
        T_after = (T_date + relativedelta(days=10)).strftime("%Y-%m-%d")
        kdata = ts.get_k_data(code, index=False, start=T_before, end=T_after)
        #T日数据
        T_data=kdata.loc[kdata.date==T]
        #得到T日K线数据在DataFrame中的索引
        T_index=T_data.index[0]
        if T_index-1 in kdata.index:
            T_yest_data=kdata.loc[T_index-1]
        else:
            return False
        #如果T日最低价是跌停价
        if round(T_yest_data['close']*0.9,2)==T_data.iloc[0]['low']:
            if kdata.loc[T_index + 1]['close']>kdata.loc[T_index ]['low'] and kdata.loc[T_index +2]['close']>kdata.loc[T_index ]['low']:
                return True
    except IndexError:
        #print(code+'k线数据不足')
        pass
    except KeyError:
        #print(code+'KeyError')
        pass
    return False

def shadow_down2(code, T):
    try:
        T_date = datetime.datetime.strptime(T, "%Y-%m-%d")
        T_before = (T_date - relativedelta(days=10)).strftime("%Y-%m-%d")
        T_after = (T_date + relativedelta(days=10)).strftime("%Y-%m-%d")
        kdata = ts.get_k_data(code, index=False, start=T_before, end=T_after)
        #T日数据
        T_data=kdata.loc[kdata.date==T]
        T_k=T_data.iloc[0]
        #得到T日K线数据在DataFrame中的索引
        T_index=T_data.index[0]
        if T_index-1 in kdata.index:
            T_yest_data=kdata.loc[T_index-1]
        else:
            return False
        T_yest_k = kdata.loc[T_index - 1]
        #如果T日最低价是跌停价
        if utils.is_shadow_down(T_k) and utils.is_shadow_down(T_yest_k):
            return True
    except IndexError:
        #print(code+'k线数据不足')
        pass
    except KeyError:
        #print(code+'KeyError')
        pass
    return False