#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2025/3/10 18:00
Desc: 东方财富网-行情首页-沪深京 A 股
https://quote.eastmoney.com/
"""

import pandas as pd
import requests


def stock_zh_a_hist(
    symbol: str = "000001",
    period: str = "daily",
    start_date: str = "19700101",
    end_date: str = "20500101",
    adjust: str = "",
    timeout: float = None,
) -> pd.DataFrame:
    """
    东方财富网-行情首页-沪深京 A 股-每日行情
    https://quote.eastmoney.com/concept/sh603777.html?from=classic
    :param symbol: 股票代码
    :type symbol: str
    :param period: choice of {'daily', 'weekly', 'monthly'}
    :type period: str
    :param start_date: 开始日期
    :type start_date: str
    :param end_date: 结束日期
    :type end_date: str
    :param adjust: choice of {"qfq": "前复权", "hfq": "后复权", "": "不复权"}
    :type adjust: str
    :param timeout: choice of None or a positive float number
    :type timeout: float
    :return: 每日行情
    :rtype: pandas.DataFrame
    """
    market_code = 1 if symbol.startswith("6") else 0
    adjust_dict = {"qfq": "1", "hfq": "2", "": "0"}
    period_dict = {"daily": "101", "weekly": "102", "monthly": "103"}
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"

    flist = []
    for i in range(1001):
        flist.append(f'f{i}')
    x= ','.join(flist)
    
    params = {
        "fields1": f"f1,f2",
        "fields2": f"f76,f77",
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "klt": period_dict[period],
        "fqt": adjust_dict[adjust],
        "secid": f"{market_code}.{symbol}",
        "beg": start_date,
        "end": end_date,
    }
    r = requests.post(url, data=params, timeout=timeout)
    data_json = r.json()
    if not (data_json["data"] and data_json["data"]["klines"]):
        return pd.DataFrame()
    temp_df = pd.DataFrame([item.split(",") for item in data_json["data"]["klines"]])
    temp_df["股票代码"] = symbol
    temp_df.columns = [
        "日期",
        "开盘",
        "收盘",
        "最高",
        "最低",
        "成交量",
        "成交额",
        "振幅",
        "涨跌幅",
        "涨跌额",
        "换手率",
        "股票代码",
    ]
    temp_df["日期"] = pd.to_datetime(temp_df["日期"], errors="coerce").dt.date
    temp_df["开盘"] = pd.to_numeric(temp_df["开盘"], errors="coerce")
    temp_df["收盘"] = pd.to_numeric(temp_df["收盘"], errors="coerce")
    temp_df["最高"] = pd.to_numeric(temp_df["最高"], errors="coerce")
    temp_df["最低"] = pd.to_numeric(temp_df["最低"], errors="coerce")
    temp_df["成交量"] = pd.to_numeric(temp_df["成交量"], errors="coerce")
    temp_df["成交额"] = pd.to_numeric(temp_df["成交额"], errors="coerce")
    temp_df["振幅"] = pd.to_numeric(temp_df["振幅"], errors="coerce")
    temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"], errors="coerce")
    temp_df["涨跌额"] = pd.to_numeric(temp_df["涨跌额"], errors="coerce")
    temp_df["换手率"] = pd.to_numeric(temp_df["换手率"], errors="coerce")
    temp_df = temp_df[
        [
            "日期",
            "股票代码",
            "开盘",
            "收盘",
            "最高",
            "最低",
            "成交量",
            "成交额",
            "振幅",
            "涨跌幅",
            "涨跌额",
            "换手率",
        ]
    ]
    return temp_df


import math
from typing import List, Dict

import pandas as pd
import requests

from akshare.utils.tqdm import get_tqdm
def fetch_paginated_data(url: str, base_params: Dict, timeout: int = 15):
    """
    东方财富-分页获取数据并合并结果
    https://quote.eastmoney.com/f1.html?newcode=0.000001
    :param url: 股票代码
    :type url: str
    :param base_params: 基础请求参数
    :type base_params: dict
    :param timeout: 请求超时时间
    :type timeout: str
    :return: 合并后的数据
    :rtype: pandas.DataFrame
    """
    # 复制参数以避免修改原始参数
    params = base_params.copy()
    # 获取第一页数据，用于确定分页信息
    r = requests.post(url, data=params, timeout=timeout)
    print(r.text)
    data_json = r.json()
    # 计算分页信息
    per_page_num = len(data_json["data"]["diff"])
    total_page = math.ceil(data_json["data"]["total"] / per_page_num)
    # 存储所有页面数据
    temp_list = []
    # 添加第一页数据
    temp_list.append(pd.DataFrame(data_json["data"]["diff"]))
    # 获取进度条
    tqdm = get_tqdm()
    # 获取剩余页面数据
    # for page in tqdm(range(2, total_page + 1), leave=False):
    #     params.update({"pn": page})
    #     r = requests.post(url, data=params, timeout=timeout)
    #     print(r.text)
    #     data_json = r.json()
    #     inner_temp_df = pd.DataFrame(data_json["data"]["diff"])
    #     temp_list.append(inner_temp_df)
    
    for page in tqdm(range(2, total_page + 1), leave=False):
        params.update({"pn": page})
        r = requests.post(url, data=params, timeout=timeout)
        data_json = r.json()
        inner_temp_df = pd.DataFrame(data_json["data"]["diff"])
        temp_list.append(inner_temp_df)
    #
    # 合并所有数据
    temp_df = pd.concat(temp_list, ignore_index=True)
    temp_df["f3"] = pd.to_numeric(temp_df["f3"], errors="coerce")
    temp_df.sort_values(by=["f3"], ascending=False, inplace=True, ignore_index=True)
    temp_df.reset_index(inplace=True)
    temp_df["index"] = temp_df["index"].astype(int) + 1
    return temp_df

def stock_zh_a_spot_em() -> pd.DataFrame:
    """
    东方财富网-沪深京 A 股-实时行情
    https://quote.eastmoney.com/center/gridlist.html#hs_a_board
    :return: 实时行情
    :rtype: pandas.DataFrame
    """
    url = "https://82.push2.eastmoney.com/api/qt/clist/get"
    flist = []
    # for i in range(4000):
    #     flist.append(f'f{i}')
    # x= ','.join(flist)
    x = 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f22,f23,f24,f25,f26,f27,f28,f29,f30,f31,f32,f33,f34,f35,f36,f37,f38,f39,f40,f41,f42,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65,f66,f67,f68,f69,f70,f71,f72,f73,f74,f75,f76,f77,f78,f79,f80,f81,f82,f83,f84,f85,f86,f87,f88,f89,f90,f91,f92,f94,f95,f97,f98,f99,f100,f101,f146,f147,f102,f103,f104,f105,f106,f107,f108,f109,f110,f111,f112,f113,f114,f115,f116,f117,f118,f119,f120,f121,f122,f123,f124,f125,f126,f127,f128,f140,f141,f129,f130,f131,f132,f133,f134,f135,f136,f137,f138,f139,f142,f143,f144,f145,f148,f149,f152,f153,f154,f160,f161,f162,f163,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f193,f194,f195,f196,f197,f199,f200,f201,f202,f203,f204,f205,f206,f207,f208,f209,f210,f211,f212,f213,f214,f215,f216,f217,f218,f219,f220,f221,f222,f223,f225,f226,f227,f228,f229,f230,f231,f232,f233,f234,f235,f236,f237,f238,f239,f240,f241,f242,f243,f244,f245,f246,f247,f248,f249,f250,f251,f252,f253,f254,f255,f256,f257,f258,f259,f260,f261,f262,f263,f264,f265,f266,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f277,f278,f279,f280,f281,f282,f292,f293,f294,f295,f296,f297,f298,f299,f300,f301,f302,f303,f304,f305,f306,f307,f308,f309,f310,f311,f312,f313,f314,f315,f316,f317,f318,f319,f320,f321,f322,f323,f324,f325,f326,f327,f328,f329,f330,f331,f332,f333,f334,f335,f336,f337,f339,f340,f341,f342,f343,f344,f345,f346,f347,f348,f349,f350,f351,f352,f353,f354,f355,f356,f357,f358,f359,f360,f361,f362,f363,f364,f365,f366,f367,f368,f369,f370,f371,f372,f373,f374,f375,f376,f377,f378,f379,f380,f381,f382,f383,f384,f385,f386,f387,f388,f389,f390,f391,f392,f393,f394,f395,f396,f397,f398,f399,f400,f402,f403,f408,f409,f410,f411,f412,f413,f414,f415,f416,f417,f418,f419,f420,f421,f422,f423,f424,f425,f426,f427,f428,f429,f430,f431,f432,f433,f434,f435,f436,f437,f438,f439,f440,f441,f442,f443,f444,f445,f446,f447,f448,f449,f450,f451,f452,f453,f454,f455,f456,f457,f458,f459,f460,f461,f462,f463,f464,f465,f466,f467,f468,f469,f470,f471,f472,f473,f474,f475,f476,f477,f478,f479,f480,f481,f482,f484,f485,f486,f487,f488,f489,f490,f491,f492,f493,f494,f495,f496,f497,f498,f499,f500,f501,f502,f503,f600,f601,f602,f603,f604,f605,f606,f607,f608,f609,f610,f611,f612,f613,f614,f615,f616,f617,f624,f625,f626,f627,f628,f629,f1020,f1113,f1045,f1009,f1023,f1049,f1129,f1037,f1135,f1115,f1058,f1132,f1130,f1131,f1137,f1133,f1138,f2020,f2113,f2045,f2009,f2023,f2049,f2129,f2037,f2135,f2115,f2058,f2132,f2130,f2131,f2137,f2133,f2138,f3020,f3113,f3045,f3009,f3023,f3049,f3129,f3037,f3135,f3115,f3058,f3132,f3130,f3131,f3137,f3133,f3138'
    params = {
        "pn": "1",
        "pz": "1",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f12",
        "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
        "fields": f"{x}",
        # "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,"
        # "f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
    }
    # from akshare.utils.func import fetch_paginated_data
    temp_df = fetch_paginated_data(url, params)
    # temp_df.columns = [
    #     "index",
    #     "_",
    #     "最新价",
    #     "涨跌幅",
    #     "涨跌额",
    #     "成交量",
    #     "成交额",
    #     "振幅",
    #     "换手率",
    #     "市盈率-动态",
    #     "量比",
    #     "5分钟涨跌",
    #     "代码",
    #     "_",
    #     "名称",
    #     "最高",
    #     "最低",
    #     "今开",
    #     "昨收",
    #     "总市值",
    #     "流通市值",
    #     "涨速",
    #     "市净率",
    #     "60日涨跌幅",
    #     "年初至今涨跌幅",
    #     "-",
    #     "-",
    #     "-",
    #     "-",
    #     "-",
    #     "-",
    #     "-",
    # ]
    # temp_df.rename(columns={"index": "序号"}, inplace=True)
    # temp_df = temp_df[
    #     [
    #         "序号",
    #         "代码",
    #         "名称",
    #         "最新价",
    #         "涨跌幅",
    #         "涨跌额",
    #         "成交量",
    #         "成交额",
    #         "振幅",
    #         "最高",
    #         "最低",
    #         "今开",
    #         "昨收",
    #         "量比",
    #         "换手率",
    #         "市盈率-动态",
    #         "市净率",
    #         "总市值",
    #         "流通市值",
    #         "涨速",
    #         "5分钟涨跌",
    #         "60日涨跌幅",
    #         "年初至今涨跌幅",
    #     ]
    # ]
    # temp_df["最新价"] = pd.to_numeric(temp_df["最新价"], errors="coerce")
    # temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"], errors="coerce")
    # temp_df["涨跌额"] = pd.to_numeric(temp_df["涨跌额"], errors="coerce")
    # temp_df["成交量"] = pd.to_numeric(temp_df["成交量"], errors="coerce")
    # temp_df["成交额"] = pd.to_numeric(temp_df["成交额"], errors="coerce")
    # temp_df["振幅"] = pd.to_numeric(temp_df["振幅"], errors="coerce")
    # temp_df["最高"] = pd.to_numeric(temp_df["最高"], errors="coerce")
    # temp_df["最低"] = pd.to_numeric(temp_df["最低"], errors="coerce")
    # temp_df["今开"] = pd.to_numeric(temp_df["今开"], errors="coerce")
    # temp_df["昨收"] = pd.to_numeric(temp_df["昨收"], errors="coerce")
    # temp_df["量比"] = pd.to_numeric(temp_df["量比"], errors="coerce")
    # temp_df["换手率"] = pd.to_numeric(temp_df["换手率"], errors="coerce")
    # temp_df["市盈率-动态"] = pd.to_numeric(temp_df["市盈率-动态"], errors="coerce")
    # temp_df["市净率"] = pd.to_numeric(temp_df["市净率"], errors="coerce")
    # temp_df["总市值"] = pd.to_numeric(temp_df["总市值"], errors="coerce")
    # temp_df["流通市值"] = pd.to_numeric(temp_df["流通市值"], errors="coerce")
    # temp_df["涨速"] = pd.to_numeric(temp_df["涨速"], errors="coerce")
    # temp_df["5分钟涨跌"] = pd.to_numeric(temp_df["5分钟涨跌"], errors="coerce")
    # temp_df["60日涨跌幅"] = pd.to_numeric(temp_df["60日涨跌幅"], errors="coerce")
    # temp_df["年初至今涨跌幅"] = pd.to_numeric(
    #     temp_df["年初至今涨跌幅"], errors="coerce"
    # )
    return temp_df


import akshare as ak
if __name__ == "__main__":
    
    # df = stock_zh_a_hist(symbol='000001', start_date='20250418')
    # df = ak.stock_zh_a_spot_em()
    df = stock_zh_a_spot_em()
    print(df)
    
    # 获取今天日期作为文件名
    today_date = pd.Timestamp.now().strftime('%Y-%m-%d')
    # 创建csv目录
    import os; os.makedirs('./csv', exist_ok=True)
    # 保存为csv文件
    df.to_csv(f'./csv/{today_date}.csv', index=False)
    print(f"数据已保存到 ./csv/{today_date}.csv")
    
    
#%%
# import pandas as pd
# df = pd.read_csv('./csv/2025-04-20.csv')
# # 筛选出所有有数据的列
# non_empty_cols = [col for col in df.columns if not df[col].isnull().all()]
# # 打印列名
# print("有数据的列名：")
# for col in non_empty_cols:
#     print(col, end=',')

