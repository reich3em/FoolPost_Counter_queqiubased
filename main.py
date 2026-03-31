import requests
import pandas as pd
from datetime import datetime
import time
import os
import sys

# 关键修改：从 GitHub 的环境变量里读取你输入的参数
# 如果读不到（本地运行），就使用默认值
STOCK_CODE = os.getenv("STOCK_CODE", "SH600519")
TARGET_DAY = os.getenv("TARGET_DAY", "2024-05-20")

class XueqiuSpider:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://xueqiu.com/"
        }
        # 激活 Session
        self.session.get("https://xueqiu.com/", headers=self.headers)

    def fetch_comments(self, symbol, target_date):
        url = "https://xueqiu.com/query/v1/symbol/status/list.json"
        comments_list = []
        try:
            target_ts = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            print(f"日期格式错误: {target_date}，请输入 YYYY-MM-DD 格式")
            return pd.DataFrame()

        print(f"开始爬取 {symbol} 在 {target_date} 的发言...")
        
        # 爬取前10页（雪球每页20条）
        for page in range(1, 11):
            params = {"count": 20, "symbol": symbol, "source": "all", "sort": "time", "page": page}
            resp = self.session.get(url, params=params, headers=self.headers)
            
            if resp.status_code != 200:
                print(f"请求失败，状态码：{resp.status_code}")
                break
                
            data = resp.json()
            items = data.get('list', [])
            if not items:
                break
            
            for status in items:
                created_at = datetime.fromtimestamp(status['created_at'] / 1000)
                post_date = created_at.date()
                
                if post_date == target_ts:
                    comments_list.append({
                        "用户": status['user']['screen_name'],
                        "内容": status['description'],
                        "时间": created_at
                    })
                elif post_date < target_ts:
                    # 时间已经早于目标日期，提前结束
                    return pd.DataFrame(comments_list)
            
            print(f"已扫描第 {page} 页...")
            time.sleep(2)
            
        return pd.DataFrame(comments_list)

if __name__ == "__main__":
    spider = XueqiuSpider()
    result_df = spider.fetch_comments(STOCK_CODE, TARGET_DAY)
    
    if not result_df.empty:
        os.makedirs("results", exist_ok=True)
        file_path = f"results/{STOCK_CODE}_{TARGET_DAY}.csv"
        result_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"✅ 成功！保存至: {file_path}，共统计到 {len(result_df)} 条发言")
    else:
        print("❌ 未发现指定日期的发言，请检查代码或日期是否有误。")
