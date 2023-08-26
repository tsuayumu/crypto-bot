import ccxt
import os
from pybit.unified_trading import HTTP
from record import Record

class Position:
  def __init__(self,symbol):
    self.exist = False
    self.side = ""
    self.price = 0
    self.count = 0
    self.symbol = symbol

  def is_buy(self):
    return self.side == "BUY"

  def is_sell(self):
    return self.side == "SELL"

  def close(self, signal, record, latest_candle, lot, slippage, test=False):
    self.count += 1
    if self.is_buy():
      if signal.is_sell():
        if type(record) is Record:
          record.set_log("{0}$あたりで成行注文を出して買いポジションを決済します\n".format(signal.price))
        self.sell_close(
          type=type,
          price=signal.price,
          test=test
        )
        if type(record) is Record:
          record.set_for_close(latest_candle, lot, slippage, self)
        
    if self.is_sell():
      if signal.is_buy():
        if type(record) is Record:
          record.set_log("{0}$あたりで成行注文を出して売りポジションを決済します\n".format(signal.price))
        self.buy_close(
          type=type,
          price=signal.price,
          test=test
        )
        if type(record) is Record:
          record.set_for_close(latest_candle, lot, slippage, self)
        
    return True

  def sell_close(self, type, price, test=False):
    if not test:
      order = self.__sell_all_from_bybit(
        self.symbol.split("/")[0],
        type,
        'sell',
        price,
      )

    self.exist = False
    self.count = 0
  
  def buy_close(self, type, price, test=False):
    # if not test:
    # order = self.__buy_all_from_bybit(
    #   self.symbol.split("/")[0],
    #   type,
    #   'buy',
    #   price,
    # )
    self.exist = False
    self.count = 0

  def __sell_all_from_bybit(self, coin, type, side, price):
    session = HTTP(
      api_key=os.getenv("BYBIT_API_KEY"),
      api_secret=os.getenv("BYBIT_SECRET"),
    )

    balance = session.get_coins_balance(
      accountType="SPOT",
      coin=coin,
    )['result']['balance'][0]['walletBalance']

    bybit = ccxt.bybit()
    bybit.apiKey = os.getenv("BYBIT_API_KEY")
    bybit.secret = os.getenv("BYBIT_SECRET")
    order = bybit.create_order(
      symbol = self.symbol,
      type=type,
      side=side,
      price=price,
      amount=balance,
    )

    return order


  