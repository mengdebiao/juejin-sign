import requests  # 导入 requests 库，用于发送 HTTP 请求
import json  # 导入 json 库，用于处理 JSON 数据
import time  # 导入 time 库，用于延时操作
import random  # 导入 random 库，用于生成随机数


# 配置参数
aid = ""
uuid = ""
params = ''
cookie = ""

# 定义请求头，用于模拟真实的浏览器请求
headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7",
    "content-type": "application/json",
    "cookie": cookie,  # 将之前定义的 cookie 变量放入请求头
    "origin": "https://juejin.cn",
    "priority": "u=1, i",
    "referer": "https://juejin.cn/",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    # 模拟浏览器的用户代理
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "x-secsdk-csrf-token": "000100000001039cfd4620f0661337ddb9fabb46968cb69f8593b0f7dd3f058c34277983aace17f36bdcc40d4ddc",
}

sign_in_time = None  # 签到时间
sign_in_reward = None  # 签到奖励矿石
remaining_ore = None  # 当前剩余矿石
continuous_check_in = None  # 连续签到天数
total_check_in = None  # 累计签到天数
sign_error = None  # 签到异常提示
lottery_prize = None  # 抽中奖品
luck_value = None  # 获取幸运值
total_luck_value = None  # 累计幸运值


# 通用请求函数
def send_request(method, url, **kwargs):
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"请求发生错误：{e}")
        return None


# 签到函数
def check_in():
    """
    签到函数，发送 POST 请求到指定 URL，进行签到操作，更新签到时间
    当响应中的 err_no 为 0 时，更新签到奖励矿石和当前剩余矿石
    如果 data["data"]["err_no"] 为 403，说明签到失败，可能是 Cookie 过期
    """
    url = (
        f"https://api.juejin.cn/growth_api/v1/check_in"
        f"?aid={aid}&uuid={uuid}&{params}"
    )
    data = send_request("POST", url, headers=headers, json={})
    if data:
        global sign_in_time, sign_error
        sign_in_time = time.strftime("%Y年%m月%d日 %H:%M:%S", time.localtime())
        if data.get("err_no") == 0:
            # 处理登录过期的情况
            if data["data"].get("err_no") == 403:
                sign_error = data["data"].get("err_msg")
                print(
                    "签到失败，Cookie 可能已过期，请检查 Cookie 是否正确或重新获取 Cookie"
                )
            else:
                # 处理签到成功的情况
                global sign_in_reward
                sign_in_reward = data["data"]["incr_point"]
        elif data.get("err_no") == 15001:
            sign_error = data["err_msg"]
        return data


# 抽奖函数
def draw_lottery():
    url = (
        f"https://api.juejin.cn/growth_api/v1/lottery/draw"
        f"?aid={aid}&uuid={uuid}&{params}"
    )
    data = send_request("POST", url, headers=headers, json={})
    if data and data.get("err_no") == 0:
        global lottery_prize, luck_value, total_luck_value
        lottery_prize = data["data"]["lottery_name"]
        luck_value = data["data"]["draw_lucky_value"]
        total_luck_value = data["data"]["total_lucky_value"]
    return data


# 获取签到天数的函数
def get_check_in_days():
    url = (
        f"https://api.juejin.cn/growth_api/v1/get_counts"
        f"?aid={aid}&uuid={uuid}&spider=0"
    )
    data = send_request("GET", url, headers=headers)
    if data and data.get("err_no") == 0:
        # 更新连续签到天数和累计签到天数
        global continuous_check_in, total_check_in
        continuous_check_in = data["data"]["cont_count"]
        total_check_in = data["data"]["sum_count"]
    return data


# 获取当前剩余矿石的函数
def get_remaining_ore():
    url = (
        f"https://api.juejin.cn/growth_api/v1/get_cur_point"
        f"?aid={aid}&uuid={uuid}&spider=0"
    )
    data = send_request("GET", url, headers=headers)
    if data and data.get("err_no") == 0:
        global remaining_ore
        remaining_ore = data["data"]
    return data


# 随机延迟1-10分钟和1-59秒
minutes_delay = random.randint(0, 10)
seconds_delay = random.randint(1, 59)
total_delay = minutes_delay * 60 + seconds_delay
print(f"等待 {minutes_delay} 分 {seconds_delay} 秒 ({total_delay} 秒) 后进行签到...")
time.sleep(total_delay)

# 调用签到函数并获取结果
check_in_result = check_in()
if check_in_result:
    print("签到结果：", json.dumps(check_in_result, ensure_ascii=False, indent=4))
    # 先检查 check_in_result 是否为 None 以及 'data' 键是否存在
    if check_in_result.get("data") and check_in_result["data"].get("err_no") == 403:
        # 这里可以添加飞书通知
        exit(1)  # 签到失败，终止程序
else:
    print("未能获取签到结果。")

# 等待5到15秒后执行抽奖
delay = random.randint(5, 15)
print(f"等待 {delay} 秒后进行抽奖...")
time.sleep(delay)

# 调用抽奖函数并获取结果
lottery_result = draw_lottery()
if lottery_result:
    print("抽奖结果：", json.dumps(lottery_result, ensure_ascii=False, indent=4))
else:
    print("未能获取抽奖结果。")

# 调用获取签到天数的函数并获取结果
check_in_days_result = get_check_in_days()
if check_in_days_result:
    print("签到天数：", json.dumps(check_in_days_result, ensure_ascii=False, indent=4))
else:
    print("未能获取签到天数。")

# 调用获取当前剩余矿石的函数并获取结果
remaining_ore_result = get_remaining_ore()
if remaining_ore_result:
    print("剩余矿石：", json.dumps(remaining_ore_result, ensure_ascii=False, indent=4))
else:
    print("未能获取当前剩余矿石。")

# 打印所有结果
print(f"签到时间：{sign_in_time}")
if sign_error:
    print(f"签到异常提示：{sign_error}")
else:
    print(f"签到奖励矿石：{sign_in_reward}")
print(f"当前剩余矿石：{remaining_ore}")
print(f"连续签到天数：{continuous_check_in}")
print(f"累计签到天数：{total_check_in}")
print(f"抽中奖品：{lottery_prize}")
print(f"获取幸运值：{luck_value}")
print(f"累计幸运值：{total_luck_value}")
