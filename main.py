import json
import os
import pandas as pd
from datetime import datetime

# 从 GitHub Actions 的环境变量中获取参数，如果没有则使用默认值
STOCK_CODE = os.getenv('STOCK_CODE', 'SH600519')
TARGET_DAY = os.getenv('TARGET_DAY', '2026-03-27') # 修改了默认日期匹配你的数据

def main():
    print(f"开始分析 {STOCK_CODE} 在 {TARGET_DAY} 的发言...")
    
    # 确保结果文件夹存在
    if not os.path.exists('results'):
        os.makedirs('results')

    # 读取数据 (假设你的数据文件叫 data.json)
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ 找不到 data.json 文件，请确保数据已上传。")
        return

    results = []
    for item in data.get('list', []):
        # 时间戳转换
        dt = datetime.fromtimestamp(item.get('created_at') / 1000)
        day_str = dt.strftime('%Y-%m-%d')
        
        # 股票代码匹配
        symbols = [s.get('symbol') for s in item.get('symbols', [])]
        
        if day_str == TARGET_DAY and STOCK_CODE in symbols:
            results.append({
                '时间': dt.strftime('%H:%M:%S'),
                '用户': item.get('user', {}).get('screen_name'),
                '内容': item.get('text', '')[:50] # 截取前50字
            })

    if results:
        df = pd.DataFrame(results)
        file_path = f"results/{STOCK_CODE}_{TARGET_DAY}.csv"
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"✅ 成功！找到 {len(results)} 条发言，已保存至 {file_path}")
    else:
        # 关键修改：找不到数据时，创建一个空的 CSV 防止 GitHub Action 报错
        print(f"⚠️ {TARGET_DAY} 没有关于 {STOCK_CODE} 的讨论。")
        with open(f"results/no_data.csv", "w") as f:
            f.write("status\nno_data_found")

if __name__ == "__main__":
    main()
