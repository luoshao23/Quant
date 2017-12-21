
import time
start = '2016-08-01'                       # 回测起始时间
end = '2017-08-19'                         # 回测结束时间
universe = DynamicUniverse('SH50')        # 证券池，支持股票和基金、期货
benchmark = 'HS300'                        # 策略参考基准
freq = 'm'                                 # 'd'表示使用日频率回测，'m'表示使用分钟频率回测
refresh_rate = (1, ['09:40', '14:40'])                           # 执行handle_data的时间间隔


accounts = {
    'fantasy_account': AccountConfig(account_type='security', capital_base=10000000)
}

def initialize(context):                   # 初始化策略运行环境
    context.counts = 0
    bold = Signal('BollDown')
    bolu = Signal('BollUp')
    ma20 = Signal('MA20')
    context.signal_generator = SignalGenerator(bold, bolu, ma20)


def handle_data(context):                  # 核心策略逻辑
    counts = context.counts
    last = context.previous_date.strftime('%Y-%m-%d')
    universe = context.get_universe(exclude_halt=True)
    account = context.get_account('fantasy_account')

    position_list = account.get_positions(exclude_halt=False).keys()

    data = context.history(universe, ['BollDown', 'BollUp','MA20'], 1, freq='1d', style='tas') [last]

    if counts <= 1:
        print data['BollDown'].loc['601328.XSHG']
        print type(data['BollDown'].loc['601328.XSHG'])
    counts += 1
    context.counts = counts

    for stock in universe:
        current_price = context.current_price(stock)
        if (current_price - data['BollDown'].loc[stock])/(data['MA20'].loc[stock] - data['BollDown'].loc[stock]) <= 0.1:
            account.order_pct(stock, 0.05)

        if (current_price - data['MA20'].loc[stock])/(data['BollUp'].loc[stock] - data['MA20'].loc[stock]) >= 0.7:
            if stock in position_list:
                account.order_to(stock, 0)

    # for stock in universe:
    #     if context.current_price(stock) > float(data):
    #         account.order_pct(stock, 0.05)
