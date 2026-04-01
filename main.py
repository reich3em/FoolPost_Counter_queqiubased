import requests
import re
import json
import pandas as pd
import os
import time
import random

def get_eastmoney_data(stock_code):
    # 提取数字代码，例如从 "SH600900" 提取 "600900"
    code_num = re.findall(r'\d+', stock_code)[0]
    
    # 东财股吧分页接口
    # p=1 表示第一页，ps=30 表示每页30条
    url = f"https://guba.eastmoney.com/interface/Getter.aspx?s=bar&name={code_num}&type=1&p=1&ps=30"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://guba.eastmoney.com/list,{code_num}.html",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }

    try:
        print(f"🚀 开始驾驭东方财富股吧 | 目标代码: {code_num}")
        
        # 模拟随机延迟，避免被识别为暴力爬虫
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # 清洗可能的 JSONP 包装
            raw_text = response.text.strip()
            # 如果返回的是 jQuery123({...}) 格式，提取括号内的内容
            json_str = re.search(r'\{.*\}', raw_text)
            
            if json_str:
                data = json.loads(json_str.group())
                if 're' in data and data['re'] is not None:
                    post_list = data['re']
                    processed = []
                    for post in post_list:
                        processed.append({
                            "阅读": post.get("readcount"),
                            "评论": post.get("replycount"),
                            "标题": post.get("title"),
                            "作者": post.get("nickname"),
                            "最后更新": post.get("update_time"),
                            "链接": f"https://guba.eastmoney.com/news,{code_num},{post.get('post_id')}.html"
                        })
                    
                    df = pd.DataFrame(processed)
                    print(f"✅ 抓取成功！获取到 {len(df)} 条最新动态。")
                    
                    # 打印前 5 条预览
                    print("-" * 30)
                    print(df[['标题', '作者']].head(5))
                    print("-" * 30)
                    
                    # 保存 CSV
                    output_file = "guba_data.csv"
                    df.to_csv(output_file, index=False, encoding='utf-8-sig')
                    print(f"💾 数据已存入: {output_file}")
                else:
                    print("⚠️ 接口返回成功但没有帖子数据，可能该股较冷门或触发了频率限制。")
            else:
                print(f"❌ 无法解析返回数据格式: {raw_text[:100]}")
        else:
            print(f"❌ 请求失败，HTTP 状态码: {response.status_code}")

    except Exception as e:
        print(f"💥 运行崩溃: {str(e)}")

if __name__ == "__main__":
    # 从环境变量读取，默认长江电力
    target_stock = os.getenv("STOCK_CODE", "600900")
    get_eastmoney_data(target_stock)
