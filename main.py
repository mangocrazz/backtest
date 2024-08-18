from src.data_processing import generate_etime_close_data_divd_time
from src.backtest import backtest
from src.utils import plot_results

def main():
    # 生成数据
    data = generate_etime_close_data_divd_time('2020-01-01', '2021-01-01', '000001.SH', 'd')
    
    # 进行回测
    result = backtest(data, '000001.SH', 'd', 1)
    
    # 绘图
    plot_results(result)

if __name__ == "__main__":
    main()
