import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import random
from datetime import datetime

def get_guba_deep_scan(stock_code, max_page=500):
    code_num = "".join(filter(str.isdigit, stock_code))
    all_results = []
    seen_titles = set()

    # 第一招：增强伪装 - 准备多个不同的 User-Agent
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (AppleWebKit/537.36; KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edge/123.0.2420.81"
    ]

    now_str = datetime.now().strftime("%Y%m%d-%H%M")
    print(f"🚀 启动深度扫描 | 目标: {code_num} | 计划抓取: {max_page} 页")

    for page in range(1, max_page + 1):
        url = f"https://guba.eastmoney.com/list,{code_num}_{page}.html" if page > 1 else f"https://guba.eastmoney.com/list,{code_num}.html"
        
        # 每次请求随机选择一个 User-Agent
        headers = {
            "User-Agent": random.choice(ua_list),
            "Referer": "https://guba.eastmoney.com/",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"⚠️ 第 {page} 页访问受阻 (状态码: {response.status_code})")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('tr.listitem') or soup.select('div.articleh')
            
            if not items:
                print(f"🛑 第 {page} 页未发现内容。")
                break

            page_new_count = 0
            for item in items:
                title_tag = item.select_one('a[href*="news,"]')
                if not title_tag: continue
                
                title = title_tag.get_text(strip=True)
                if title not in seen_titles:
                    author_tag = item.select_one('.l4 a') or item.select_one('.nickname a')
                    author_id = author_tag.get_text(strip=True) if author_tag else "未知用户"
                    time_tag = item.select_one('.l5') or item.select_one('.update')
                    update_time = time_tag.get_text(strip=True) if time_tag else "未知时间"

                    all_results.append({
                        "
