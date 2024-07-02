import json
import pandas as pd
import plotly.express as px







def make_chart():
    # 配置文件路径
    config_file_path = 'config.json'
    # 加载 JSON 配置文件
    with open(config_file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 从配置文件中获取变量
    get_currency = config['get_currency']
    show_chart = config['show_chart']
    save_chart = config['save_chart']
    save_chart_name = config['save_chart_name']


    # 从JSON文件中加载数据
    with open('exchange_rates.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 将JSON数据转换为DataFrame
    df = pd.DataFrame(data)

    # 将time列转换为datetime格式
    df['time'] = pd.to_datetime(df['time'])

    # 将汇率列转换为数值
    df['现汇买入价'] = pd.to_numeric(df['buying_fx_rate'])
    df['现钞买入价'] = pd.to_numeric(df['buying_cash_rate'])
    df['现汇卖出价'] = pd.to_numeric(df['selling_fx_rate'])
    df['现钞卖出价'] = pd.to_numeric(df['selling_cash_rate'])
    df['中行折算价'] = pd.to_numeric(df['boc_conversion_rate'])

    # 提取日期部分
    df['date'] = df['time'].dt.date

    # 保留每天的最高值
    daily_max = df.groupby('date').max().reset_index()

    # 创建交互式图表
    fig = px.line(daily_max, x='date', y=['现汇买入价', '现钞买入价', '现汇卖出价', '现钞卖出价', '中行折算价'],
                  labels={
                      'date': '日期',
                      'value': '汇率'
                  },
                  title=f'{get_currency} to 人民币 汇率走势 (单位为每100外币换算人民币)')

    if save_chart:
        # 保存图表为HTML文件
        fig.write_html(f"{save_chart_name}.html")

    if show_chart:
        # 显示图表
        fig.show()



