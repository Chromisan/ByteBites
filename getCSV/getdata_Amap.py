import requests
from typing import List, Dict
import json
import os
import csv  # 添加csv模块导入
import time
from dotenv import load_dotenv
load_dotenv()
class GaodeMapAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://restapi.amap.com/v5/place/around"
    def search_pois(self, keyword: str, location: str = "", city: str = "", radius: int = 3000, page_size: int = 25, max_pages: int = 5) -> Dict:
        all_pois = []
        all_business = {}
        all_photos = []
    
        for page_num in range(1, max_pages + 1):
            params = {
            'key': self.api_key,
            'keywords': keyword,
            'region': city,#城市名称(可选)
            #'types':'050000',
            'radius': radius,#搜索半径（可调），单位：米
            'output': 'JSON',
            'page_size': min(page_size, 25),  # 限制最大值为25
            'page_num': page_num,
            'show_fields': 'business',# 指定需要返回的字段'business,photos'#获取照片！！
            'extensions':'all'
            }
        
        # 如果提供了location，添加到请求参数中
            if location:
                params['location'] = location
                #print(f"参数: {params}")
    
            try:
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                result = response.json()
                #print("API返回数据:", json.dumps(result, ensure_ascii=False, indent=2))  # 添加这行调试代码
            
                if result['status'] == '1':
                    pois = result.get('pois', [])
                    if not pois:  # 如果当前页没有数据，说明已经到最后一页
                        print("这页怎么没数据了")
                        break
                    
                    all_pois.extend(pois)
                    # 更新商户信息
                    all_business.update(result.get('business', {}))
                    # 添加照片信息
                    all_photos.extend(result.get('photos', []))
                
                    print(f"已获取第 {page_num} 页数据，共 {len(pois)} 条记录")
                    # 添加30秒休眠，但最后一页不需要休眠
                    if page_num < max_pages:
                        print(f"等待30秒后继续获取下一页...")
                        time.sleep(30)
                    else:
                        print("原来已经是最后一页了")
                else:
                    print(f"获取第 {page_num} 页数据失败: {result['info']}")
                    break
                
            except Exception as e:
                print(f"获取第 {page_num} 页时发生错误: {str(e)}")
                break
    
        return {
            'pois': all_pois,
            'business': all_business,
            'photos': all_photos
        }
    
    def get_location_by_ip(self) -> str:
        """获取当前IP所在位置的坐标"""
        try:
            ip_url = "https://restapi.amap.com/v3/ip"
            params = {'key': self.api_key}
            response = requests.get(ip_url, params=params)
            result = response.json()
            if result['status'] == '1' and result.get('rectangle'):
                # 取经纬度范围的中心点
                rect = result['rectangle'].split(';')[0]
                return format_location(rect)
            return ""
        except:
            return ""
        
def format_location(location: str) -> str:

    try:
        if not location:
            return ""
        # 分割经纬度
        lng, lat = location.split(',')
        # 格式化为6位小数
        formatted_lng = f"{float(lng):.6f}"
        formatted_lat = f"{float(lat):.6f}"
        return f"{formatted_lng},{formatted_lat}"
    except:
        return location

def format_poi_info(poi: Dict, business: Dict, photos: List) -> str:
    """格式化POI,business,photo信息，显示更详细的信息"""
    # 基础信息
    basic_info = f"""
    【基础信息】
    名称: {poi.get('name', '未知')}
    地址: {poi.get('address', '未知')}
    位于: {poi.get('location', '未知')}
    类型: {poi.get('type', '未知')}"""

    # 从 POI 中获取商户信息
    business = poi.get('business', {})
    # 从 POI 中获取照片信息
    photos = poi.get('photos', [])


    # 联系方式
    contact_info = f"""
    【联系方式】
    电话: {business.get('tel', '未知')}"""

    # 商户信息
    business_info = f"""
    【商户信息】
    今日营业时间: {business.get('opentime_today', '未知')}
    每周营业时间: {business.get('opentime_week', '未知')}"""
    
    # 餐饮信息
    restaurant_info = f"""
    【餐饮信息】
    人均消费: {business.get('cost ', '未知')}
    评分：{business.get('rating', '未知')}
    特色菜品: {business.get('tag ', '未知')}
    别名: {business.get('alias', '无')}"""

    # 添加图片信息
    if photos and isinstance(photos, list):
        photo_info = "\n【图片信息】"
        for i, photos in enumerate(photos, 1):
            photo_info += f"""
            图片{i}:
            标题: {photos.get('title', '未知')}
            URL: {photos.get('url', '未知')}"""
    else:
        photo_info = "\n【图片信息】\n暂无图片"


    return basic_info + contact_info + business_info + restaurant_info + photo_info

def save_to_csv(pois: List[Dict], filename: str = "poi_results.csv"):
    """
    将POI数据保存为CSV文件
    params:
        pois: POI信息列表
        filename: 输出的CSV文件名
    """
    if not pois:
        print("没有数据可以保存")
        return
    
    # 确定CSV文件的表头（根据POI数据的关键字段）
    fieldnames = [
        'name', 'address', 'location', 'type',
        'tel', 'cost', 'rating', 'opentime_today',
        'opentime_week', 'tag'
    ]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for poi in pois:
                # 提取business信息
                business = poi.get('business', {})
                
                # 构建每一行的数据
                row = {
                    'name': poi.get('name', ''),
                    'address': poi.get('address', ''),
                    'location': poi.get('location', ''),
                    'type': poi.get('type', ''),
                    'tel': business.get('tel', ''),
                    'cost': business.get('cost', ''),
                    'rating': business.get('rating', ''),
                    'opentime_today': business.get('opentime_today', ''),
                    'opentime_week': business.get('opentime_week', ''),
                    'tag': business.get('tag', '')
                }
                writer.writerow(row)
        print(f"数据已保存到 {filename}")
    except Exception as e:
        print(f"保存CSV文件时出错: {str(e)}")



def main():
    API_KEY = os.getenv("AMAP_API_KEY")
    gaode = GaodeMapAPI(API_KEY)
    
    #INPUT-para 获取用户输入
    keyword = input("请输入要搜索的地点: ")
    city = input("请输入城市名(回车跳过，默认为南京): ") or "南京"
    page_size = 25  #要显示的数量（可调，默认20）
    max_pages = 12   # 最大获取页数
    radius = 3000   # 搜索半径
    # 获取当前位置坐标
    locationI = '118.779711,32.054377'#物理楼坐标#gaode.get_location_by_ip()#ip坐标不准确
    print(f"获取到的当前位置坐标: {locationI}")
    # 搜索POI，传入location参数 location=location
    result = gaode.search_pois(
        keyword, 
        city=city, 
        radius=radius,
        page_size=page_size, 
        location=locationI,
        max_pages=max_pages
    )
    pois = result['pois']
    #business = result['business']
    #photos = result['photos']

    if pois:
        print(f"\n找到 {len(pois)} 个相关地点:")
        """for i, poi in enumerate(pois, 1):
            print(f"\n--- 地点 {i} ---")
            print(format_poi_info(poi, business, photos))
        """
        # 保存数据到CSV文件
        filename = f"{keyword}_{city}_{radius}m_poi_results.csv"
        save_to_csv(pois, filename)
    else:
        print("未找到相关地点")

if __name__ == "__main__":
    main()