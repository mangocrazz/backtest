import matplotlib.pyplot as plt

def plot_results(ret_frame_test):
    plt.figure(figsize=(8,6))
    plt.plot(ret_frame_test['持仓净值（累计）'], 'b-', label='Test curve')
    plt.legend()
    plt.grid()
    plt.xlabel('Factor')
    plt.ylabel('Return')
    plt.show()
