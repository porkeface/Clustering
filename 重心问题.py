import concurrent.futures
import requests
import geopandas as gpd
import random

from shapely.geometry import shape

n = 0

def fetch_walking_time(origin, destination, key, mode, show_fields):
    # 高德API的URL
    https="https://restapi.amap.com/v5/direction"
    url = f'{https}/{mode}?key={key}&origin={origin}&destination={destination}&show_fields={show_fields}'
    try:
        # 发送GET请求
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['status'] == '1' and data['info'] == 'OK':
            distance = data['route']['paths'][0]['distance']
            duration = data['route']['paths'][0]['cost']['duration']
            return distance, duration
        else:
            # 如果不是'status': '1', 'info': 'OK'，就重新请求一遍，因为api可能不稳定
            return fetch_walking_time(origin, destination, key, mode, show_fields)
    except requests.RequestException as e:
        # 重新抛出异常或进行其他错误处理
        raise e


gdf = gpd.read_file("F:\\厦门市\\厦门市.shp")


# 定义一个函数来随机提取坐标
def extract_random_coordinates(row):
    # 获取几何对象
    geometry = row.geometry
    # 将几何对象转换为Shapely几何对象
    shapely_geom = shape(geometry)
    # 随机选择几何对象
    if shapely_geom.geom_type == 'Point':
        # 对于点，直接返回坐标
        return shapely_geom.coords.xy
    elif shapely_geom.geom_type == 'LineString' or shapely_geom.geom_type == 'MultiLineString':
        # 对于线，随机选择一个线段
        if shapely_geom.geom_type == 'MultiLineString':
            line = random.choice(shapely_geom.geoms)
        else:
            line = shapely_geom
        # 随机选择线段上的一个点
        index = random.randint(0, len(line.coords) - 1)
        return line.coords[index]
    elif shapely_geom.geom_type == 'Polygon' or shapely_geom.geom_type == 'MultiPolygon':
        # 对于面，随机选择一个面
        if shapely_geom.geom_type == 'MultiPolygon':
            polygon = random.choice(shapely_geom.geoms)
        else:
            polygon = shapely_geom
        # 随机选择一个环
        if len(polygon.interiors) > 0:
            rings = polygon.interiors + (polygon.exterior,)
        else:
            rings = (polygon.exterior,)
        ring = random.choice(rings)
        # 随机选择环上的一个点
        index = random.randint(0, len(ring.coords) - 1)
        return ring.coords[index]
    else:
        return None


# 返回经纬度
def piont(num):
    lst = []
    for i in range(num):
        gdf['random_coordinates'] = gdf.apply(extract_random_coordinates, axis=1)
        lst.append(gdf.iloc[0]["random_coordinates"])
    return lst

    # 返回经纬度


def piont():
    gdf['random_coordinates'] = gdf.apply(extract_random_coordinates, axis=1)
    return gdf.iloc[0]["random_coordinates"]


def main():
    key = '417eb6f8ecd5569727e6612828cb49a3'  # 替换为您的API密钥hsy
    key = 'fd519562fc3140f3942a801334781727'  # 替换为您的API密钥wss
    key = 'ff4bb143244cb3f6078ca9014631a272'  # 替换为您的API密钥sk
    mode = 'driving'
    show_fields = 'cost'

    # 储存临时获取回来的成本数据
    temporary = []

    #输入的五个起始位置经纬度坐标
    origin_point = [(118.138383, 24.5178),
                    (118.082837, 24.450496),
                    (118.167067, 24.532477),
                    (118.185164, 24.480522),
                    (118.103277, 24.489196)]

    x = [i[0] for i in origin_point]   #返回五个坐标的经度列表
    y = [i[1] for i in origin_point]   #返回五个坐标的纬度列表
    section_x = (min(x), max(x))       #五个经度中最大最小经度范围
    section_y = (min(y), max(y))       #五个经度中最大最小纬度范围
    destinations = []                  #保存随机生成的五个经纬度坐标

    #随机生成五个经纬度数组，判断是否在所输入坐标的最大最小经纬度范围内
    m = 5
    while m:
        i = piont()
        if section_x[0] <= i[0] <= section_x[1] and section_y[0] <= i[1] <= section_y[1]:
            destinations.append(i)
            m -= 1
        continue

    #粒子当前位置
    tem_destinations = [i for i in enumerate(destinations)]
    print("tem_destinations:", tem_destinations)

    gbest = []#储存群体最优位置
    pbest = []#个体群体最优位置
    # 上次最小距离
    last_distancesbest = 999999999
    last_durationsbest = 0
    for dest_index, destination in enumerate(destinations):
        temporary.clear()
        for index, origin in enumerate(origin_point):
            cost = fetch_walking_time(','.join(map(str, origin)), ','.join(map(str, destination)),
                                      key, mode,show_fields)
            temporary.append(cost)
        distance_cost = [int(dis[0]) for dis in temporary]
        total_distances = sum(distance_cost)
        if last_distancesbest >= total_distances:
            last_distancesbest = total_distances
            gbest.append((dest_index, destination, total_distances))
        pbest.append((dest_index, destination, total_distances))
    print("pbest:", pbest)
    print("gbest:", gbest)
    print("_______________________")

    # 返回更新经纬度，粒子下一次的位置
    update_coordinates = []
    c1 = c2 = 1     #学习因子
    rand = (round(random.uniform(0.01, 0.1), 3))
    Vx = 0          #新经度坐标
    Vy = 0          #新纬度坐标

    num = 30
    count = 0
    while num:
        count += 1
        num -= 1
        for i in range(5):
            pbest_dx = pbest[i][1][0] - tem_destinations[i][1][0]
            pbest_dy = pbest[i][1][1] - tem_destinations[i][1][1]
            gbest_dx = gbest[-1][1][0] - tem_destinations[i][1][0]
            gbest_dy = gbest[-1][1][1] - tem_destinations[i][1][1]
            Vx += c1 * rand * pbest_dx + c2 * rand * gbest_dx
            Vy += c1 * rand * pbest_dy + c2 * rand * gbest_dy
            new_coordinate = (round(tem_destinations[i][1][0] + Vx, 6),
                              round(tem_destinations[i][1][1] + Vy, 6))
            update_coordinates.append((i, new_coordinate))
        print("update_coordinates:", update_coordinates)

        for dest_index, destination in update_coordinates:
            temporary.clear()
            for index, origin in enumerate(origin_point):
                cost = fetch_walking_time(','.join(map(str, origin)), ','.join(map(str, destination)),
                                          key, mode,show_fields)
                temporary.append(cost)
            distance_cost = [int(dis[0]) for dis in temporary]
            total_distances = sum(distance_cost)
            if last_distancesbest >= total_distances:
                last_distancesbest = total_distances
                gbest.append((dest_index + 5 * count, destination, total_distances))
            if pbest[dest_index][-1] >= total_distances:
                pbest[dest_index] = (dest_index + 5 * count, destination, total_distances)
        tem_destinations.clear()
        tem_destinations = [i for i in update_coordinates]
        update_coordinates.clear()
        print("pbest:", pbest)
        print("gbest:", gbest)
        print('------------------')


if __name__ == "__main__":
    try:
        main()
    except RecursionError as e:
        print("出现局部最优 或 api超限")
