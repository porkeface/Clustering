import concurrent.futures
import json
import random

import requests


def fetch_walking_time(origin, destination, key, mode, show_fields):
    # 高德API的URL
    url = f'https://restapi.amap.com/v5/direction/{mode}?key={key}&origin={origin}&destination={destination}&show_fields={show_fields}'

    try:
        # 发送GET请求
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['status'] == '1' and data['info'] == 'OK':
            distance = data['route']['paths'][0]['distance']
            duration = data['route']['paths'][0]['cost']['duration']
            print(distance,duration)
            return distance, duration
        else:
            #如果不是'status': '1', 'info': 'OK'，就重新请求一遍，因为api可能不稳定
            fetch_walking_time(origin, destination, key, mode, show_fields)
            return ;
    except requests.RequestException as e:
        return str(e)


def o1():
    # 从文件中读取 JSON 数据
    with open("F:/selected_area.geojson", 'r', encoding="utf-8") as file:
        geojson_data = json.load(file)

    # 提取经纬度数据并转换为二维列表
    coordinates_list = []
    for feature in geojson_data['features']:
        geometry = feature['geometry']
        if geometry['type'] == 'MultiPolygon':
            # 对于 MultiPolygon 类型，遍历每个多边形的坐标列表
            for polygon in geometry['coordinates']:
                for ring in polygon:
                    coordinates_list.extend(ring)
        elif geometry['type'] == 'Polygon':
            # 对于 Polygon 类型，遍历每个多边形的坐标列表
            for ring in geometry['coordinates']:
                coordinates_list.extend(ring)
        elif geometry['type'] == 'Point':
            # 对于 Point 类型，直接添加坐标
            coordinates_list.append(geometry['coordinates'])
    # 将列表中的每个子列表转换为元组
    tuple_list = [tuple(sublist) for sublist in coordinates_list]
    return tuple_list


def lst():
    # 假设这是你的列表
    my_list = o1()
    my_list2 = my_list[:]
    # 指定你想抽取的元素数量
    num_elements = 5

    # 使用 random.sample 从列表中随机抽取元素
    five_piont = random.sample(my_list, num_elements)

    # 从原列表中移除这些元素
    for element in five_piont:
        my_list2.remove(element)

    print("原列表:", my_list)
    print("新列表:", my_list2)
    print("抽取的元素:", five_piont)

def main():
    key = 'ff4bb143244cb3f6078ca9014631a272'  # 替换为您的API密钥
    mode = 'driving'
    show_fields = 'cost'

    # 定义两组经纬度
    origins = [(116.391275, 39.90765)]  # 示例起点坐标列表
    destinations = [(116.410274, 39.921988)]  # 示例终点坐标列表


    with open("D:/gaode_驾车通行时间.txt", 'w') as f:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            for index, origin in enumerate(origins):
                for dest_index, destination in enumerate(destinations):
                    future = executor.submit(fetch_walking_time,','.join(map(str, origin)),','.join(map(str, destination)),key, mode, show_fields)
                    futures[(index, dest_index)] = future

            for (index, dest_index), future in futures.items():
                distance, duration = future.result()
                print(index, dest_index, distance, duration)
                f.write(f"{index}to{dest_index}：路程：{distance}米，耗时：{duration}秒\n")


if __name__ == "__main__":
    main()
