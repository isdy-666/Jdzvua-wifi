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

    # 模拟请求参数 通过F12去抓取自己的运营商 以下请求除了wlan_user_ip其他都需要改成自己抓取的请求，以下信息全部重抓取
    params = {
        "callback": callback,
        "login_method": "1",
        "user_account": ",0,学号@telecom",  # 改成学号
        "user_password": "密码",  # 改成密码
        "wlan_user_ip": wlan_user_ip,
        "wlan_user_ipv6": "",
        "wlan_user_mac": "",
        "wlan_ac_ip": "",
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

# 定时任务检查
def check_wifi_and_login():
    connected_wifi = get_connected_wifi()
    if connected_wifi == "Jvua":
        print("已连接到指定的 Wi-Fi：Jvua，开始登录...")
        if login_to_campus():
            # 登录成功后不再继续运行调度器
            print("登录成功，停止检查任务。")
            return  # 成功登录后退出函数，不再安排下次检查
    else:
        print(f"当前未连接到指定的 Wi-Fi 网络。当前连接的是：{connected_wifi}，等待连接...")

    # 如果未连接或登录失败，重新安排下一次检查
    scheduler.enter(5, 1, check_wifi_and_login)  # 间隔时间可以适当调整以减少频率

# 执行登录守护程序
if __name__ == "__main__":
    try:
        # 安排第一次检查 Wi-Fi 状态的时间
        scheduler.enter(0, 1, check_wifi_and_login)
        # 启动调度器
        scheduler.run()
    except Exception as e:
        logging.error(f"程序运行出现异常：{e}", exc_info=True)
        input("程序出现异常，按任意键退出...")  # 防止程序闪退
