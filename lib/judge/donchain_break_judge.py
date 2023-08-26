class DonchainBreakJudge:
  def __init__(self):
		self.signal = ''
		self.candle = ''
		self.ma = ''
		self.ma_buffer = ''
		self.hige_buffer = ''
		self.position = ''

  def set_params(self, signal, candle, ma, ma_buffer, hige_buffer, position):
		self.signal = signal
		self.candle = candle
		self.ma = ma
		self.ma_buffer = ma_buffer
		self.hige_buffer = hige_buffer
		self.position = position

  def judge_open_signal(self):
    

  