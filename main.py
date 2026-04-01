import requests
import os
import pandas as pd
import time
import random

def get_snowball_comments(stock_code):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://xueqiu.com/S/{stock_code}",
        "Accept": "application/json, text/plain, */*"
    }
    
    session = requests.Session()
    
    try:
        print(f"--- 正在连接雪球网 ({stock_code}) ---")
        # 建立 Session
        session.get(f"https://xueqiu.com/S/{stock_code}", headers=headers, timeout=10)
        
        # 随机等待：2到5秒之间的小数
        wait_time = random.uniform(2.0, 5.0)
        print(f"☕ 模拟人工操作，随机等待 {wait_time:.2f} 秒...")
        time.sleep(wait_time)
        
        # 请求接口
        api_url = f"https://xueqiu.com/query/v1/symbol/status/list.json?symbol={stock_code}&count=15&source=user"
        response = session.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            comment_list = response.json().get('list', [])
            
            if not comment_list:
                print("⚠️ 接口返回成功但没有内容，可能是被反爬拦截。")
                print(f"返回样板: {response.text[:100]}")
                return

            processed_data = []
            for item in comment_list:
                user_name = item.get("user", {}).get("screen_name", "匿名")
                raw_text = item.get("text", "") or item.get("description", "")
                # 清洗 HTML
                clean_text = raw_text.replace("<br/>", " ").replace("</p>", "").replace("<p>", "")
                
                processed_data.append({
                    "作者": user_name,
                    "内容": clean_text
                })
            
            df = pd.DataFrame(processed_data)
            print("\n--- 抓取成功！预览前3条 ---")
            print(df.head(3))
            
            # 保存
            file_name = f"{stock_code}_comments.csv"
            df.to_csv(file_name, index=False, encoding='utf-8-sig')
            print(f"\n✅ 已存至: {file_name}")
            
        else:
            print(f"❌ 服务器响应失败，状态码: {response.status_code}")

    except Exception as e:
        print(f"❌ 运行中发生错误: {e}")

if __name__ == "__main__":
    # 获取环境变量或默认值
    stock = os.getenv("STOCK_CODE", "SH600900")
    get_snowball_comments(stock)
