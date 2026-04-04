import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import random
from datetime import datetime

def scrape_guba_range():
    # 从 GitHub Actions 的输入中获取参数
    stock_code = os.getenv("STOCK_CODE", "300059")
    start_page = int(os.getenv("START_PAGE", "1"))
    end_page = int(os.getenv("END_PAGE", "10"))
    
    code_num = "".join(filter(str.isdigit, stock_code))
    all_results = []
    
    # 第一招：增强伪装（随机请求头）
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    ]

    print(f"🚀 [main2] 启动 | 股票: {code_num} | 页码范围: {start_page} -> {end_page}")

    for page in range(start_page, end_page + 1):
        # 构造带有页码偏移的 URL
        url = f"https://guba.eastmoney.com/list,{code_num}_{page}.html"
        
        headers = {
            "User-Agent": random.choice(ua_list),
            "Referer": "https://guba.eastmoney.com/"
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"❌ 第 {page} 页请求失败 (状态码: {response.status_code})")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('tr.listitem') or soup.select('div.articleh')
            
            if not items:
                print(f"⚠️ 第 {page} 页没有数据")
                continue

            for item in items:
                title_tag = item.select_one('a[href*="news,"]')
                if not title_tag: continue
                
                all_results.append({
                    "页码": page,
                    "标题": title_tag.get_text(strip=True),
                    "作者": (item.select_one('.l4 a, .nickname a').get_text(strip=True) if item.select_one('.l4 a, .nickname a') else "未知"),
                    "时间": (item.select_one('.l5, .update').get_text(strip=True) if item.select_one('.l5, .update') else "未知")
                })
            
            print(f"✅ 第 {page} 页抓取完成")

            # 第二招：拉长随机延迟
            time.sleep(random.uniform(3, 4))

        except Exception as e:
            print(f"💥 错误: {e}")
            break

    if all_results:
        df = pd.DataFrame(all_results)
        # 生成带时间戳和页码范围的文件名
        file_tag = datetime.now().strftime("%H%M")
        filename = f"Data_{code_num}_p{start_page}-{end_page}_{file_tag}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✨ 任务成功！文件: {filename}")

if __name__ == "__main__":
    scrape_guba_range()
