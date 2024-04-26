import math

import numpy as np

from myapp.datasrc import MySQLTool
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Line, Scatter
import os

# 可靠度分级
real_grade = ['4', '3', '2', '1', '0']
conf_grade = {key: real_grade[0] for key in ['0', '1', '4', '5', '9']}
conf_grade.update({key: real_grade[1] for key in ['A', 'C', 'I', 'M', 'P', 'R', 'U']})
conf_grade.update({key: real_grade[2] for key in ['2', '6']})
conf_grade.update({key: real_grade[3] for key in ['3', '7']})
conf_grade.update({key: real_grade[4] for key in ['0']})

# 获取特定气象站全部的的气象数据，考虑到代码的复用定义了这个函数
def alltime(stat):
    '''
    stat: 站点编号，字符串
    begin: 开始日期，传入形式为字符串，格式为“xxxx-xx-xx”
    end: 结束日期，传入形式为字符串，格式为“xxxx-xx-xx”
    '''
    mysqlite = MySQLTool()
    # 执行查询语句
    mysqlite._cur.execute("select * from datasource where substring(stat_date, 1, 11) = %s", (stat,))
    # 获取查询结果
    result = mysqlite._cur.fetchall()
    # 获取查询的字段名
    columns = [desc[0] for desc in mysqlite._cur.description]
    # 使用查询结果和字段名创建 DataFrame
    df = pd.DataFrame(result, columns=columns)
    # print(df)
    # 关闭游标和连接
    mysqlite.close_con()
    return df

# 获取指定时间段的气象数据，考虑到代码的复用定义了这个函数
def spectime(stat, begin, end):
    '''
    stat: 站点编号，字符串
    begin: 开始日期，传入形式为字符串，格式为“xxxx-xx-xx”
    end: 结束日期，传入形式为字符串，格式为“xxxx-xx-xx”
    '''
    mysqlite = MySQLTool()
    newend = end[:-2] + ('0' if len(str(int(end[-2:]) + 1)) == 1 else '') + str(int(end[-2:]) + 1)  # 结束日期要加1
    # 执行查询语句
    # print(((stat + ',' + begin), (stat + ',' + newend)))
    mysqlite._cur.execute("select * from datasource where stat_date between %s and %s",
                          ((stat + ',' + begin), (stat + ',' + newend)))
    # 获取查询结果
    result = mysqlite._cur.fetchall()
    # 获取查询的字段名
    columns = [desc[0] for desc in mysqlite._cur.description]
    # 使用查询结果和字段名创建 DataFrame
    df = pd.DataFrame(result, columns=columns)
    # 关闭游标和连接
    mysqlite.close_con()
    return df

