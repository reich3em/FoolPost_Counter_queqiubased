import requests
import sys
import os

def get_snowball_comments(stock_code):
    # 模拟浏览器头，雪球需要这个，否则会拦截
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://xueqiu.com"
    }
    
    # 1. 获取 Session（雪球需要先访问主页拿 Cookie）
    session = requests.Session()
    session.get("https://xueqiu.com", headers=headers)
    
    # 2. 爬取讨论（这是一个示例 URL，雪球的 API 可能随时间变化）
    url = f"https://xueqiu.com/query/v1/symbol/status/list.json?symbol={stock_code}&count=10&source=user"
    
    response = session.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"--- {stock_code} 的最新讨论 ---")
        for comment in data.get('list', []):
            print(f"- {comment.get('text')[:50]}...") # 只打印前50个字
    else:
        print(f"爬取失败，状态码：{response.status_code}")

if __name__ == "__main__":
    # 从 GitHub Actions 的环境变量中读取输入的股票代码
    code = os.getenv("STOCK_CODE")
    if not code:
        # 如果环境变量没拿到，就看命令行参数
        code = sys.argv[1] if len(sys.argv) > 1 else "SH000001"
    
    get_snowball_comments(code)
