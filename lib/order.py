import os
import ccxt
from record import Record

class Order:
  def __init__(self,symbol):
    self.exist = False
    self.side = ""
    self.price = 0
    self.count = 0
    self.symbol = symbol

  def entry(self, order_type, signal, record, lot, test=False):
    if signal.is_buy():
      if type(record) is Record:
        record.set_log("{0}$で買いを入れます\n".format(signal.price))
      self.buy(
        type=order_type,
        price=signal.price,
        lot=lot,
        test=test,
      )

    if signal.is_sell():
      if type(record) is Record:
        record.set_log("{0}$で売りを入れます\n".format(signal.price))
      self.sell(
        type=order_type,
        price=signal.price,
        test=test,
      )

    return True

  def buy(self, type, price, lot, test=False):
    if not test:
      self.__create_order_from_bybit(
        side="buy",
        type=type,
        price=price,
        amount=lot,
      )

    self.exist = True
    self.side = "BUY"
    self.price = price

  def sell(self, type, price, test=False):
    # TODO 売注文コード
    # if not test:
    self.exist = True
    self.side = "SELL"
    self.price = price

  def check_order(self, position):
    # 注文状況を確認して通っていたら以下を実行
    # 一定時間で注文が通っていなければキャンセルする

    # 今は成行注文にするから強制的に注文が通ったことにしている
    if self.exist:
      self.exist = False
      self.count = 0
      position.exist = True
      position.side = self.side
      position.price = self.price
    
    return True

  # https://docs.ccxt.com/#/spec?id=createorder
  def __create_order_from_bybit(self,type,side,price,amount ):
    bybit = ccxt.bybit()
    bybit.apiKey = os.getenv("BYBIT_API_KEY")
    bybit.secret = os.getenv("BYBIT_SECRET")
    order = bybit.create_order(
      symbol = self.symbol,
      type=type,
      side=side,
      price=price,
      amount=amount,
    )

    return order
