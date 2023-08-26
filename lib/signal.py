class Signal:
  def __init__(self):
    self.side = ""
    self.price = 0

  def is_buy(self):
    return self.side == "BUY"

  def is_sell(self):
    return self.side == "SELL"

  def is_exists(self):
    return self.side != ""

  def set_buy(self, price):
    self.side = "BUY"
    self.price = price

  def set_sell(self, price):
    self.side = "SELL"
    self.price = price
  
  def reset(self):
    self.side = ""
    self.price = 0
