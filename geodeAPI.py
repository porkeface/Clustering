import requests

n=0
def fetch_walking_time(origin, destination, key, mode, show_fields):
    global n
    # 高德API的URL
    base_url = "https://restapi.amap.com/v5/direction/"
    full_url = f"{base_url}{mode}?key={key}&origin={origin}&destination={destination}&show_fields={show_fields}"
    print(full_url)

    try:
        # 发送GET请求
        response = requests.get(full_url)
        response.raise_for_status()
        data = response.json()

        if data['status'] == '1' and data['info'] == 'OK':
            distance = data['route']['paths'][0]['distance']
            duration = data['route']['paths'][0]['cost']['duration']
            print(distance,duration)
            return distance, duration
        else:
            n+=1
            print(n)
            # 如果不是'status': '1', 'info': 'OK'，就重新请求一遍，因为api可能不稳定
            # return fetch_walking_time(origin, destination, key, mode, show_fields)
    except requests.RequestException as e:
        # 重新抛出异常或进行其他错误处理
        raise e
key = 'ff4bb143244cb3f6078ca9014631a272'  # 替换为您的API密钥
key = '417eb6f8ecd5569727e6612828cb49a3'  # 替换为您的API密钥
mode = 'driving'
show_fields = 'cost'
# 起点和终点的经纬度
points = [(117.9900584,24.7736418), (117.9860057,24.6096735), (118.1364632,24.5853571), (118.2940129,24.7114982),
          (118.1592598,24.8204152)]
destinations = [(118.254211,24.827292), (118.298744,24.827442), (117.985913,24.853451), (118.183155,24.455286),
                (117.941782,24.640597)]
for origin,destination in zip(points,destinations):
    fetch_walking_time(",".join(map(str,origin)), ",".join(map(str,destination)), key, mode, show_fields)
