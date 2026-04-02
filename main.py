import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

def get_guba_deep_scan(stock_code, max_page=50):
    # 提取纯数字代码
    code_num = "".join(filter(str.isdigit, stock_code))
    all_results = []
    seen_titles = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "https://guba.eastmoney.com/",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    print(f"🚀 开始深度扫描 | 目标: {code_num} | 计划爬取: {max_page} 页")

    for page in range(1, max_page + 1):
        # 构建翻页 URL
        if page == 1:
            url = f"https://guba.eastmoney.com/list,{code_num}.html"
        else:
            url = f"https://guba.eastmoney.com/list,{code_num}_{page}.html"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"⚠️ 第 {page} 页访问受阻 (状态码: {response.status_code})，停止翻页。")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # 同时兼容多种可能的 HTML 结构
            items = soup.select('tr.listitem') or soup.select('div.articleh')
            
            if not items:
                print(f"🛑 第 {page} 页未发现内容，可能已达末尾。")
                break

            page_count = 0
            for item in items:
                # 1. 标题提取 (排除置顶/广告/无效链接)
                title_tag = item.select_one('a[href*="news,"]')
                if not title_tag: continue
                
                title = title_tag.get_text(strip=True)
                # 过滤掉短标题和重复项
                if len(title) < 4 or title in seen_titles: continue

                # 2. 作者 ID
                author_tag = item.select_one('.l4 a') or item.select_one('.nickname a')
                author_id = author_tag.get_text(strip=True) if author_tag else "未知用户"

                # 3. 最后更新时间
                time_tag = item.select_one('.l5') or item.select_one('.update')
                update_time = time_tag.get_text(strip=True) if time_tag else "未知时间"

                all_results.append({
                    "股票代码": code_num,
                    "标题": title,
                    "作者ID": author_id,
                    "最后更新": update_time
                })
                seen_titles.add(title)
                page_count += 1

            print(f"✅ 第 {page}/{max_page} 页处理完成，新增 {page_count} 条记录。")
            
            # 💡 核心：模仿人类行为的 2.1s 延迟
            if page < max_page:
                time.sleep(2.1)

        except Exception as e:
            print(f"💥 第 {page} 页发生错误: {e}")
            break

    # 保存结果
    if all_results:
        df = pd.DataFrame(all_results)
        output_file = f"guba_{code_num}_deep.csv"
        # 使用 utf-8-sig 确保 Excel 打开中文不乱码
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n✨ 深度扫描任务结束！")
        print(f"📊 总计抓取: {len(df)} 条数据")
        print(f"💾 文件已保存: {output_file}")
    else:
        print("❌ 任务失败，未获得任何有效数据。")

if __name__ == "__main__":
    # 从 Actions 传入的环境变量获取代码
    stock = os.getenv("STOCK_CODE", "600900")
    get_guba_deep_scan(stock, max_page=50)
