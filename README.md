# 汇率抓取器

## 概述
此脚本从中国银行网站抓取汇率数据，并生成包含汇率数据的JSON文件。可选地，它还可以生成和保存汇率图表。

## 功能
- 从中国银行网站获取汇率数据。
- 支持无头模式的Chrome浏览器。
- 将数据保存为JSON格式。
- 可选地生成和显示汇率图表。
- 通过JSON文件进行配置。

## 前置条件
- Python 3.7或更高版本
- Google Chrome浏览器
- 与Chrome浏览器版本兼容的ChromeDriver
- 所需的Python包：
  - `requests`
  - `selenium`
  - `beautifulsoup4`
  - `undetected-chromedriver`

## 安装

1. **克隆仓库：**
   ```bash
   git clone https://github.com/shidaijiya/get_boc_rate.git
   cd get_boc_rate
   ```

2. **安装所需的Python包：**
   ```bash
   pip install -r requirements.txt
   ```

3. **下载并放置ChromeDriver：**
   - 从[ChromeDriver官方网站](https://sites.google.com/a/chromium.org/chromedriver/downloads)下载ChromeDriver。
   - 将`chromedriver.exe`文件放在项目的`driver`目录中。

4. **配置：**
   - 如果不存在`config.json`文件，脚本将在首次运行时生成默认配置文件。

## 配置
`config.json`文件包含以下配置选项及其接受的类型：

```json
{
    "rate_url": "https://srh.bankofchina.com/search/whpj/search_cn.jsp",
    "get_currency": "美元",
    "start_date": "2023-06-01",
    "end_date": "2023-06-30",
    "auto_end_date": true,
    "headless": true,
    "window_size": [1100, 720],
    "save_json_name": "exchange_rates.json",
    "show_chart": true,
    "save_chart": true,
    "save_chart_name": "exchange_rates.html",
    "only_making": false
}
```

- `rate_url`：字符串类型，表示汇率页面的URL。
- `get_currency`：字符串类型，表示要抓取的货币名称（中文）。
- `start_date`：字符串类型，表示抓取的开始日期，格式为YYYY-MM-DD。
- `end_date`：字符串类型，表示抓取的结束日期，格式为YYYY-MM-DD。
- `auto_end_date`：布尔值类型，表示是否自动将结束日期设置为当天。
- `headless`：布尔值类型，表示是否以无头模式运行Chrome。
- `window_size`：列表类型，包含两个整数，表示浏览器窗口的宽和高。
- `save_json_name`：字符串类型，表示保存汇率数据的文件名。
- `show_chart`：布尔值类型，表示是否显示图表。
- `save_chart`：布尔值类型，表示是否保存图表。
- `save_chart_name`：字符串类型，表示保存图表的文件名。
- `only_making`：布尔值类型，表示如果数据存在，仅制作图表。

## 使用方法
1. **运行脚本：**
   ```bash
   python main.py
   ```

2. **按照屏幕上的指示进行操作：**
   - 脚本将检查更新。
   - 它将使用配置来抓取数据并可选地生成图表。

## 适用于Windows的发行版
除了直接运行脚本外，您还可以使用适用于Windows的发行版进行安装和配置，具体步骤请参考相关文档。该发行版包含Chrome和ChromeDriver，无需二次配置。

## 错误处理
如果抓取过程中发生错误，脚本将提示您刷新并重试。它还会在退出前保存任何成功抓取的数据。

## 许可
此项目基于MIT许可证。

## 致谢
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Selenium](https://www.selenium.dev/)
- [Requests](https://docs.python-requests.org/en/master/)
