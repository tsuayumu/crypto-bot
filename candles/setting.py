# -*- coding: utf-8 -*-
# 現在から指定の期間までのデータを取得して、終わったら最新のデータを取得し続けるプログラム

import sys
sys.path.insert(0, "../lib")
import ccxt
from pprint import pprint
from datetime import datetime
import time
import ndjson
import pandas as pd

START_TIME = datetime(2023, 8, 24)
FILE_PATH = 'candles.ndjson'

def get_price(file_path="",min='1m', since=0, until=0):
	base = ccxt.bybit()

	df = pd.read_json(file_path, lines=True)
	try:
		close_time_dt_list = df['close_time_dt'].to_list()
	except:
		print("データがなかった")
		close_time_dt_list = []

	with open(file_path, 'a') as f:
		writer = ndjson.writer(f)

		while since < until:
			if skip_judge(since,close_time_dt_list):
				print("スキップします : " + fromtimestamp(since))
			else:
				try:
					candles = base.fetch_ohlcv(
						symbol='BTC/USDT',     # 暗号資産[通貨]
						timeframe = min,    # 時間足('1m', '5m', '1h', '1d')
						since=since,           # 取得開始時刻(Unix Timeミリ秒)
						limit=500,           # 取得件数(デフォルト:100、最大:500)
						params={}             # 各種パラメータ
					)
				except:
					print("価格取得でエラー発生 : ")
					print("10秒待機してやり直します")
					time.sleep(10)
					continue

				print("-----取得中-----")
				print("先頭データ : " +  fromtimestamp(candles[0][0]))
				print("末尾データ : " + fromtimestamp(candles[-1][0]))
				print("---------------")
				
				if candles is not None:
					for candle in candles:
						if fromtimestamp(candle[0]) in close_time_dt_list:
							print("すでにデータがあるのでスキップ: " + fromtimestamp(candle[0]))
						else:
							writer.writerow(
								{
									"close_time" : candle[0],
									"close_time_dt" : fromtimestamp(candle[0]),
									"open_price" : candle[1],
									"high_price" : candle[2],
									"low_price" : candle[3],
									"close_price": candle[4]
								}
							)
				time.sleep(2)

			since = since + (500 * 60 * 1000)

	return True

def fromtimestamp(target_time):
	return datetime.fromtimestamp(target_time / 1000).strftime('%Y/%m/%d %H:%M')

def skip_judge(since,close_time_dt_list):
	inspect_time = since + 60000
	for i in range(500):
		if fromtimestamp(inspect_time) in close_time_dt_list:
			inspect_time = inspect_time + 60000
		else:
			return False
	return True

def to_ms(datetime_object):
	return int(time.mktime(datetime_object.timetuple()) * 1000)

since = START_TIME
until = datetime.now()

get_price(
	file_path=FILE_PATH,
	min='1m',
	since=to_ms(since),
	until=to_ms(until)
)

while True:
	time.sleep(60)

	# 取りこぼしがあるかもなのでバッファを持つ
	since = until - 60000 * 60
	until = datetime.now()

	try:
		get_price(
			file_path=FILE_PATH,
			min='1m',
			since=to_ms(since),
			until=to_ms(until)
		)
	except:
		print("価格取得でエラー発生 : " + fromtimestamp(since) + " ~ " + fromtimestamp(until))

