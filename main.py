import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime

def get_guba_deep_scan(stock_code, max_page=500):
    code_num = "".join(filter(str.isdigit, stock_code))
    all_results = []
    seen_titles = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://guba.eastmoney.com/",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    # 获取当前时间用于文件名
    now_str = datetime.now().strftime("%Y%m%d-%H%M")
    
    print(f"🚀 启动超级扫描 | 目标: {code_num} | 深度上限: {max_page} 页")

    for page in range(1, max_page + 1):
        url = f"https://guba.eastmoney.com/list,{code_num}_{page}.html" if page > 1 else f"https://guba.eastmoney.com/list,{code_num}.html"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"⚠️ 第 {page} 页访问受阻 (状态码: {response.status_code})")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('tr.listitem') or soup.select('div.articleh')
            
            if not items:
                print(f"🛑 第 {page} 页未发现内容，可能已达东财显示极限。")
                break

            page_new_count = 0
            for item in items:
                title_tag = item.select_one('a[href*="news,"]')
                if not title_tag: continue
                
                title = title_tag.get_text(strip=True)
                if len(title) < 4: continue

                # 记录总条数，但不一定每一条都存（去重）
                if title not in seen_titles:
                    author_tag = item.select_one('.l4 a') or item.select_one('.nickname a')
                    author_id = author_tag.get_text(strip=True) if author_tag else "未知用户"
                    time_tag = item.select_one('.l5') or item.select_one('.update')
                    update_time = time_tag.get_text(strip=True) if time_tag else "未知时间"

                    all_results.append({
                        "股票代码": code_num,
                        "标题": title,
                        "作者ID": author_id,
                        "最后更新": update_time
                    })
                    seen_titles.add(title)
                    page_new_count += 1

            print(f"✅ 第 {page}/{max_page} 页: 新增 {page_new_count} 条")
            
            # 如果连续 5 页都没有新增，说明全是重复内容，提前结束以节省资源
            if page_new_count == 0 and page > 50:
                print("📝 检测到连续重复内容，判定已抓取完毕。")
                break

            time.sleep(2.2) # 500页量大，稍微增加一点延迟保护IP

        except Exception as e:
            print(f"💥 第 {page} 页错误: {e}")
            break

    if all_results:
        df = pd.DataFrame(all_results)
        # 格式：代码-日期-时间.csv
        output_file = f"{code_num}-{now_str}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n✨ 任务完成！总抓取: {len(df)} 条 | 文件: {output_file}")
    else:
        print("❌ 未获得有效数据")

if __name__ == "__main__":
    stock = os.getenv("STOCK_CODE", "600900")
    # 这里确保传参是 500
    get_guba_deep_scan(stock, max_page=500)
