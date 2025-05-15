#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from flask import Flask, request, render_template_string
import urllib.parse

# 数据加载
data_path = "南大周边店铺.xlsx"
df = pd.read_excel(data_path, sheet_name='美食_南京_3000m_poi_results')
df['cost'] = df['cost'].fillna(df['cost'].median())
df['tag'] = df['tag'].fillna('')
df['rating'] = df['rating'].fillna(0)
df['type'] = df['type'].fillna('')
df['name'] = df['name'].fillna('')
df['address'] = df['address'].fillna('')

# 百度地图导航链接生成函数
def generate_baidu_map_link(address):
    base = "https://map.baidu.com/search/"
    return base + urllib.parse.quote(address)

def recommend_restaurants(keyword, max_price=100, min_rating=4.0, top_n=10):
    result_df = df[df['rating'] >= min_rating]
    if max_price:
        result_df = result_df[result_df['cost'] <= max_price]
    if keyword:
        mask = (
            result_df['name'].str.contains(keyword, na=False, case=False) |
            result_df['type'].str.contains(keyword, na=False, case=False) |
            result_df['tag'].str.contains(keyword, na=False, case=False)
        )
        result_df = result_df[mask]
    result_df = result_df.sort_values(by=['rating', 'cost'], ascending=[False, True]).head(top_n)
    result_df['简评'] = result_df.apply(lambda row: f"{row['name']} 是一家评分 {row['rating']} 分的 {row['type'].split(';')[-1]}，人均约 {int(row['cost'])} 元。", axis=1)
    result_df['map_link'] = result_df['address'].apply(generate_baidu_map_link)
    return result_df[['name', 'type', 'cost', 'rating', 'address', '简评', 'map_link']]

# Flask app 初始化
app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>菜根探 · 美食推荐</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #5A5A5A; }
        form { margin-bottom: 30px; }
        .result { margin-bottom: 20px; padding: 10px; border-bottom: 1px solid #ccc; }
    </style>
</head>
<body>
    <h1>🍜 菜根探 · 美食推荐官</h1>
    <form method="get">
        <label>你今天想吃什么？<input type="text" name="keyword" required></label>
        <label>最大人均预算（元）<input type="number" name="max_price" value="80"></label>
        <input type="submit" value="智能推荐">
    </form>

    {% if results %}
        <h2>为你推荐以下餐厅：</h2>
        {% for row in results %}
            <div class="result">
                <strong>{{ row['name'] }}</strong> - {{ row['type'] }}<br>
                📍 地址：<a href="{{ row['map_link'] }}" target="_blank">{{ row['address'] }}</a><br>
                💰 人均：{{ row['cost'] }} 元 ｜ ⭐ 评分：{{ row['rating'] }}<br>
                📝 简评：{{ row['简评'] }}<br>
                🧭 <a href="{{ row['map_link'] }}" target="_blank">点击打开百度地图导航</a>
            </div>
        {% endfor %}
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    keyword = request.args.get('keyword', '')
    max_price = request.args.get('max_price', '')
    results = []
    if keyword:
        try:
            max_price_val = int(max_price) if max_price else 100
            df_result = recommend_restaurants(keyword, max_price=max_price_val)
            results = df_result.to_dict(orient='records')
        except Exception as e:
            results = []
    return render_template_string(HTML_TEMPLATE, results=results)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

