# 移動平均線による売買ロジック
# 移動平均線を実体線で下から上に越えたら買いを入れる
# ろうそく足が赤色になった時点で売る
# 移動平均線を実体線で上から下に越えたら売りを入れる
# ろうそく足が緑色になった時点で売る

from lib.get_candle_data import get_candle_data_from_file
from lib.log_price import log_price
from lib.check_order import check_order
from lib.records import records
from lib.backtest import backtest

from sma.lib.judge_open_signal import judge_open_signal
from sma.lib.judge_close_signal import judge_close_signal

import requests
from datetime import datetime
import time
import matplotlib.pyplot as plt
import pandas as pd

#-----設定項目

chart_sec = 240    # n分足を使用
ma = 5         # 過去chart_sec*ｎ足の移動平均線
ma_buffer = 50 # 移動平均線のバッファ
hige_buffer = 50 # ひげが長い場合に売買しないためのバッファ
wait = 0            # ループの待機時間
lot = 1             # BTCの注文枚数
slippage = 0.001    # 手数料・スリッページ

# 判定してエントリー注文を出す関数
def entry_signal( data, flag ):
	signal = judge_open_signal( data, ma_buffer,hige_buffer )
	if signal["side"] == "BUY":
		flag["records"]["log"].append("移動平均線を上抜けました、{0}$で買いを入れます\n".format(signal["price"]))

		# ここに買い注文のコードを入れる
		
		flag["order"]["exist"] = True
		flag["order"]["side"] = "BUY"
		flag["order"]["price"] = round(signal["price"] * lot)

	if signal["side"] == "SELL":
		flag["records"]["log"].append("移動平均線を下抜けました、{0}$で売りを入れます\n".format(signal["price"]))

		# ここに売り注文のコードを入れる
		
		flag["order"]["exist"] = True
		flag["order"]["side"] = "SELL"
		flag["order"]["price"] = round(data["close_price"] * lot)

	return flag

# 手仕舞いのシグナルが出たら決済の成行注文を出す関数
def close_position( data,flag ):
	
	flag["position"]["count"] += 1
	signal = judge_close_signal( data,flag )
	
	if flag["position"]["side"] == "BUY":
		if signal:
			if signal["side"] == "SELL":
				flag["records"]["log"].append("ろうそく足が赤だったので、{0}$あたりで成行注文を出して買いポジションを決済します\n".format(signal["price"]))
				
				# 決済の成行注文コードを入れる
				
				records( flag,data,lot,slippage )
				flag["position"]["exist"] = False
				flag["position"]["count"] = 0
			
	if flag["position"]["side"] == "SELL":
		if signal:
			if signal["side"] == "BUY":
				flag["records"]["log"].append("ろうそく足が緑だったので、{0}$あたりで成行注文を出して売りポジションを決済します\n".format(signal["price"]))
				
				# 決済の成行注文コードを入れる
				
				records( flag,data,lot,slippage )
				flag["position"]["exist"] = False
				flag["position"]["count"] = 0
			
	return flag	

def add_ma(price):
	df = pd.DataFrame(price)
	df["ma"] = df["close_price"].rolling(window=ma).mean()
	
	return df.to_dict(orient='records')

# ここからメイン処理

# 価格チャートを取得
# [
# 	{
# 		'close_time': 1627052400000,
# 		'close_time_dt': '2021/07/24 00:00',
# 		'open_price': 32486.03,
# 		'high_price': 32492.81,
# 		'low_price': 32439.84,
# 		'close_price': 32455.67,
# 	},・・・
# ]
price = get_candle_data_from_file("./candle_data/btc_usdt.json", chart_sec)

price = add_ma(price)

flag = {
	"order":{
		"exist" : False,
		"side" : "",
		"price" : 0,
		"count" : 0
	},
	"position":{
		"exist" : False,
		"side" : "",
		"price": 0,
		"count":0
	},
	"records":{
		"buy-count": 0,
		"buy-winning" : 0,
		"buy-return":[],
		"buy-profit": [],
		"buy-holding-periods":[],
		
		"sell-count": 0,
		"sell-winning" : 0,
		"sell-return":[],
		"sell-profit":[],
		"sell-holding-periods":[],
		
		"drawdown": 0,
		"date":[],
		"gross-profit":[0],
		"slippage":[],
		"log":[]
	}
}


i = 0

# dataは今の価格
while i < len(price):

	# 過去〇〇足分の安値・高値データを準備する
	if i < ma:
		flag = log_price(price[i],flag)
		time.sleep(wait)
		i += 1
		continue
	
	data = price[i]
	flag = log_price(data,flag)
	
	
	if flag["order"]["exist"]:
		flag = check_order( flag )

	if flag["position"]["exist"]:
		flag = close_position( data,flag )
	else:
		flag = entry_signal( data, flag )

	i += 1
	time.sleep(wait)


print("--------------------------")
print("テスト期間：")
print("開始時点 : " + str(price[0]["close_time_dt"]))
print("終了時点 : " + str(price[-1]["close_time_dt"]))
print(str(len(price)) + "件のローソク足データで検証")
print("--------------------------")

backtest(flag)