import numpy as np
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

class Record:
  def __init__(self):
    self.buy_count = 0
    self.buy_winning = 0
    self.buy_return = []
    self.buy_profit = []
    self.buy_holding_periods = []

    self.sell_count = 0
    self.sell_winning = 0
    self.sell_return = []
    self.sell_profit = []
    self.sell_holding_periods = []

    self.drawdown = 0
    self.date = []
    self.gross_profit = [0]
    self.slippage = []
    self.log = []

  def set_log(self, log_text):
    self.log.append(log_text)

  def set_for_close(self, candle, lot, slippage, position):
    # 取引手数料等の計算
    entry_price = position.price
    exit_price = round(candle["close_price"] * lot)
    trade_cost = round( exit_price * slippage )

    self.set_log("スリッページ・手数料として " + str(trade_cost) + "$を考慮します\n")
    self.slippage.append(trade_cost)

    # 手仕舞った日時の記録
    self.date.append(candle["close_time_dt"])
    
    # 値幅の計算
    buy_profit = exit_price - entry_price - trade_cost
    sell_profit = entry_price - exit_price - trade_cost
    
    # 利益が出てるかの計算
    if position.is_buy():
      self.buy_count += 1
      self.buy_profit.append( buy_profit )
      self.gross_profit.append( self.gross_profit[-1] + buy_profit )
      self.buy_return.append( round( buy_profit / entry_price * 100, 4 ))
      self.buy_holding_periods.append( position.count )

      if buy_profit  > 0:
        self.buy_winning += 1
        self.set_log(str(buy_profit) + "$の利益です\n")
      else:
        self.set_log(str(buy_profit) + "$の損失です\n")
    
    if position.is_sell():
      self.sell_count += 1
      self.sell_profit.append( sell_profit )
      self.gross_profit.append( self.gross_profit[-1] + sell_profit )
      self.sell_return.append( round( sell_profit / entry_price * 100, 4 ))
      self.sell_holding_periods.append( position.count )

      if sell_profit > 0:
        self.sell_winning += 1
        self.set_log(str(sell_profit) + "$の利益です\n")
      else:
        self.set_log(str(sell_profit) + "$の損失です\n")
    
    # ドローダウンの計算
    drawdown =  max(self.gross_profit) - self.gross_profit[-1] 
    if  drawdown  > self.drawdown:
      self.drawdown = drawdown
    
    return True

  def backtest(self):
    buy_gross_profit = np.sum(self.buy_profit)
    sell_gross_profit = np.sum(self.sell_profit)
    
    print("バックテストの結果")
    print("--------------------------")
    print("買いエントリの成績")
    print("--------------------------")
    print("トレード回数     :  {}回".format(self.buy_count ))
    print("勝率             :  {}％".format(round(self.buy_winning / self.buy_count * 100,1)))
    print("平均リターン     :  {}％".format(round(np.average(self.buy_return),2)))
    print("総損益           :  {}$".format( np.sum(self.buy_profit) ))
    print("平均保有期間     :  {}足分".format( round(np.average(self.buy_holding_periods),1) ))
    
    if self.sell_count > 0:
      print("--------------------------")
      print("売りエントリの成績")
      print("--------------------------")
      print("トレード回数     :  {}回".format(self.sell_count ))
      print("勝率             :  {}％".format(round(self.sell_winning / self.sell_count * 100,1)))
      print("平均リターン     :  {}％".format(round(np.average(self.sell_return),2)))
      print("総損益           :  {}$".format( np.sum(self.sell_profit) ))
      print("平均保有期間     :  {}足分".format( round(np.average(self.sell_holding_periods),1) ))
    
    print("--------------------------")
    print("総合の成績")
    print("--------------------------")
    print("最大ドローダウン :  {0}$ / {1}％".format(-1 * self.drawdown, -1 * round(self.drawdown/max(self.gross_profit)*100,1)  ))
    print("総損益           :  {}$".format( self.gross_profit[-1] ))
    print("手数料合計       :  {}$".format( -1 * np.sum(self.slippage) ))
    
    # ログファイルの出力
    file =  open("/Users/tsuda_ayumu/Develop/crypto_bot/log/{0}-log.txt".format(datetime.now().strftime("%Y-%m-%d-%H-%M")),'wt',encoding='utf-8')
    file.writelines(self.log)

    # 損益曲線をプロット
    del self.gross_profit[0]
    date_list = pd.to_datetime( self.date )
    
    plt.plot( date_list, self.gross_profit )
    plt.xlabel("Date")
    plt.ylabel("Balance")
    plt.xticks(rotation=50) # X軸の目盛りを50度回転
    
    plt.show()
