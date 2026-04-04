import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import random
import re

def get_stock_list(max_count):
    """从 stocks.txt 中提取前 max_count 个股票代码"""
    file_path = 'stocks.txt'
    if not os.path.exists(file_path):
        print(f"❌ 找不到 {file_path}")
        return []
    
    try:
        # 自动识别空格或制表符分隔，跳过表头
        df = pd.read_csv(file_path, sep=r'\s+', encoding='utf-8')
        # 提取第一列 '代码'
        raw_codes = df.iloc[:, 0].tolist()
        
        # 清洗代码：提取数字部分
        clean_codes = [re.sub(r'\D', '', str(c)) for c in raw_codes if str(c).strip()]
        
        # 只取前 max_count 个
        selected_codes = clean_codes[:max_count]
        return selected_codes
    except Exception as e:
        print(f"❌ 读取文件出错: {e}")
        return []

def scrape_guba_batch():
    # 从环境变量获取控制参数
    max_stocks = int(os.getenv("MAX_STOCKS", "5"))   # 默认爬前5个
    start_page = int(os.getenv("START_PAGE", "1"))   # 起始页
    end_page = int(os.getenv("END_PAGE", "1"))       # 结束页（每只爬几页）

    stock_list = get_stock_list(max_stocks)
    if not stock_list:
        print("⚠️ 没有可爬取的股票代码")
        return

    print(f"🚀 任务开始 | 计划处理股票数: {len(stock_list)} | 每只爬取: {start_page}-{end_page}页")

    for index, code in enumerate(stock_list):
        all_data = []
        print(f"\n({index+1}/{len(stock_list)}) 正在抓取股票: {code}...")
        
        for page in range(start_page, end_page + 1):
            url = f"https://guba.eastmoney.com/list,{code}_{page}.html"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://guba.eastmoney.com/"
            }
            
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code != 200: break
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                items = soup.select('tr.listitem') or soup.select('div.articleh')
                
                page_count = 0
                for item in items:
                    title_tag = item.select_one('a[href*="news,"]')
                    if not title_tag: continue
                    
                    all_data.append({
                        "股票代码": code,
                        "页码": page,
                        "标题": title_tag.get_text(strip=True),
                        "时间": (item.select_one('.l5, .update').get_text(strip=True) if item.select_one('.l5, .update') else "")
                    })
                    page_count += 1
                
                print(f"  ✅ 第 {page} 页完成，获取 {page_count} 条")
                time.sleep(random.uniform(2, 3)) # 页间延迟
            except Exception as e:
                print(f"  ❌ 抓取第 {page} 页出错: {e}")
                break
        
        # 保存该股票的数据
        if all_data:
            df_res = pd.DataFrame(all_data)
            filename = f"Guba_{code}_p{start_page}-{end_page}.csv"
            df_res.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"  💾 已保存: {filename}")
        
        # 换股延迟，避免封IP
        if index < len(stock_list) - 1:
            wait = random.uniform(5, 8)
            print(f"☕ 休息 {wait:.1f} 秒后处理下一只...")
            time.sleep(wait)

if __name__ == "__main__":
    scrape_guba_batch()
