import requests
import random
import subprocess
import ctypes
import socket


# 动态生成参数
def generate_dynamic_params():
    callback = "dr1004"  # 登出时 callback 固定为 dr1004
    v = random.randint(1000, 9999)  # 假设 v 是四位随机数
    return callback, v


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
        print(f"获取本地 IP 失败：{e}")
        return None


# 登出函数
def logout_from_campus():
    url_base = "http://172.22.1.46:801/eportal/portal/logout"

    # 获取动态参数
    callback, v = generate_dynamic_params()

    # 动态获取本地 IP
    wlan_user_ip = get_local_ip()
    if not wlan_user_ip:
        print("无法获取本地 IP，登出终止。")
        return

    # 模拟请求参数 以下信息全部需要自己抓取
    params = {
        "callback": callback,
        "login_method": "1",
        "user_account": "drcom",
        "user_password": "123",
        "ac_logout": "0",
        "register_mode": "1",
        "wlan_user_ip": wlan_user_ip,#不要变动
        "wlan_user_ipv6": "",
        "wlan_vlan_id": "0",
        "wlan_user_mac": "",
        "wlan_ac_ip": "",
        "wlan_ac_name": "",
        "jsVersion": "4.2",
        "v": v,
        "lang": "zh"
    }

    try:
        # 发送请求
        response = requests.get(url_base, params=params)
        if response.status_code == 200:
            print("登出成功！")
            print("返回数据：", response.text)
        else:
            print("登出失败，HTTP 状态码：", response.status_code)
    except Exception as e:
        print(f"请求失败：{e}")


# 检查是否为管理员权限
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


# 弹出询问框，询问是否需要关机
def prompt_for_shutdown():
    result = ctypes.windll.user32.MessageBoxW(None, "是否需要立即关机？", "关机确认", 1)
    # MessageBoxW 返回 1 代表用户点击了 "确定"，2 代表用户点击了 "取消"
    return result == 1


# 执行彻底关机
def shutdown_completely():
    # Windows下执行彻底关机命令
    shutdown_command = "shutdown /s /f /t 0"
    try:
        subprocess.run(shutdown_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"关机失败：{e}")


# 主函数
if __name__ == "__main__":
    # 首先进行登出操作
    logout_from_campus()

    # 弹出关机询问框
    if prompt_for_shutdown():
        # 检查管理员权限，如果有则执行关机
        if is_admin():
            shutdown_completely()
        else:
            # 提升为管理员权限以执行关机命令
            ctypes.windll.shell32.ShellExecuteW(None, "runas", "python", __file__, None, 1)
