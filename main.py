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

    # 第一招：随机请求头
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
    ]

    now_str = datetime.now().strftime("%Y%m%d-%H%M")
    print(f"🚀 启动深度扫描 | 目标: {code_num} | 计划抓取: {max_page} 页")

    for page in range(1, max_page + 1):
        url = f"https://guba.eastmoney.com/list,{code_num}_{page}.html" if page > 1 else f"https://guba.eastmoney.com/list,{code_num}.html"
        
        headers = {
            "User-Agent": random.choice(ua_list),
            "Referer": "https://guba.eastmoney.com/",
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"⚠️ 第 {page} 页无法访问，状态码: {response.status_code}")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('tr.listitem') or soup.select('div.articleh')
            
            if not items:
                print(f"🛑 第 {page} 页没有抓到内容。")
                break

            page_new_count = 0
            for item in items:
                title_tag = item.select_one('a[href*="news,"]')
                if not title_tag: continue
                
                title = title_tag.get_text(strip=True)
                if title not in seen_titles:
                    author_tag = item.select_one('.l4 a, .nickname a')
                    author_id = author_tag.get_text(strip=True) if author_tag else "未知"
                    time_tag = item.select_one('.l5, .update')
                    update_time = time_tag.get_text(strip=True) if time_tag else "未知"

                    all_results.append({
                        "股票代码": code_num,
                        "标题": title,
                        "作者ID": author_id,
                        "最后更新": update_time
                    })
                    seen_titles.add(title)
                    page_new_count += 1

            print(f"✅ 第 {page} 页: 新增 {page_new_count} 条 (累计: {len(all_results)})")
            
            # 如果连续多页无新内容，判定已到底部
            if page_new_count == 0 and page > 40:
                print("📝 后面都是重复内容，抓取结束。")
                break

            # 第二招：拉长随机延迟
            time.sleep(random.uniform(3, 4))

        except Exception as e:
            print(f"💥 运行异常: {e}")
            break

    if all_results:
        df = pd.DataFrame(all_results)
        output_file = f"{code_num}-{now_str}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n✨ 成功保存文件: {output_file}")
    else:
        print("❌ 未能保存任何数据")

if __name__ == "__main__":
    stock = os.getenv("STOCK_CODE", "300059")
    get_guba_deep_scan(stock, max_page=500)
