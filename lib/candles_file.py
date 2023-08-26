import ccxt
from datetime import datetime
import ndjson

class CandlesFile:
	def __init__(self, symbol, save_file):
		self.symbol = symbol
		self.save_file = save_file

	# 1分足のデータをリアルタイムで取得してファイル保存
	def save_latest_price(self):
		# 最新のろうそく足取得
		latest_candle = self.__get_latest_candle_data()
		# ファイルに書き込む
		if latest_candle is not None:
			self.__save(latest_candle)

		return True

	def __get_latest_candle_data(self):
		candles = []
		base = ccxt.bybit()
		while candles == []:
			try:
				candles = base.fetch_ohlcv(
					symbol=self.symbol,     # 暗号資産[通貨]
					timeframe = '1m',    # 時間足('1m', '5m', '1h', '1d')
					limit=1,           # 取得件数(デフォルト:100、最大:500)
					params={}             # 各種パラメータ
				)
			except:
				print("価格取得でエラー発生 : ")
				print("5秒待機してやり直します")
				time.sleep(5)
		
		return candles[0]

	def __save(self,candle):
		price = {
			"close_time" : int(candle[0] / 1000),
			"close_time_dt" : datetime.fromtimestamp(candle[0] / 1000).strftime('%Y/%m/%d %H:%M'),
			"open_price" : candle[1],
			"high_price" : candle[2],
			"low_price" : candle[3],
			"close_price": candle[4]
		}

		with open(self.save_file, 'a') as f:
			writer = ndjson.writer(f)
			writer.writerow(price)
