import json
import time
import re
import sys
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from undetected_chromedriver import ChromeOptions
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import threading
from make_chart import make_chart




# -----------------------------------------------------------------------------------------------------------------------
def load_setting():
    today = datetime.now().strftime("%Y-%m-%d")

    # 等待页面加载完成并选择美元
    wait = WebDriverWait(driver, 10)
    select_element = wait.until(EC.presence_of_element_located((By.ID, "pjname")))
    select = Select(select_element)
    select.select_by_visible_text(get_currency)

    # 填充开始日期
    search_ipt_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "search_ipt")))
    if not len(search_ipt_elements) > 2:
        print("遇到错误找不到日期填充框\n"
              "进程将在30s后退出...")
        time.sleep(30)
        sys.exit()
    if customize:
        if auto_end_date:
            customize_start_date = calculate_past_date(customize_date)
            search_ipt_elements[1].send_keys(customize_start_date)
            search_ipt_elements[2].send_keys(today)
        else:
            customize_start_date = calculate_past_date(customize_date,end_date)
            search_ipt_elements[1].send_keys(customize_start_date)
            search_ipt_elements[2].send_keys(end_date)
    else:
        search_ipt_elements[1].send_keys(start_date)
        if auto_end_date:
            # 检查是否自动设置结束日期
            search_ipt_elements[2].send_keys(today)
        else:
            search_ipt_elements[2].send_keys(end_date)


    # 等待所有搜索按钮元素加载完成并点击第二个
    search_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input.search_btn")))
    if len(search_buttons) > 1:
        search_buttons[1].click()
    else:
        print("遇到错误找不到搜索按钮\n"
              "进程将在30s后退出...")
        time.sleep(30)
        sys.exit()

def get_latest_release():
    try:
        # 获取系统代理设置
        http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
        https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')

        proxies = {
            "http": http_proxy,
            "https": https_proxy
        }

        # 发送请求获取最新的发布信息
        url = "https://api.github.com/repos/shidaijiya/get_boc_rate/releases/latest"
        response = requests.get(url, proxies=proxies)

        if response.status_code == 200:
            release_info = response.json()
            if 'assets' in release_info and len(release_info['assets']) > 0:
                # 提取第一个资产文件的下载链接
                for asset in release_info['assets']:
                    if 'browser_download_url' in asset:
                        return release_info['tag_name'], asset['browser_download_url']
                print("没有找到发布版本的资产文件下载链接。\n"
                      "正在退出...")
                time.sleep(5)
                sys.exit()
            else:
                print("没有找到发布版本的资产文件。\n"
                      "正在退出...")
                time.sleep(5)
                sys.exit()
        else:
            print(f"无法连接到GitHub，状态码: {response.status_code}\n"
                  "正在退出...")
            time.sleep(5)
            sys.exit()
    except requests.RequestException as e:
        print(f"无法连接到互联网: {e}\n"
              "正在退出...")
        time.sleep(5)
        sys.exit()


def calculate_completion_time(need_time):
    # 计算预计完成的具体时间
    estimated_completion_time = datetime.now() + timedelta(minutes=need_time)

    # 格式化为 "小时:分钟" 的格式
    formatted_completion_time = estimated_completion_time.strftime("%H:%M")

    # 返回预计完成时间的字符串
    return formatted_completion_time


def extract_data():
    # 等待结果加载完成
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.odd")))

    # 获取页面源代码
    html = driver.page_source

    # 使用Beautiful Soup解析HTML
    soup = BeautifulSoup(html, "html.parser")

    # 找到所有<tr class="odd">标签
    detail_rows = soup.find_all("tr", class_="odd")

    # 遍历每个<tr class="odd">标签并提取数据
    for detail_row in detail_rows:
        cells = detail_row.find_all("td")
        row_data = {
            "currency": cells[0].get_text(strip=True),
            "buying_fx_rate": cells[1].get_text(strip=True),
            "buying_cash_rate": cells[2].get_text(strip=True),
            "selling_fx_rate": cells[3].get_text(strip=True),
            "selling_cash_rate": cells[4].get_text(strip=True),
            "boc_conversion_rate": cells[5].get_text(strip=True),
            "time": cells[6].get_text(strip=True)
        }
        data.append(row_data)


