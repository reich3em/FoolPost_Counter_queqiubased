import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import re

def get_guba_ultra(stock_code, max_page=50):
    code_num = "".join(filter(str.isdigit, stock_code))
    all_results = []
    
    # 模拟真实 Chrome 浏览器的完整请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": f"https://guba.eastmoney.com/list,{code_num}.html",
        "Connection": "keep-alive"
    }

    session = requests.Session() # 使用 Session 自动处理可能的 Cookie

    for page in range(1, max_page + 1):
        url = f"https://guba.eastmoney.com/list,{code_num}_{page}.html" if page > 1 else f"https://guba.eastmoney.com/list,{code_num}.html"
        
        try:
            res = session.get(url, headers=headers, timeout=15)
            res.encoding = 'utf-8'
            
            # 如果被拦截，打印部分源码便于调试
            if "访问被拒绝" in res.text or "验证码" in res.text:
                print(f"❌ 第 {page} 页触发了反爬验证，请稍后再试。")
                break

            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 兼容性更强的定位方式：直接找包含 news, 的链接
            items = soup.select('tr.listitem') or soup.select('.articleh') or soup.select('li')
            
            page_count = 0
            for item in items:
                try:
                    title_tag = item.select_one('a[href*="news,"]')
                    if not title_tag: continue
                    
                    title = title_tag.get_text(strip=True)
                    read = item.select_one('.l1').get_text(strip=True) if item.select_one('.l1') else "0"
                    comment = item.select_one('.l2').get_text(strip=True) if item.select_one('.l2') else "0"
                    author_a = item.select_one('.l4 a') or item.select_one('.nickname')
                    author_name = author_a.get_text(strip=True) if author_a else "未知"
                    update_time = item.select_one('.l5').get_text(strip=True) if item.select_one('.l5') else "-"
                    
                    # 提取 UID
                    author_uid = "N/A"
                    if author_a and author_a.has_attr('href'):
                        uid_match = re.search(r'/user/(\d+)', author_a['href'])
                        author_uid = uid_match.group(1) if uid_match else "N/A"

                    all_results.append({
                        "阅读": read, "评论": comment, "标题": title, 
                        "作者": author_name, "作者ID": author_uid, "最后更新": update_time
                    })
                    page_count += 1
                except: continue

            print(f"✅ 第 {page} 页: 抓取 {page_count} 条")
            if page_count == 0 and page == 1:
                print("⚠️ 警告：第一页就没抓到数据，可能是解析器失效了。")
            
            time.sleep(2.1)

        except Exception as e:
            print(f"❌ 出错: {e}")
            break

    if all_results:
        df = pd.DataFrame(all_results)
        output_file = f"guba_{code_num}_pro.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"📊 成功生成文件: {output_file}，共 {len(df)} 行")
    else:
        print("💀 依然没有任何数据，建议检查东方财富网是否改版。")

if __name__ == "__main__":
    stock = os.getenv("STOCK_CODE", "300059")
    get_guba_ultra(stock, max_page=50)