# 展示指定站点在指定时间段的露点数据
def showdew(stat, begin="", end=""):
    '''
    stat: 站点编号，字符串
    begin: 开始日期，传入形式为字符串，格式为“xxxx-xx-xx”
    end: 结束日期，传入形式为字符串，格式为“xxxx-xx-xx”
    '''
    if(begin=="" or end==""):
        df = alltime(stat)
    else:
        df = spectime(stat, begin, end)
    # print(df)
    conf = []
    dew = {}
    # 准备数据
    x_data = [(iter.split(',')[1]).split('T')[0] + '日' + (iter.split(',')[1]).split('T')[1][:2] + '时' for iter in df['stat_date']]
    y_data = [int(iter.split(',')[0])/10 for iter in df['dew']]
    for i in range(len(df['dew'])):
        fir = int((df['dew'][i]).split(',')[0])
        sec = (df['dew'][i]).split(',')[1]
        conf.append(conf_grade[sec] if (fir != 9999) else conf_grade['0'])
    conf_list = {}
    conf_list['4'] = conf.count('4')
    conf_list['3'] = conf.count('3')
    conf_list['2'] = conf.count('2')
    conf_list['1'] = conf.count('1')
    conf_list['0'] = conf.count('0')
    reliable = (conf_list['4'] + conf_list['3'])/len(conf)
    y_data_copy = []
    for i in range(len(conf)):
        if conf[i] == '0' or conf[i] == '1':
            pass
        else:
            y_data_copy.append(y_data[i])
    dew['upt'] = max(y_data_copy)
    dew['lwt'] = min(y_data_copy)
    dew['avg'] = sum(y_data_copy)/len(y_data_copy)
    dew['var'] = np.var(y_data_copy)
    dew['cv'] = math.sqrt(dew['var'])/dew['avg']
    # print(conf_list)
    # 创建 Line 图表
    line_date = Line()
    # line_conf = Line()
    line_conf = Scatter()  # 使用 Scatter 类型来表示散点图
    # 添加数据
    line_date.add_xaxis(xaxis_data=x_data)
    line_date.add_yaxis(series_name='露点数据(°C)', y_axis=y_data, label_opts=opts.LabelOpts(is_show=False), yaxis_index=0)
    line_date.extend_axis(yaxis=opts.AxisOpts(axisline_opts=opts.AxisLineOpts()))  # 添加一条蓝色的y轴
    line_conf.add_xaxis(xaxis_data=x_data)
    line_conf.add_yaxis(series_name='可信度', y_axis=conf, symbol='circle', symbol_size=4, label_opts=opts.LabelOpts(is_show=False), yaxis_index=1)
    # 设置图表标题和其他配置
    line_date.set_global_opts(
        title_opts=opts.TitleOpts(title='站点编号' + stat + '(' + df['name'].loc[0] + ')' + '\n露点数据展示'),
        xaxis_opts=opts.AxisOpts(type_='category'),
        yaxis_opts=opts.AxisOpts(type_='value', axislabel_opts=opts.LabelOpts(formatter="{value}°C")),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="right", pos_top="top")
    )
    line_conf.set_global_opts(
        yaxis_opts=opts.AxisOpts(type_="category"),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="right", pos_top="top")
    )
    line_date.overlap(line_conf)
    # # 渲染图表到 HTML 文件
    # current_directory = os.path.dirname(os.path.realpath(__file__))
    # os.makedirs(current_directory + '/html', exist_ok = True)
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>露点数据</title>
        <style>
            body {{
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            #chart-container {{
                width: 80%;
                height: 80%;
            }}
        </style>
    </head>
    <body>
        <div id="chart-container">
            {line_date.render_embed()}
        </div>
    </body>
    </html>
    '''
    os.makedirs('myapp/static/html/' + stat, exist_ok=True)
    with open('myapp/static/html/' + stat + '/dew.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    return conf_list, reliable, dew
# showdew('55279099999', '2022-12-03', '2023-12-05')

# 展示指定站点在指定时间段的海平面压力数据
def showslp(stat, begin="", end=""):
    '''
    stat: 站点编号，字符串
    begin: 开始日期，传入形式为字符串，格式为“xxxx-xx-xx”
    end: 结束日期，传入形式为字符串，格式为“xxxx-xx-xx”
    '''
    if(begin=="" or end==""):
        df = alltime(stat)
    else:
        df = spectime(stat, begin, end)
    conf = []
    slp = {}
    # 准备数据
    x_data = [(iter.split(',')[1]).split('T')[0] + '日' + (iter.split(',')[1]).split('T')[1][:2] + '时'  for iter in df['stat_date']]
    y_data = [int(iter.split(',')[0])/10 for iter in df['slp']]
    for i in range(len(df['slp'])):
        fir = int((df['slp'][i]).split(',')[0])
        sec = (df['slp'][i]).split(',')[1]
        conf.append(conf_grade[sec] if (fir != 99999) else conf_grade['0'])
    conf_list = {}
    conf_list['4'] = conf.count('4')
    conf_list['3'] = conf.count('3')
    conf_list['2'] = conf.count('2')
    conf_list['1'] = conf.count('1')
    conf_list['0'] = conf.count('0')
    y_data_copy = []
    for i in range(len(conf)):
        if conf[i] == '0' or conf[i] == '1':
            pass
        else:
            y_data_copy.append(y_data[i])
    slp['upt'] = max(y_data_copy)
    slp['lwt'] = min(y_data_copy)
    slp['avg'] = sum(y_data_copy)/len(y_data_copy)
    slp['var'] = np.var(y_data_copy)
    slp['cv'] = math.sqrt(slp['var'])/slp['avg']
    reliable = (conf_list['4'] + conf_list['3']) / len(conf)
    # 创建 Line 图表
    line_date = Line()
    # line_conf = Line()
    line_conf = Scatter()  # 使用 Scatter 类型来表示散点图
    # 添加数据
    line_date.add_xaxis(xaxis_data=x_data)
    line_date.add_yaxis(series_name='气压数据(hPa)', y_axis=y_data, label_opts=opts.LabelOpts(is_show=False), yaxis_index=0)
    line_date.extend_axis(yaxis=opts.AxisOpts(axisline_opts=opts.AxisLineOpts()))  # 添加一条蓝色的y轴
    line_conf.add_xaxis(xaxis_data=x_data)
    line_conf.add_yaxis(series_name='可信度', y_axis=conf, symbol='circle', symbol_size=4, label_opts=opts.LabelOpts(is_show=False), yaxis_index=1)
    # 设置图表标题和其他配置
    line_date.set_global_opts(
        title_opts=opts.TitleOpts(title='站点编号' + stat + '(' + df['name'].loc[0] + ')' + '\n气压数据展示'),
        xaxis_opts=opts.AxisOpts(type_='category'),
        yaxis_opts=opts.AxisOpts(type_='value', axislabel_opts=opts.LabelOpts(formatter="{value}hPa")),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="right", pos_top="top")
    )
    line_conf.set_global_opts(
        yaxis_opts=opts.AxisOpts(type_="category"),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="right", pos_top="top")
    )
    line_date.overlap(line_conf)
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>气压数据</title>
        <style>
            body {{
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            #chart-container {{
                width: 80%;
                height: 80%;
            }}
        </style>
    </head>
    <body>
        <div id="chart-container">
            {line_date.render_embed()}
        </div>
    </body>
    </html>
    '''
    with open('myapp/static/html/' + stat + '/slp.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    return conf_list, reliable, slp
# showslp('55279099999', '2022-12-03', '2023-12-05')

# 展示指定站点在指定时间段的温度数据
def showtmp(stat, begin="", end=""):
    '''
    stat: 站点编号，字符串
    begin: 开始日期，传入形式为字符串，格式为“xxxx-xx-xx”
    end: 结束日期，传入形式为字符串，格式为“xxxx-xx-xx”
    '''
    if(begin=="" or end==""):
        df = alltime(stat)
    else:
        df = spectime(stat, begin, end)
    conf = []
    tmp = {}
    # 准备数据
    x_data = [(iter.split(',')[1]).split('T')[0] + '日' + (iter.split(',')[1]).split('T')[1][:2] + '时' for iter in
              df['stat_date']]
    y_data = [int(iter.split(',')[0]) / 10 for iter in df['tmp']]
    for i in range(len(df['tmp'])):
        fir = int((df['tmp'][i]).split(',')[0])
        sec = (df['tmp'][i]).split(',')[1]
        conf.append(conf_grade[sec] if (fir != 9999) else conf_grade['0'])
    conf_list = {}
    conf_list['4'] = conf.count('4')
    conf_list['3'] = conf.count('3')
    conf_list['2'] = conf.count('2')
    conf_list['1'] = conf.count('1')
    conf_list['0'] = conf.count('0')
    reliable = (conf_list['4'] + conf_list['3']) / len(conf)
    y_data_copy = []
    for i in range(len(conf)):
        if conf[i] == '0' or conf[i] == '1':
            pass
        else:
            y_data_copy.append(y_data[i])
    tmp['upt'] = max(y_data_copy)
    tmp['lwt'] = min(y_data_copy)
    tmp['avg'] = sum(y_data_copy)/len(y_data_copy)
    tmp['var'] = np.var(y_data_copy)
    tmp['cv'] = math.sqrt(tmp['var'])/tmp['avg']
    # 创建 Line 图表
    line_date = Line()
    line_conf = Scatter()  # 使用 Scatter 类型来表示散点图
    # 添加数据
    line_date.add_xaxis(xaxis_data=x_data)
    line_date.add_yaxis(series_name='气温数据(°C)', y_axis=y_data, label_opts=opts.LabelOpts(is_show=False), yaxis_index=0)
    line_date.extend_axis(yaxis=opts.AxisOpts(axisline_opts=opts.AxisLineOpts()))  # 添加一条蓝色的y轴
    line_conf.add_xaxis(xaxis_data=x_data)
    line_conf.add_yaxis(series_name='可信度', y_axis=conf, symbol='circle', symbol_size=4,
                        label_opts=opts.LabelOpts(is_show=False), yaxis_index=1)
    # 设置图表标题和其他配置
    line_date.set_global_opts(
        title_opts=opts.TitleOpts(title='站点编号' + stat + '(' + df['name'].loc[0] + ')' + '\n气温数据展示'),
        xaxis_opts=opts.AxisOpts(type_='category'),
        yaxis_opts=opts.AxisOpts(type_='value', axislabel_opts=opts.LabelOpts(formatter="{value}°C")),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="right", pos_top="top")
    )
    line_conf.set_global_opts(
        yaxis_opts=opts.AxisOpts(type_="category"),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="right", pos_top="top")
    )
    line_date.overlap(line_conf)
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>气温数据</title>
        <style>
            body {{
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            #chart-container {{
                width: 80%;
                height: 80%;
            }}
        </style>
    </head>
    <body>
        <div id="chart-container">
            {line_date.render_embed()}
        </div>
    </body>
    </html>
    '''
    with open('myapp/static/html/' + stat + '/tmp.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    return conf_list, reliable, tmp

# showtmp('55279099999', '2022-12-03', '2023-12-05')

# 展示指定站点在指定时间段的可见度数据
def showvis(stat, begin="", end=""):
    '''
    stat: 站点编号，字符串
    begin: 开始日期，传入形式为字符串，格式为“xxxx-xx-xx”
    end: 结束日期，传入形式为字符串，格式为“xxxx-xx-xx”
    '''
    if(begin=="" or end==""):
        df = alltime(stat)
    else:
        df = spectime(stat, begin, end)
    conf = []
    vis = {}
    # 准备数据
    x_data = [(iter.split(',')[1]).split('T')[0] + '日' + (iter.split(',')[1]).split('T')[1][:2] + '时' for iter in
              df['stat_date']]
    y_data = [int(iter.split(',')[0]) for iter in df['vis']]
    for i in range(len(df['vis'])):
        fir = int((df['vis'][i]).split(',')[0])
        sec = (df['vis'][i]).split(',')[1]
        conf.append(conf_grade[sec] if (fir != 999999) else conf_grade['0'])
    conf_list = {}
    conf_list['4'] = conf.count('4')
    conf_list['3'] = conf.count('3')
    conf_list['2'] = conf.count('2')
    conf_list['1'] = conf.count('1')
    conf_list['0'] = conf.count('0')
    reliable = (conf_list['4'] + conf_list['3']) / len(conf)
    y_data_copy = []
    for i in range(len(conf)):
        if conf[i] == '0' or conf[i] == '1':
            pass
        else:
            y_data_copy.append(y_data[i])
    vis['upt'] = max(y_data_copy)
    vis['lwt'] = min(y_data_copy)
    vis['avg'] = sum(y_data_copy)/len(y_data_copy)
    vis['var'] = np.var(y_data_copy)
    vis['cv'] = math.sqrt(vis['var'])/vis['avg']
    # 创建 Line 图表
    line_date = Line()
    # line_conf = Line()
    line_conf = Scatter()  # 使用 Scatter 类型来表示散点图
    # 添加数据
    line_date.add_xaxis(xaxis_data=x_data)
    line_date.add_yaxis(series_name='可视距离数据(m)', y_axis=y_data, label_opts=opts.LabelOpts(is_show=False), yaxis_index=0)
    line_date.extend_axis(yaxis=opts.AxisOpts(axisline_opts=opts.AxisLineOpts()))  # 添加一条蓝色的y轴
    line_conf.add_xaxis(xaxis_data=x_data)
    line_conf.add_yaxis(series_name='可信度', y_axis=conf, symbol='circle', symbol_size=4,
                        label_opts=opts.LabelOpts(is_show=False), yaxis_index=1)
    # 设置图表标题和其他配置
    line_date.set_global_opts(
        title_opts=opts.TitleOpts(title='站点编号' + stat + '(' + df['name'].loc[0] + ')' + '\n可视距离数据展示'),
        xaxis_opts=opts.AxisOpts(type_='category'),
        yaxis_opts=opts.AxisOpts(type_='value', axislabel_opts=opts.LabelOpts(formatter="{value}m")),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="right", pos_top="top")
    )
    line_conf.set_global_opts(
        yaxis_opts=opts.AxisOpts(type_="category"),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="right", pos_top="top")
    )
    line_date.overlap(line_conf)
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>可视距离数据</title>
        <style>
            body {{
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            #chart-container {{
                width: 80%;
                height: 80%;
            }}
        </style>
    </head>
    <body>
        <div id="chart-container">
            {line_date.render_embed()}
        </div>
    </body>
    </html>
    '''
    with open('myapp/static/html/' + stat + '/vis.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    return conf_list, reliable, vis
# showvis('55279099999', '2022-12-03', '2023-12-05')

# 展示指定站点在指定时间段的风速数据
def showwnd(stat, begin="", end=""):
    '''
    stat: 站点编号，字符串
    begin: 开始日期，传入形式为字符串，格式为“xxxx-xx-xx”
    end: 结束日期，传入形式为字符串，格式为“xxxx-xx-xx”
    '''
    if(begin=="" or end==""):
        df = alltime(stat)
    else:
        df = spectime(stat, begin, end)
    conf = []
    dire = {}
    # 准备数据，制作风向数据展示图
    x_data = [(iter.split(',')[1]).split('T')[0] + '日' + (iter.split(',')[1]).split('T')[1][:2] + '时' for iter in
              df['stat_date']]
    y_data = [int(iter.split(',')[0]) for iter in df['wnd']]
    for i in range(len(df['wnd'])):
        fir = int((df['wnd'][i]).split(',')[0])
        sec = (df['wnd'][i]).split(',')[1]
        conf.append(conf_grade[sec] if (fir != 999) else conf_grade['0'])
    dire_conf_list = {}
    dire_conf_list['4'] = conf.count('4')
    dire_conf_list['3'] = conf.count('3')
    dire_conf_list['2'] = conf.count('2')
    dire_conf_list['1'] = conf.count('1')
    dire_conf_list['0'] = conf.count('0')
    dire_reliable = (dire_conf_list['4'] + dire_conf_list['3']) / len(conf)
    y_data_copy = []
    for i in range(len(conf)):
        if conf[i] == '0' or conf[i] == '1':
            pass
        else:
            y_data_copy.append(y_data[i])
    dire['upt'] = max(y_data_copy)
    dire['lwt'] = min(y_data_copy)
    dire['avg'] = sum(y_data_copy)/len(y_data_copy)
    dire['var'] = np.var(y_data_copy)
    dire['cv'] = math.sqrt(dire['var'])/dire['avg']
    # 创建 Line 图表
    line_dire = Line()
    # line_conf = Line()
    conf_dire = Scatter()  # 使用 Scatter 类型来表示散点图
    # 添加数据
    line_dire.add_xaxis(xaxis_data=x_data)
    line_dire.add_yaxis(series_name='风向数据(°, 从正北方向顺时针开始)', y_axis=y_data, label_opts=opts.LabelOpts(is_show=False), yaxis_index=0)
    line_dire.extend_axis(yaxis=opts.AxisOpts(axisline_opts=opts.AxisLineOpts()))  # 添加一条蓝色的y轴
    conf_dire.add_xaxis(xaxis_data=x_data)
    conf_dire.add_yaxis(series_name='可信度', y_axis=conf, symbol='circle', symbol_size=4,
                        label_opts=opts.LabelOpts(is_show=False), yaxis_index=1)
    # 设置图表标题和其他配置
    line_dire.set_global_opts(
        title_opts=opts.TitleOpts(title='站点编号' + stat + '(' + df['name'].loc[0] + ')' + '\n风向数据展示'),
        xaxis_opts=opts.AxisOpts(type_='category'),
        yaxis_opts=opts.AxisOpts(type_='value', axislabel_opts=opts.LabelOpts(formatter="{value}m")),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="right", pos_top="top")
    )
    conf_dire.set_global_opts(
        yaxis_opts=opts.AxisOpts(type_="category"),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="right", pos_top="top")
    )
    line_dire.overlap(conf_dire)
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>风向数据</title>
        <style>
            body {{
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            #chart-container {{
                width: 80%;
                height: 80%;
            }}
        </style>
    </head>
    <body>
        <div id="chart-container">
            {line_dire.render_embed()}
        </div>
    </body>
    </html>
    '''
    with open('myapp/static/html/' + stat + '/wnddire.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    # 数据准备，制作风速数据展示图
    conf = []
    y_data = []
    sped = {}
    for i in range(len(df['wnd'])):
        fir = int((df['wnd'][i]).split(',')[3])
        y_data.append(fir)
        sec = (df['wnd'][i]).split(',')[4]
        conf.append(conf_grade[sec] if (fir != 9999) else conf_grade['0'])
    sped_conf_list = {}
    sped_conf_list['4'] = conf.count('4')
    sped_conf_list['3'] = conf.count('3')
    sped_conf_list['2'] = conf.count('2')
    sped_conf_list['1'] = conf.count('1')
    sped_conf_list['0'] = conf.count('0')
    sped_reliable = (sped_conf_list['4'] + sped_conf_list['3']) / len(conf)
    y_data_copy = []
    for i in range(len(conf)):
        if conf[i] == '0' or conf[i] == '1':
            pass
        else:
            y_data_copy.append(y_data[i])
    sped['upt'] = max(y_data_copy)
    sped['lwt'] = min(y_data_copy)
    sped['avg'] = sum(y_data_copy)/len(y_data_copy)
    sped['var'] = np.var(y_data_copy)
    sped['cv'] = math.sqrt(sped['var'])/sped['avg']
    # 创建 Line 图表
    line_sped = Line()
    # line_conf = Line()
    conf_sped = Scatter()  # 使用 Scatter 类型来表示散点图
    # 添加数据
    line_sped.add_xaxis(xaxis_data=x_data)
    line_sped.add_yaxis(series_name='风速数据(m/s)', y_axis=y_data, label_opts=opts.LabelOpts(is_show=False),
                        yaxis_index=0)
    line_sped.extend_axis(yaxis=opts.AxisOpts(axisline_opts=opts.AxisLineOpts()))  # 添加一条蓝色的y轴
    conf_sped.add_xaxis(xaxis_data=x_data)
    conf_sped.add_yaxis(series_name='可信度', y_axis=conf, symbol='circle', symbol_size=4,
                        label_opts=opts.LabelOpts(is_show=False), yaxis_index=1)
    # 设置图表标题和其他配置
    line_sped.set_global_opts(
        title_opts=opts.TitleOpts(title='站点编号' + stat + '(' + df['name'].loc[0] + ')' + '\n风速数据展示'),
        xaxis_opts=opts.AxisOpts(type_='category'),
        yaxis_opts=opts.AxisOpts(type_='value', axislabel_opts=opts.LabelOpts(formatter="{value}m")),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="right", pos_top="top")
    )
    conf_sped.set_global_opts(
        yaxis_opts=opts.AxisOpts(type_="category"),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="right", pos_top="top")
    )
    line_sped.overlap(conf_sped)
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>风速数据</title>
        <style>
            body {{
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            #chart-container {{
                width: 80%;
                height: 80%;
            }}
        </style>
    </head>
    <body>
        <div id="chart-container">
            {line_sped.render_embed()}
        </div>
    </body>
    </html>
    '''
    with open('myapp/static/html/' + stat + '/wndsped.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    return dire_conf_list, sped_conf_list, dire_reliable, sped_reliable, dire, sped
# showwnd('55279099999', '2022-12-03', '2023-12-05')

# 在html文件夹下生成所有站点的六类数据展示图，路径格式为"/html/站点编号/xx.html"
def spec_htmls(stat):
    try:
        # print(stat)
        dew_conf, dew_reli, dew = showdew(stat)
        slp_conf, slp_reli, slp = showslp(stat)
        tmp_conf, tmp_reli, tmp = showtmp(stat)
        vis_conf, vis_reli, vis = showvis(stat)
        dire_conf, sped_conf, dire_reli, sped_reli, dire, sped = showwnd(stat)
        reli = {}
        reli['0'] = dew_reli; reli['1'] = slp_reli; reli['2'] = tmp_reli; reli['3'] = vis_reli; reli['4'] = dire_reli; reli['5'] = sped_reli
        analy = {}
        analy['0'] = dew; analy['1'] = slp; analy['2'] = tmp; analy['3'] = vis; analy['4'] = dire; analy['5'] = sped;
        return dew_conf, slp_conf, tmp_conf, vis_conf, dire_conf, sped_conf, reli, analy
    except Exception as e:
        print("[htmls generate error]", e)
        return False

# spec_htmls("55279099999")