def calculate_past_date(input_str, start_date_str=None):
    # 解析传入的日期字符串，如果没有提供，则使用当前日期
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    else:
        start_date = datetime.now()

    # 定义匹配输入格式的正则表达式模式（数字后跟'd'、'w'、'm'或'y'）
    pattern = r'(\d+)([dwmy])'
    match = re.match(pattern, input_str)

    if not match:
        raise ValueError("Invalid input format")

    # 提取数字和时间单位
    number = int(match.group(1))
    period = match.group(2)

    if period == 'd':
        past_date = start_date - timedelta(days=number)
    elif period == 'w':
        past_date = start_date - timedelta(weeks=number)
    elif period == 'm':
        past_date = start_date - timedelta(days=number * 30)  # 将一个月近似为30天
    elif period == 'y':
        past_date = start_date - timedelta(days=number * 365)  # 将一年近似为365天
    else:
        raise ValueError("Invalid period unit")

    return past_date.strftime('%Y-%m-%d')


# -----------------------------------------------------------------------------------------------------------------------
version = "v1.23"


latest_version, download_url = get_latest_release()

if latest_version == version:
    print(f"当前版本:{version} 已经为最新版本")
else:
    print(f"检测到新版本为了更好的体验\n"
          f"最新版本为:{latest_version}\n"
          f"下载链接:{download_url}\n"
          f"更新新版本,程序将在120s后退出...")
    time.sleep(120)
    sys.exit()

# -----------------------------------------------------------------------------------------------------------------------
# 配置文件路径
config_file_path = 'config.json'

# 默认配置
default_config = {
    "rate_url": "https://srh.bankofchina.com/search/whpj/search_cn.jsp",  # 链接地址通常不需要变动
    "get_currency": "美元",  # 需要抓取的货币(中文)
    "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),  # 抓取开始日期(customize = True时无效)
    "end_date": datetime.now().strftime("%Y-%m-%d"),  # 抓取结束日期(auto_end_date = True）
    "customize_date": "1w", # 自定义时间范围
    "customize": True, # 是否开启自定义时间范围
    "auto_end_date": True,  # 是否自动设置结束日期(开启自动默认为当天结束,customize = True时无效)
    "headless": True,  # 是否使用无头模式
    "window_size": [1100, 720],  # 窗口大小
    "save_json_name": "exchange_rates.json",  # 默认保存文件名
    "show_chart": True,  # 是否显示图表(注:当show_chart和save_chart都等于False时默认不制作)
    "save_chart": True,  # 是否保存图表
    "save_chart_name": "exchange_rates.html",
    "only_making": False  # 是否仅制作图表
}

# 检查配置文件是否存在，如果不存在则创建并写入默认配置
if not os.path.exists(config_file_path):
    print("您未创建配置文件,已为您生成默认配置\n"
          "当前默认使用默认配置运行")
    with open(config_file_path, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=4)

