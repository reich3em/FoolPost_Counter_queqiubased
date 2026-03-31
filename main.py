import requests
import pandas as pd
from datetime import datetime
import time
import os

class XueqiuSpider:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://xueqiu.com/"
        }
        self.session.get("https://xueqiu.com/", headers=self.headers)

    def fetch_comments(self, symbol, target_date):
        url = "https://xueqiu.com/query/v1/symbol/status/list.json"
        comments_list = []
        target_ts = datetime.strptime(target_date, "%Y-%m-%d").date()
        
        for page in range(1, 6): # 默认爬取前5页，防止被封
            params = {"count": 20, "symbol": symbol, "source": "all", "sort": "time", "page": page}
            resp = self.session.get(url, params=params, headers=self.headers)
            data = resp.json()
            
            for status in data.get('list', []):
                created_at = datetime.fromtimestamp(status['created_at'] / 1000)
                if created_at.date() == target_ts:
                    comments_list.append({"用户": status['user']['screen_name'], "内容": status['description'], "时间": created_at})
            
            time.sleep(2)
        return pd.DataFrame(comments_list)

if __name__ == "__main__":
    # --- 你可以在这里修改参数 ---
    STOCK_CODE = "SH600519"  # 贵州茅台
    TARGET_DAY = "2024-05-20" 
    # -------------------------
    
    spider = XueqiuSpider()
    result_df = spider.fetch_comments(STOCK_CODE, TARGET_DAY)
    
    # 创建结果文件夹
    os.makedirs("results", exist_ok=True)
    file_path = f"results/{STOCK_CODE}_{TARGET_DAY}.csv"
    result_df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"爬取完成！保存至: {file_path}，共 {len(result_df)} 条记录")
