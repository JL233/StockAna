import json

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy

def get_stock_basics():
    url='http://quote.eastmoney.com/stocklist.html'
    web_data=requests.get(url)
    #手动设置网页解码格式
    web_data.encoding = 'gbk'
    soup=BeautifulSoup(web_data.text,'lxml')
    #打印html
    #print(soup.prettify())
    stocks=soup.select('#quotesearch > ul > li > a')
    names=[]
    codes=[]
    for each in stocks:
        # 将正则表达式编译成Pattern对象
        pattern = re.compile(r'(.*?)\(([0-9]{6})\)')
        # 使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
        list = pattern.findall(each.text)
        if list:
            name=list[0][0]
            code=list[0][1]
            if code.startswith('0') or code.startswith('6') or code.startswith('3'):
                names.append(name)
                codes.append(code)
    s1 = pd.Series(numpy.array(names))
    s2 = pd.Series(numpy.array(codes))
    df = pd.DataFrame({"name": s1},index=s2);
    return df
#判断当天K线是否涨停板
def is_ztb(k_yest, k):
    close_yest = k_yest['close']
    close_today=k['close']
    ztb=close_yest*1.1
    if close_today-round(ztb,2)==0:
        return True
    return False
#判断是否具有长下影线
def is_shadow_down(k):
    open=k['open']
    close=k['close']
    high=k['high']
    low=k['low']
    unshadow=open-close if open>close else close-open
    shadow_down = close - low if open > close else open - low
    shadow_up = high - open if open > close else high - close
    if shadow_down/open<0.01:
        return False
    if shadow_down<2*shadow_up:
        return False
    if shadow_down>2*unshadow:
        return True
    if shadow_down/open>0.02:
        return True
    return False
#计算个股涨幅
def cal_uplift(k_yest,k):
    return (k['close']-k_yest['close'])/k_yest['close']
def get_money_flow(code):
    url = 'https://his.kaipanla.com/w1/api/index.php?apiv=w4'
    payload = {'c': 'StockLineData',
               'StockID': code,
               'Index': '0',
               'st': '151',
               'Type': 'd',
               'a': 'GetDaDanKLine2',
               'UserID': '233523',
               'Token': '4b19d1ccdbf6f4d4d28363fbc536b51e'
               }
    r = requests.post(url, data=payload, verify=False)
    resp_all = json.loads(r.text)
    return resp_all