import requests
import os
import pandas as pd

def get_snowball_comments(stock_code):
    # 模拟真实浏览器的身份信息
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://xueqiu.com"
    }
    
    # 使用 Session 保持状态
    session = requests.Session()
    # 1. 先访问首页，获取必要的 Cookie
    session.get("https://xueqiu.com", headers=headers)
    
    # 2. 爬取指定股票的讨论接口
    # 注意：count=20 表示获取最近20条
    url = f"https://xueqiu.com/query/v1/symbol/status/list.json?symbol={stock_code}&count=20&source=user"
    
    print(f"正在抓取 {stock_code} 的讨论...")
    response = session.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json().get('list', [])
        if not data:
            print("❌ 未获取到讨论内容，可能是代码输入错误或 API 变动。")
            return
            
        # 整理数据
        comments = []
        for item in data:
            comments.append({
                "时间": item.get("created_at"),
                "内容": item.get("description"), # description 通常包含纯文本
                "作者": item.get("user", {}).get("screen_name")
            })
            
        df = pd.DataFrame(comments)
        # 打印在日志里让你直接看到
        for index, row in df.head(10).iterrows():
            print(f"[{row['作者']}]: {row['内容'][:100]}...\n")
            
        # 存成 CSV 文件
        df.to_csv(f"{stock_code}_data.csv", index=False, encoding='utf-8-sig')
        print(f"✅ 成功！数据已保存至 {stock_code}_data.csv")
    else:
        print(f"❌ 抓取失败，错误码：{response.status_code}")

if __name__ == "__main__":
    # 优先从环境变量读取 GitHub 输入的代码
    stock = os.getenv("STOCK_CODE", "SH600900")
    get_snowball_comments(stock)
