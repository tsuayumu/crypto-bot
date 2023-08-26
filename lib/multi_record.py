import numpy as np
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

class MultiRecord:
  def __init__(self):
    self.date = []
    self.profit = []
    self.return_rate = []
    self.side = []
    self.holding_periods = []
    self.slippage = []

    self.result_count = []
    self.result_winRate = []
    self.result_returnRate = []
    self.result_drawdown = []
    self.result_profitFactor = []
    self.result_gross = []


  # 各トレードのパフォーマンスを記録する関数
  def add(self,position,candle,lot,slippage):
    # 取引手数料等の計算
    entry_price = position.price
    exit_price = round(candle["close_price"] * lot)
    trade_cost = round( exit_price * slippage )
    self.slippage.append(trade_cost)
    
    # 手仕舞った日時と保有期間を記録
    self.date.append(candle["close_time_dt"])
    self.holding_periods.append( position.count )
    
    # 値幅の計算
    buy_profit = exit_price - entry_price - trade_cost
    sell_profit = entry_price - exit_price - trade_cost
    
    # 利益が出てるかの計算
    if position.is_buy():
      self.side.append( "BUY" )
      self.profit.append( buy_profit )
      self.return_rate.append( round( buy_profit / entry_price * 100, 4 ))
    
    if position.is_sell():
      self.side.append( "SELL" )
      self.profit.append( sell_profit )
      self.return_rate.append( round( sell_profit / entry_price * 100, 4 ))
    
    return True

  # バックテストの集計用の関数
  def backtest(self):
    # 成績を記録したpandas DataFrameを作成
    records = pd.DataFrame({
      "Date"     :  pd.to_datetime(self.date),
      "Profit"   :  self.profit,
      "Side"     :  self.side,
      "Rate"     :  self.return_rate,
      "Periods"  :  self.holding_periods,
      "Slippage" :  self.slippage
    })
    
    # 総損益の列を追加する
    records["Gross"] = records.Profit.cumsum()
    
    # 最大ドローダウンの列を追加する
    records["Drawdown"] = records.Gross.cummax().subtract(records.Gross)
    records["DrawdownRate"] = round(records.Drawdown / records.Gross.cummax() * 100,1)

    print("バックテストの結果")
    print("-----------------------------------")
    print("総合の成績")
    print("-----------------------------------")
    print("全トレード数       :  {}回".format(len(records) ))
    print("勝率               :  {}％".format(round(len(records[records.Profit>0]) / len(records) * 100,1)))
    print("平均リターン       :  {}％".format(round(records.Rate.mean(),2)))
    print("平均保有期間       :  {}足分".format( round(records.Periods.mean(),1) ))
    print("")
    print("最大の勝ちトレード :  {}円".format(records.Profit.max()))
    print("最大の負けトレード :  {}円".format(records.Profit.min()))
    print("最大ドローダウン   :  {0}円 / {1}％".format(-1 * records.Drawdown.max(), -1 * records.DrawdownRate.loc[records.Drawdown.idxmax()]  ))
    print("利益合計           :  {}円".format( records[records.Profit>0].Profit.sum() ))
    print("損失合計           :  {}円".format( records[records.Profit<0].Profit.sum() ))
    print("")
    print("最終損益           :  {}円".format( records.Profit.sum() ))
    print("手数料合計         :  {}円".format( -1 * records.Slippage.sum() ))

    try:
      profit_factor = round( -1 * (records[records.Profit>0].Profit.sum() / records[records.Profit<0].Profit.sum()) ,2)
    except:
      profit_factor = 0

    self.result_count.append(len(records))
    self.result_winRate.append(round(len(records[records.Profit>0]) / len(records) * 100,1))
    self.result_returnRate.append(round(records.Rate.mean(),2))
    self.result_drawdown.append(-1 * records.Drawdown.max())
    self.result_profitFactor.append(records.Profit.sum())
    self.result_gross.append(profit_factor)

  def result(self):
    return {
      "トレード回数" : self.result_count,
      "勝率" : self.result_winRate,
      "平均リターン" : self.result_returnRate,
      "ドローダウン" : self.result_drawdown,
      "PF" : self.result_profitFactor,
      "最終損益" : self.result_gross
    }

  def headers(self):
    return [
      "トレード回数",
      "勝率",
      "平均リターン",
      "ドローダウン",
      "PF",
      "最終損益"
    ]

  def set_log(self, log_text):
    # 特に記録しないがインタフェースだけ定義
    return True
