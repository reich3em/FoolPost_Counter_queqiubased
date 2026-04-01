import requests
import os
import pandas as pd
import time
import random

def get_snowball_comments(stock_code):
    # 1. 更加真实的浏览器身份标识 (User-Agent)
    # 模拟 Windows 电脑上的 Chrome 浏览器
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://xueqiu.com/S/{stock_code}",
        "Accept": "application/json, text/plain, */*"
    }
    
    # 创建一个 Session 对象，它会自动帮我们处理 Cookie
    session = requests.Session()
    
    try:
        # 第一步：先访问股票主页，诱导服务器给我们分发 Cookie
        print(f"--- 正在连接雪球网，准备爬取 {stock_code} ---")
        session.get(f"https://xueqiu.com/S/{stock_code}", headers=headers, timeout=10)
        
        # 第二步：模拟人工随机等待，避开简单的机器检测
        wait_time = random.uniform(2.1, 4.8) 
        print(f"☕ 模拟人类操作中... 随机等待 {wait_time:.2f} 秒")
        time.sleep(wait_time)
        
        # 第三步：请求真正的讨论列表接口
        # count=15 表示取最近的 15 条
        api_url = f"https://xueqiu.com/query/v1/symbol/status/list.json?symbol={stock_code}&count=15&source=user"
        
        response = session.get(api_url, headers=headers, timeout=10)
        print(f"服务器响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            json_data = response.json()
            comment_list = json_data.get('list', [])
            
            if not comment_list:
                print("⚠️ 没拿到讨论数据。可能原因：该股票近期无讨论，或被雪球反爬虫拦截。")
                # 打印前100个字符看看服务器
