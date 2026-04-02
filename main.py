import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import re

def get_guba_pro_plus(stock_code, max_page=50):
    code_num = "".join(filter(str.isdigit, stock_code))
    all_results = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": f"https://guba.eastmoney.com/list,{code_num}.html"
    }

    print(f"🚀 启动全字段爬虫 | 目标: {code_num} | 深度: {max_page} 页")

    for page in range(1, max_page + 1):
        url = f"https://guba.eastmoney.com/list,{code_num}_{page}.html" if page > 1 else f"https://guba.eastmoney.com/list,{code_num}.html"
        
        try:
            res = requests.get(url, headers=headers, timeout=15)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 定位数据行
            items = soup.find_all('tr', class_='listitem') or soup.find_all('div', class_='articleh')
            
            if not items:
                print(f"🛑 第 {page} 页未发现数据，可能已达上限。")
                break

            page_count = 0
            for item in items:
                try:
                    # 1. 阅读 (.l1) & 评论 (.l2)
                    read = item.select_one('.l1').get_text(strip=True) if item.select_one('.l1') else "0"
                    comment = item.select_one('.l2').get_text(strip=True) if item.select_one('.l2') else "0"
                    
                    # 2. 帖子类型 (.l3 em) - 用于过滤新闻/公告
                    type_tag = item.select_one('.l3 em')
                    post_type = type_tag.get_text(strip=True) if type_tag else "讨论"
                    
                    # 3. 标题 (.l3 a)
                    title_tag = item.select_one('.l3 a[href*="news,"]')
                    if not title_tag: continue
                    title = title_tag.get_text(strip=True)
                    
                    # 4. 作者昵称 & UID (信号源追踪)
                    author_a = item.select_one('.l4 a')
                    author_name = author_a.get_text(strip=True) if author_a else "未知"
                    
                    # 从 href 中提取 UID (例如 /user/1234567890)
                    author_uid = "N/A"
                    if author_a and 'href' in author_a.attrs:
                        uid_match = re.search(r'/user/(\d+)', author_a['href'])
                        if uid_match:
                            author_uid = uid_match.group(1)

                    # 5. 最后更新 (.l5)
                    update_time = item.select_one('.l5').get_text(strip=True) if item.select_one('.l5') else "-"

                    # 过滤表头行
                    if "作者" in author_name or "标题" in title: continue

                    all_results.append({
                        "类型": post_type,
                        "阅读": read,
                        "评论": comment,
                        "标题": title,
                        "作者": author_name,
                        "作者ID": author_uid,
                        "最后更新": update_time
                    })
                    page_count += 1
                except:
                    continue

            print(f"✅ 第 {page}/{max_page} 页: 抓取 {page_count} 条")
            
            # 严格遵守 2.1s 翻页延迟
            if page < max_page:
                time.sleep(2.1)

        except Exception as e:
            print(f"❌ 运行异常: {e}")
            break

    if all_results:
        df = pd.DataFrame(all_results)
        # 按照逻辑排序：类型、热度、内容、身份、时间
        df = df[["类型", "阅读", "评论", "标题", "作者", "作者ID", "最后更新"]]
        
        output_file = f"guba_{code_num}_pro.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n💎 深度挖掘完成！数据量: {len(df)}")
        print(f"📂 结果文件: {output_file}")
    else:
        print("⚠️ 未能获取有效数据，请检查网络或页面结构。")

if __name__ == "__main__":
    stock = os.getenv("STOCK_CODE", "600900")
    get_guba_pro_plus(stock, max_page=50)
