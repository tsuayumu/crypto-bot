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

import requests
from datetime import datetime
import time
import matplotlib.pyplot as plt
import pandas as pd

#-----設定項目

chart_sec = 60    # n分足を使用
ma = 1440         # 過去chart_sec*ｎ足の移動平均線
wait = 0            # ループの待機時間
lot = 1             # BTCの注文枚数
slippage = 0.001    # 手数料・スリッページ

# 売買判定する関数
def judge_open_signal( data ):

	# 移動平均線よりも下に位置してる
	if data["open_price"] < data["ma"]:
		# 移動平均線を上抜ける
		if data["close_price"] > data["ma"]:
			return {
				"side" : "BUY",
				"price" : data["close_price"]
			}

	# 移動平均線よりも上に位置してる
	if data["open_price"] > data["ma"]:
		# 移動平均線を下抜ける
		if data["close_price"] < data["ma"]:
			return {
				"side" : "SELL",
				"price" : data["close_price"]
			}
	
	return {"side" : None , "price":0}

# 判定してエントリー注文を出す関数
def entry_signal( data, flag ):
	signal = judge_open_signal( data )
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


def judge_close_signal( data, flag ):
	# 買いのポジションが入ってる
	if flag["position"]["side"] == "BUY":
		# ろうそく足が赤
		if data["open_price"] > data["close_price"]:
			return {
				"side" : "SELL",
				"price" : data["close_price"]
			}
	
	# 売りのポジションが入ってる
	if flag["position"]["side"] == "SELL":
		# ろうそく足が緑
		if data["open_price"] < data["close_price"]:
			return {
				"side" : "BUY",
				"price" : data["close_price"]
			}

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
	df["ma"] = df["close_price"].rolling(window=int(ma/chart_sec)).mean()
	
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
	if i < int(ma/chart_sec):
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