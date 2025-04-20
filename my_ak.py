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
    
    import asyncio
    import aiohttp

    async def fetch_page(session, url, params, page):
        params.update({"pn": page})
        async with session.post(url, data=params, timeout=15) as response:
            data = await response.json()
            return pd.DataFrame(data["data"]["diff"])

    async def fetch_all_pages():
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_page(session, url, params, page) for page in range(1, total_page + 1)]
            for future in tqdm(asyncio.as_completed(tasks), total=total_page, leave=False):
                inner_temp_df = await future
                temp_list.append(inner_temp_df)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fetch_all_pages())
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
    for i in range(10001):
        flist.append(f'f{i}')
    x= ','.join(flist)
    params = {
        "pn": "1",
        "pz": "100",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f12",
        "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
        "fields": f"{x}",
    }
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
    df = ak.stock_zh_a_spot_em()
    print(df)
    
    # 获取今天日期作为文件名
    today_date = pd.Timestamp.now().strftime('%Y-%m-%d')
    # 创建csv目录
    import os; os.makedirs('./csv', exist_ok=True)
    # 保存为csv文件
    df.to_csv(f'./csv/{today_date}.csv', index=False)
    print(f"数据已保存到 ./csv/{today_date}.csv")
