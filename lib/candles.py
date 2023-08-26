import ndjson
import matplotlib.pyplot as plt
import pandas as pd

class Candles:
	def __init__(self, path, minutes):
		self.list = self.__get_from_file(path, minutes)

	def latest_candle(self):
		return self.list[-1]

	# ろうそく足のデータに移動平均線のデータを加える
	def add_ma(self):
		df = pd.DataFrame(self.list)
		df["5ma"] = df["close_price"].rolling(window=5).mean()
		df["10ma"] = df["close_price"].rolling(window=10).mean()
		df["20ma"] = df["close_price"].rolling(window=20).mean()
		df["50ma"] = df["close_price"].rolling(window=50).mean()
		df["100ma"] = df["close_price"].rolling(window=100).mean()
		df["200ma"] = df["close_price"].rolling(window=200).mean()

		self.list = df.to_dict(orient='records')

		return True

	def __get_from_file(self, path, minutes):
		with open(path, encoding='UTF-8') as f:
			candles = ndjson.load(f)
		
			result = []

			# 4時間足の場合、0100スタートなので、1時間分レコードを削除する
			if minutes == 240:
				for i in range(60):
					del candles[0]

			# 日足の場合、0900スタートなので、9時間分レコードを削除する
			if minutes == 60 * 24:
				for i in range(60 * 9):
					del candles[0]

			for candles in self.__split_list(candles, minutes):
				range_index = minutes
				high_prices = []
				low_prices = []

				# 想定足分なかったらスキップ
				if not len(candles) == minutes:
					continue

				for i in range(range_index):
					# 1分足の最初
					if i == 0:
						open_price = candles[i]["open_price"]
						close_time = candles[i]["close_time"]
						close_time_dt = candles[i]["close_time_dt"]
					high_prices.append(candles[i]["high_price"])
					low_prices.append(candles[i]["low_price"])
					# 1分足の最後
					if i == range_index - 1:
						result.append(
							{
								"close_time" : close_time,
								"close_time_dt" : close_time_dt,
								"open_price" : open_price,
								"high_price" : max(high_prices),
								"low_price" : min(low_prices),
								"close_price": candles[i]["close_price"]
							}
						)
						open_price = candles[i]["close_price"]

		return result

	def __split_list(_self, l, n):
		"""
		リストをサブリストに分割する
		:param l: リスト
		:param n: サブリストの要素数
		:return: 
		"""
		for idx in range(0, len(l), n):
				yield l[idx:idx + n]