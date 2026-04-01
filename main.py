import requests
from bs4 import BeautifulSoup # 注意：这里增加了依赖
import pandas as pd
import os
import time

def get_guba_html(stock_code):
    # 提取数字代码
    code_num = "".join(filter(str.isdigit, stock_code))
    # 网页版列表地址
    url = f"https://guba.eastmoney.com/list,{code_num}.html"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://guba.eastmoney.com/",
        "Cookie": "qgqp_b_id=123456" # 随便写点基础Cookie模拟真人
    }

    try:
        print(f"🕵️ 改用网页解析法 | 目标: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8' # 强制编码，防止乱码
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 东财最新的帖子列表通常在 class 为 'articleh' 的 div 里
            # 或者在 tr 标签里。这里我们寻找所有的列表项
            items = soup.select('.listitem') or soup.select('tr')
            
            processed_data = []
            print(f"找到候选行数: {len(items)}")

            for item in items:
                try:
                    # 尝试抓取标题和作者（东财网页结构经常微调，这里用选择器兼容）
                    title_node = item.select_one('.l3 a') or item.select_one('a[title]')
                    author_node = item.select_one('.l4 a') or item.select_one('.nickname')
                    
                    if title_node and author_node:
                        processed_data.append({
                            "标题": title_node.get_text(strip=True),
                            "作者": author_node.get_text(strip=True),
                            "链接": "https://guba.eastmoney.com" + title_node.get('href', '')
                        })
                except:
                    continue

            if processed_data:
                df = pd.DataFrame(processed_data)
                print(f"✅ 解析成功！提取到 {len(df)} 条帖子")
                print(df.head(5))
                df.to_csv("guba_data.csv", index=False, encoding='utf-8-sig')
            else:
                print("⚠️ 网页内容已拿到，但没解析出帖子，可能是结构变了。")
        else:
            print(f"❌ 网页请求依然失败，状态码: {response.status_code}")

    except Exception as e:
        print(f"💥 运行异常: {e}")

if __name__ == "__main__":
    get_guba_html(os.getenv("STOCK_CODE", "600900"))