try:
    # 加载 JSON 配置文件
    with open(config_file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
except json.JSONDecodeError:
        print("配置文件格式错误\n"
              "30s后退出...")
        time.sleep(30)
        sys.exit()


# 从配置文件中获取变量
rate_url = config['rate_url']
get_currency = config['get_currency']
start_date = config['start_date']
end_date = config['end_date']
customize_date = config['customize_date']
customize = config['customize']
auto_end_date = config['auto_end_date']
headless = config['headless']
window_size = config['window_size']
save_json_name = config['save_json_name']
show_chart = config['show_chart']
save_chart = config['save_chart']
save_chart_name = config['save_chart_name']
only_making = config['only_making']

save_file_exists = os.path.exists(save_json_name)

if only_making:
    if save_file_exists:
        print("您配置了仅制作表格,正在制作")
        make_chart()
        print("制作完成！正在退出...")
        time.sleep(3)
        sys.exit()
    else:
        print(f"{save_json_name} 不存在,已开始抓取")

# -----------------------------------------------------------------------------------------------------------------------
# PATH
driver_path = Service("driver/chromedriver.exe")  # 驱动路径
chrome_path = "Application/chrome.exe"  # Chrome浏览器路径

# 设置 Chrome 参数
options = ChromeOptions()
options.binary_location = chrome_path # 设置指定Chrome浏览器路径(从代码单独运行请注释该行)
options.add_argument("--disable-blink-features=AutomationControlled")  # 禁用某些自动化控制
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")  # 设置 User-Agent
options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 禁用自动化标志
options.add_experimental_option('useAutomationExtension', False)  # 禁用自动化扩展

# 根据 headless 参数设置无头模式
if headless:
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

# 创建浏览器实例
driver = webdriver.Chrome(service=driver_path, options=options)
# 设置浏览器窗口大小
driver.set_window_size(window_size[0], window_size[1])

# -----------------------------------------------------------------------------------------------------------------------

# 打开目标网页
driver.get(rate_url)





load_setting()

# 存储数据
data = []

# 提取第一页数据
extract_data()

# 获取最大页数
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
max_pages_text = soup.find('div', {'class': 'turn_page'}).find('li').get_text(strip=True)
max_pages = int(re.search(r'\d+', max_pages_text).group())

print(f"总页数: {max_pages}")
need_time = max_pages * 2 / 60
need_time = round(need_time, 1)
print(f"正在获取,预计需要: {need_time} 分钟\n"
      f"预计完成时间: {calculate_completion_time(need_time)}")

page_count = 1

while page_count < max_pages:
    try:
        # 找到并点击下一页按钮
        next_button = driver.find_element(By.CSS_SELECTOR, "li.turn_next > a")
        driver.execute_script("arguments[0].click();", next_button)

        # 等待新页面加载完成
        time.sleep(2)  # 等待页面加载，可以根据实际情况调整时间

        # 检查是否出现频繁操作提示
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        if "查询操作太频繁，请一分钟后再试" in soup.text:
            print("查询操作太频繁,尝试刷新重试")
            time.sleep(3)
            driver.refresh()
            # 检查是否出现频繁操作提示
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            if "查询操作太频繁，请一分钟后再试" in soup.text:
                need_time = (max_pages - page_count) * 2 / 60 + 1
                need_time = round(need_time, 1)
                print(f"刷新重试失败进入等待，新预计剩余等待时间为:{need_time}分钟\n"
                      f"剩余:{max_pages - page_count}页\n"
                      f"预计完成时间: {calculate_completion_time(need_time)}")
                time.sleep(60)
                driver.refresh()
                print("等待完成获取继续！")
            else:
                print("刷新重试成功！获取继续")

        else:
            extract_data()
            page_count += 1
            need_time = (max_pages - page_count) * 2 / 60
            need_time = round(need_time, 1)
            print(f"新预计剩余等待时间为:{need_time}分钟\n"
                  f"剩余:{max_pages - page_count}页\n"
                  f"预计完成时间: {calculate_completion_time(need_time)}")

    except Exception as e:
        print(f"出现错误")
        user_input = input("是否刷新重试？(y/n，默认y): ").strip().lower()
        if user_input == 'n':
            user_input = input("是否查看具体错误日志并继续？(y/n，默认n): ").strip().lower()
            if user_input == 'y':
                print(f"具体错误日志: {e}")
            else:
                pass
            print("错误退出,已保存已获取的内容")
            # 将数据保存为 JSON 文件
            with open(save_json_name, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            sys.exit()
        else:
            driver.refresh()

# 关闭浏览器
driver.quit()

# 将数据保存为 JSON 文件
with open(save_json_name, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
print(f"获取完成！数据在{save_json_name}中\n")

if show_chart and save_chart:
    make_chart()

else:
    print("您配置了不制作和显示图表\n"
          "本次进程结束,感谢使用再会！")
    time.sleep(5)
