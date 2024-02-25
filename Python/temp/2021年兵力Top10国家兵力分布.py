from pyecharts.charts import Bar
from pyecharts import options as opts
# 兵力数据为正规军兵力数据
# 俄罗斯空军兵力数据为空天军
country = ['中国', '美国', '俄罗斯', '印度', '朝鲜', '韩国', '土耳其', '巴基斯坦', '伊朗', '越南']  # 国家
army = [91, 54.1, 24, 113, 95, 49.5, 51.9, 52, 35, 42]  # 陆军兵力
navy = [30, 37.2, 14.8, 5.5, 4.6, 6.7, 5.1, 2.2, 1.8, 4.2]  # 海军兵力
airForce = [40, 33.4, 43, 12.7, 8.6, 5.2, 6.3, 4.5, 3, 1.5]  # 空军兵力
otherForce = [39, 18.3, 20.9, 0, 2.4, 0, 0.6, 0, 12, 1.5]  # 其他兵力
bar = Bar()
bar.add_xaxis(xaxis_data=country)
bar.add_yaxis(series_name="陆军", y_axis=army, stack='soldierNumber', color='#008000')
bar.add_yaxis(series_name="海军", y_axis=navy, stack='soldierNumber', color='#000080')
bar.add_yaxis(series_name="空军", y_axis=airForce, stack='soldierNumber', color='#00BFFF')
bar.add_yaxis(series_name="其他", y_axis=otherForce, stack='soldierNumber', color='#800000')
bar.set_global_opts(
    title_opts=opts.TitleOpts(title="2021年兵力Top10国家兵力分布"),  # 标题
    xaxis_opts=opts.AxisOpts(name='国家'),
    yaxis_opts=opts.AxisOpts(name='兵力（万人）'),
    legend_opts=opts.LegendOpts(pos_right='right', orient='vertical'),
    tooltip_opts=opts.TooltipOpts(is_show=True, trigger='axis'),
    datazoom_opts=opts.DataZoomOpts(is_show=True)
)
bar.render('Python\\temp\\2021年兵力Top10国家兵力分布.html')  # 生成HTML文件
