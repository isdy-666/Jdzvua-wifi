import os
import subprocess
import requests
import random
import time
import sched
import socket
import logging
import ctypes

# 初始化日志配置
logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

scheduler = sched.scheduler(time.time, time.sleep)

# 动态生成 callback 和 v 参数
def generate_dynamic_params():
    callback = f"dr{random.randint(1000, 9999)}"
    v = random.randint(1000, 9999)  # 假设是四位随机数
    return callback, v

# 获取当前连接的 Wi-Fi 名称（支持 Windows 和 Linux）
def get_connected_wifi():
    try:
        if os.name == 'nt':  # Windows 系统
            result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True, shell=True)
            for line in result.stdout.split('\n'):
                if "SSID" in line and "BSSID" not in line:
                    wifi_name = line.split(':')[-1].strip()
                    return wifi_name
        else:  # 假设是 Linux 系统
            result = subprocess.run(["iwgetid", "-r"], capture_output=True, text=True)
            wifi_name = result.stdout.strip()
            return wifi_name
    except Exception as e:
        logging.error(f"获取 Wi-Fi 名称失败：{e}", exc_info=True)
        return None

# 动态获取本地 IP 地址
def get_local_ip():
    try:
        # 使用 UDP 协议获取本地 IP 地址
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        logging.error(f"获取本地 IP 失败：{e}", exc_info=True)
        return None

# 使用 ctypes 发送 Windows 系统通知
def show_notification(title, message):
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x40 | 0x1)
    except Exception as e:
        logging.error(f"发送通知失败：{e}", exc_info=True)

# 登录函数
def login_to_campus():
    url_base = "http://172.22.1.46:801/eportal/portal/login"

    # 获取动态参数
    callback, v = generate_dynamic_params()

    # 动态获取本地 IP
    wlan_user_ip = get_local_ip()
    if not wlan_user_ip:
        print("无法获取本地 IP，登录终止。")
        return False

    # 模拟请求参数 通过F12去抓取自己的运营商 以下请求除了wlan_user_ip其他都需要改成自己抓取的请求
    params = {
        "callback": callback,
        "login_method": "1",
        "user_account": ",0,学号@telecom",  # 改成学号  @telecom是运营商@telecom是中国电信
        "user_password": "密码",  # 改成密码
        "wlan_user_ip": wlan_user_ip,
        "wlan_user_ipv6": "",
        "wlan_user_mac": "",#自己抓mac地址
        "wlan_ac_ip": "172.17.2.254",
        "wlan_ac_name": "",
        "jsVersion": "4.2",
        "terminal_type": "1",
        "lang": "zh-cn",
        "v": v
    }

    try:
        # 发送请求
        response = requests.get(url_base, params=params)
        if response.status_code == 200:
            print("登录成功！")
            print("返回数据：", response.text)
            # 发送系统通知
            show_notification("校园网登录成功", "您已成功登录校园网。")
            return True  # 返回 True 表示登录成功
        else:
            print("登录失败，HTTP 状态码：", response.status_code)
            logging.error(f"登录失败，HTTP 状态码：{response.status_code}")
            return False  # 返回 False 表示登录失败
    except Exception as e:
        logging.error(f"请求失败：{e}", exc_info=True)
        return False  # 返回 False 表示请求失败

# 执行登录请求
def execute_login():
    print("直接开始登录...")
    if login_to_campus():
        print("登录成功！")
    else:
        print("登录失败，请检查日志。")

# 执行登录守护程序
if __name__ == "__main__":
    try:
        # 执行登录
        execute_login()
    except Exception as e:
        logging.error(f"程序运行出现异常：{e}", exc_info=True)
        input("程序出现异常，按任意键退出...")  # 防止程序闪退
