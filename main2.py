import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import random
import re
from datetime import datetime

def get_stock_list(max_count):
    """从 stocks.txt 中提取前 max_count 个股票代码"""
    file_path = 'stocks.txt'
    if not os.path.exists(file_path):
        print(f"❌ 找不到 {file_path}")
        return []
    
    try:
        # 自动识别空格或制表符分隔，并跳过表头
        df = pd.read_csv(file_path, sep=r'\s+', encoding='utf-8')
        # 提取第一列，通常是'代码'
        raw_codes = df.iloc[:, 0].tolist()
        
        # 清洗代码：只保留数字部分
        clean_codes = [re.sub(r'\D', '', str(c)) for c in raw_codes if str(c).strip()]
        
        # 只取前 max_count 个
        return clean_codes[:max_count]
    except Exception as e:
        print(f"❌ 读取文件出错: {e}")
        return []

def scrape_guba_batch():
    # 获取环境变量
    max_stocks = int(os.getenv("MAX_STOCKS", "5"))
    start_page = int(os.getenv("START_PAGE", "1"))
    end_page = int(os.getenv("END_PAGE", "2"))

    stock_list = get_stock_list(max_stocks)
    if not stock_list:
        print("⚠️ 没有可爬取的股票代码")
        return

    # 🌟 核心：建立一个总列表，存放所有股票的所有数据
    all_stocks_data = []

    print(f"🚀 批量任务启动 | 目标股票数: {len(stock_list)} | 范围: {start_page}-{end_page}页")

    for index, code in enumerate(stock_list):
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
                
                count = 0
                for item in items:
                    title_tag = item.select_one('a[href*="news,"]')
                    if not title_tag: continue
                    
                    # 🌟 将单条数据加入总列表
                    all_stocks_data.append({
                        "股票代码": code,
                        "页码": page,
                        "标题": title_tag.get_text(strip=True),
                        "时间": (item.select_one('.l5, .update').get_text(strip=True) if item.select_one('.l5, .update') else "")
                    })
                    count += 1
                
                print(f"  ✅ 第 {page} 页抓取成功 ({count}条)")
                time.sleep(random.uniform(1.5, 3)) # 适当减少延迟提高效率
            except Exception as e:
                print(f"  ❌ 抓取出错: {e}")
                break
        
        # 换股休息，保护IP
        if index < len(stock_list) - 1:
            time.sleep(random.uniform(3, 5))

    # 🌟 循环结束后，统一保存为一个文件
    if all_stocks_data:
        df_final = pd.DataFrame(all_stocks_data)
        # 生成带时间戳的文件名，防止覆盖
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"Guba_Batch_Result_{timestamp}.csv"
        
        df_final.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n✨ 任务全部完成！总计 {len(all_stocks_data)} 条数据已写入: {filename}")
    else:
        print("📁 未抓取到任何数据。")

if __name__ == "__main__":
    scrape_guba_batch()
