import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re

def get_guba_robust(stock_code):
    # 兼容处理输入，提取纯数字
    code_num = "".join(filter(str.isdigit, stock_code))
    url = f"https://guba.eastmoney.com/list,{code_num}.html"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://guba.eastmoney.com/",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    try:
        print(f"📡 正在探测战场 | 目标股票: {code_num}")
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 策略：直接抓取所有包含 "news,代码" 的超链接，这是帖子的固定特征
            # 链接示例: /news,600900,1445678.html
            pattern = re.compile(f'/news,{code_num},\\d+\\.html')
            links = soup.find_all('a', href=pattern)
            
            results = []
            seen_titles = set() # 去重

            for link in links:
                title = link.get_text(strip=True)
                href = link.get('href')
                
                # 过滤掉太短的标题（比如“回复”、“更多”）
                if len(title) > 5 and title not in seen_titles:
                    # 尝试寻找同一行内的阅读数/评论数 (通常在父节点的父节点里)
                    parent_text = link.parent.parent.get_text("|", strip=True)
                    # 简单切分获取大致数据
                    parts = parent_text.split("|")
                    
                    results.append({
                        "标题": title,
                        "链接": "https://guba.eastmoney.com" + href,
                        "大致预览": parent_text[:50] # 保留原始行数据供参考
                    })
                    seen_titles.add(title)

            if results:
                df = pd.DataFrame(results)
                print(f"🎊 抓取成功！有效帖子数: {len(df)}")
                print(df[['标题']].head(10))
                
                output_file = f"guba_{code_num}.csv"
                df.to_csv(output_file, index=False, encoding='utf-8-sig')
                print(f"💾 数据已存入: {output_file}")
            else:
                # 如果还是没找到，打印一部分源码辅助排查
                print("⚠️ 未能提取到链接，HTML 结构可能已通过 JS 混淆。")
                print("源码片段预览:", response.text[:500])
        else:
            print(f"❌ 访问失败，状态码: {response.status_code}")

    except Exception as e:
        print(f"💥 运行异常: {e}")

if __name__ == "__main__":
    stock = os.getenv("STOCK_CODE", "600900")
    get_guba_robust(stock)
