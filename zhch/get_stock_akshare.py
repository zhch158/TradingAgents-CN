# pip install pyecharts akshare
from pyecharts.charts import Kline
from pyecharts import options as opts
import akshare as ak
import os
import sys
import traceback

def create_stock_kline_chart(stock_code="300674"):
    """创建股票K线图"""
    """
    title_opts=opts.TitleOpts(title="stock_code 股票日 K 线图") 为图表添加了一个清晰的标题，方便读者快速了解图表内容。
    xaxis_opts=opts.AxisOpts(is_scale=True) 和 yaxis_opts=opts.AxisOpts(is_scale=True) 设置轴为缩放轴，使图表能够自动适应数据范围，避免出现数据超出显示区域的问题。
    datazoom_opts=[opts.DataZoomOpts(is_show=True, type_="inside")] 添加了数据缩放功能，用户可以方便地拖动鼠标来查看特定日期区间内的 K 线细节，这对于分析大量历史数据时非常实用。
     """
    try:
        # 获取股票的历史数据
        print("正在获取股票数据...")
        
        # 添加更多的错误处理
        try:
            stock_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq", start_date="20250101")
        except Exception as e:
            print(f"获取股票数据失败: {e}")
            print("可能的原因：")
            print("1. 网络连接问题")
            print("2. akshare版本问题，请尝试: pip install akshare --upgrade")
            print("3. 股票代码可能不存在或格式错误")
            return None
        
        if stock_data is None or stock_data.empty:
            print("未获取到股票数据，请检查股票代码或日期范围")
            return None
            
        print(f"获取到 {len(stock_data)} 条数据")
        
        # 检查数据列是否存在
        required_columns = ['开盘', '收盘', '最低', '最高', '日期']
        missing_columns = [col for col in required_columns if col not in stock_data.columns]
        
        if missing_columns:
            print(f"数据缺少必要列: {missing_columns}")
            print(f"实际数据列: {list(stock_data.columns)}")
            return None
        
        # 准备K线图数据
        data = []
        dates = []
        
        for index, row in stock_data.iterrows():
            try:
                # [开盘, 收盘, 最低, 最高]
                open_price = float(row['开盘'])
                close_price = float(row['收盘'])
                low_price = float(row['最低'])
                high_price = float(row['最高'])
                
                data.append([open_price, close_price, low_price, high_price])
                
                # 处理日期格式
                if hasattr(row['日期'], 'strftime'):
                    dates.append(row['日期'].strftime('%Y-%m-%d'))
                else:
                    dates.append(str(row['日期']))
                    
            except (ValueError, TypeError) as e:
                print(f"数据转换错误，跳过第 {index} 行: {e}")
                continue

        if not data:
            print("没有有效的K线数据")
            return None

        # 创建K线图
        kline = (
            Kline()
            .add_xaxis(dates)
            .add_yaxis("日K线", data)
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"{stock_code} 股票日K线图"),
                xaxis_opts=opts.AxisOpts(is_scale=True),
                yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, 
                        areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    )
                ),
                datazoom_opts=[
                    opts.DataZoomOpts(is_show=True, type_="inside"),
                    opts.DataZoomOpts(
                        is_show=True, 
                        type_="slider", 
                        xaxis_index=[0], 
                        range_start=0, 
                        range_end=100
                    )
                ],
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                legend_opts=opts.LegendOpts(is_show=True)
            )
        )

        # 根据运行环境选择合适的渲染方式
        if is_notebook_environment():
            print("检测到Jupyter环境，使用notebook渲染")
            try:
                kline.render_notebook()
                print("图表已在notebook中渲染")
            except Exception as e:
                print(f"notebook渲染失败: {e}")
                print("尝试生成HTML文件...")
                render_html_file(kline, stock_code)
        else:
            render_html_file(kline, stock_code)

        return kline
                
    except Exception as e:
        print(f"创建K线图时发生错误: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        print("\n请检查:")
        print("1. 是否已安装 akshare 和 pyecharts")
        print("2. 网络连接是否正常")
        print("3. 股票代码是否正确")
        return None

def render_html_file(kline, stock_code):
    """渲染HTML文件"""
    try:
        output_file = f"{stock_code}_kline.html"
        kline.render(output_file)
        print(f"K线图已保存到: {output_file}")
        
        # 尝试在浏览器中打开
        try:
            import webbrowser
            file_path = os.path.abspath(output_file)
            webbrowser.open(f"file://{file_path}")
            print("正在浏览器中打开图表...")
        except Exception as e:
            print(f"无法自动打开浏览器: {e}")
            print(f"请手动打开文件: {os.path.abspath(output_file)}")
    except Exception as e:
        print(f"生成HTML文件失败: {e}")

def is_notebook_environment():
    """检测是否在Jupyter Notebook环境中运行"""
    try:
        # 检查是否有IPython
        from IPython import get_ipython
        if get_ipython() is not None:
            return True
    except ImportError:
        pass
    
    # 检查环境变量
    if 'JPY_PARENT_PID' in os.environ:
        return True
        
    return False

def show_stock_data_info(stock_code="300674"):
    """显示股票数据信息"""
    try:
        print("正在获取股票数据信息...")
        stock_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq", start_date="20250101")

        if stock_data is None or stock_data.empty:
            print("未获取到股票数据")
            return
            
        print("=== 股票数据信息 ===")
        print(f"数据条数: {len(stock_data)}")
        print(f"数据列: {list(stock_data.columns)}")
        print("\n最近5天数据:")
        print(stock_data.tail().to_string(index=False))
        
        if not stock_data.empty:
            try:
                min_price = stock_data['最低'].min()
                max_price = stock_data['最高'].max()
                latest_close = stock_data['收盘'].iloc[-1]
                
                print(f"\n价格区间: {min_price:.2f} - {max_price:.2f}")
                print(f"最新收盘价: {latest_close:.2f}")
            except Exception as e:
                print(f"计算价格统计时出错: {e}")
            
    except Exception as e:
        print(f"获取股票数据时发生错误: {e}")
        print("详细错误信息:")
        traceback.print_exc()

def main():
    """主函数"""
    while True:
        try:
            input_stock_code = input("请输入股票代码（默认为300674，输入quit退出）: ") or "300674"
            if input_stock_code.lower() == "quit":
                print("退出程序")
                break
            
            # 显示股票数据信息
            show_stock_data_info(input_stock_code)
            print("\n" + "="*50)
            
            # 创建K线图
            kline = create_stock_kline_chart(stock_code=input_stock_code)
            
            if kline is not None:
                print("✅ K线图创建成功!")
            else:
                print("❌ K线图创建失败!")
                
        except KeyboardInterrupt:
            print("\n用户中断，退出程序")
            break
        except Exception as e:
            print(f"发生错误: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    main()