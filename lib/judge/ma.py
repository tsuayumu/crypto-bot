
class MaJudge:
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

	# 売買判定する関数
	def judge_open_signal(self):
		signal = self.signal 
		candle = self.candle 
		ma = self.ma 
		ma_buffer = self.ma_buffer 
		hige_buffer = self.hige_buffer

		# 移動平均線よりも下に位置してる
		if candle["open_price"] < candle["{}ma".format(ma)]:
			# 移動平均線を上抜ける
			if candle["close_price"] > candle["{}ma".format(ma)] + ma_buffer:
				# 上ひげが長い時は入らない
				if candle["high_price"] - candle["close_price"] < hige_buffer:
					# 上に移動平均線がいっぱいある時は入らない
					# if candle["close_price"] > candle["20ma"]:
					return signal.set_buy(candle["close_price"])

		# 移動平均線よりも上に位置してる
		if candle["open_price"] > candle["{}ma".format(ma)]:
			# 移動平均線を下抜ける
			if candle["close_price"] < candle["{}ma".format(ma)] - ma_buffer:
				# 下ひげが長い時は入らない
				if candle["close_price"] - candle["low_price"] < hige_buffer:
					# 上に移動平均線がいっぱいある時は入らない
					# if candle["close_price"] < candle["20ma"]:
					return signal.set_sell(candle["close_price"])

		signal.reset()

	def judge_close_signal(self):
		signal =self.signal
		candle =self.candle
		position =self.position

		# 買いのポジションが入ってる
		if position.is_buy():
			# ろうそく足が赤
			if candle["open_price"] > candle["close_price"]:
				return signal.set_sell(candle["close_price"])
		
		# 売りのポジションが入ってる
		if position.is_sell():
			# ろうそく足が緑
			if candle["open_price"] < candle["close_price"]:
				return signal.set_buy(candle["close_price"])

