import requests
import os
import pandas as pd
import time
import random

def get_snowball_comments(stock_code):
    # 模拟更全面的浏览器头部
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Host": "xueqiu.com",
        "Connection": "keep-alive"
    }
    
    # 使用 session 自动管理 Cookie
    session = requests.Session()
    
    try:
        print(f"--- 尝试绕过拦截，正在连接雪球 ({stock_code}) ---")
        
        # 1. 模拟打开雪球首页获取基础 Cookie
        session.get("https://xueqiu.com/", headers=headers, timeout=10)
        
        # 2. 模拟进入股票详情页
        detail_url = f"https://xueqiu.com/S/{stock_code}"
        session.get(detail_url, headers=headers, timeout=10)
        
        # 3. 随机等待，模拟人类阅读
        wait_time = random.uniform(3.5, 6.2)
        print(f"☕ 正在解析页面数据，随机等待 {wait_time:.2f} 秒...")
        time.sleep(wait_time)
        
        # 4. 更新 API 请求的 Headers (关键：需要增加 Referer)
        api_headers = headers.copy()
        api_headers["Referer"] = detail_url
        api_headers["Accept"] = "application/json, text/plain, */*"
        
        api_url = f"https://xueqiu.com/query/v1/symbol/status/list.json?symbol={stock_code}&count=15&source=user"
        
        response = session.get(api_url, headers=api_headers, timeout=10)
        
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("success") is True:
                comment_list = res_json.get('list', [])
                
                processed_data = []
                for item in comment_list:
                    user_name = item.get("user", {}).get("screen_name", "匿名")
                    raw_text = item.get("text", "") or item.get("description", "")
                    clean_text = raw_text.replace("<br/>", " ").replace("</p>", "").replace("<p>", "")
                    processed_data.append({"作者": user_name, "内容": clean_text})
                
                df = pd.DataFrame(processed_data)
                print(f"✅ 成功抓取到 {len(df)} 条讨论！")
                print(df.head(3))
                
                df.to_csv(f"{stock_code}_comments.csv", index=False, encoding='utf-8-sig')
            else:
                print(f"❌ API 拒绝访问。错误码: {res_json.get('code')}")
                print(f"服务器回复: {response.text}")
        else:
            print(f"❌ 网络请求失败，状态码: {response.status_code}")

    except Exception as e:
        print(f"❌ 程序崩溃: {e}")

if __name__ == "__main__":
    stock = os.getenv("STOCK_CODE", "SH600900")
    get_snowball_comments(stock)
