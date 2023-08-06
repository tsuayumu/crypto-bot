from lib.get_candle_data import get_candle_data_from_file

import requests
from datetime import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sma.lib.judge_open_signal import judge_open_signal
from sma.lib.judge_close_signal import judge_close_signal

#-----設定項目

wait = 0            # ループの待機時間
lot = 1             # BTCの注文枚数
slippage = 0.001    # 手数料・スリッページ

# バックテストのパラメーター設定
#---------------------------------------------------------------------------------------------
chart_sec_list  = [ 5, 15, 60, 120, 240, 720, 1440, 2880 ] 
ma_list = [5,10,20,50,100,200]
ma_buffer_list = [0, 50, 100, 200, 400] # 移動平均線のバッファ
hige_buffer_list = [10,25,50,100,200,300,100000] # ひげが長い場合に売買しないためのバッファ
#---------------------------------------------------------------------------------------------

# 判定してエントリー注文を出す関数
def entry_signal( data, flag, ma_buffer,hige_buffer ):
	signal = judge_open_signal( data,ma_buffer,hige_buffer )
	if signal["side"] == "BUY":
		# ここに買い注文のコードを入れる
		
		flag["order"]["exist"] = True
		flag["order"]["side"] = "BUY"
		flag["order"]["price"] = round(signal["price"] * lot)

	if signal["side"] == "SELL":
		# ここに売り注文のコードを入れる
		
		flag["order"]["exist"] = True
		flag["order"]["side"] = "SELL"
		flag["order"]["price"] = round(data["close_price"] * lot)

	return flag



# サーバーに出した注文が約定したか確認する関数
# ここでは注文を通している
def check_order( flag ):
	
	# 注文状況を確認して通っていたら以下を実行
	# 一定時間で注文が通っていなければキャンセルする
	
	flag["order"]["exist"] = False
	flag["order"]["count"] = 0
	flag["position"]["exist"] = True
	flag["position"]["side"] = flag["order"]["side"]
	flag["position"]["price"] = flag["order"]["price"]
	
	return flag

# 手仕舞いのシグナルが出たら決済の成行注文を出す関数
def close_position( data,flag ):
	
	flag["position"]["count"] += 1
	signal = judge_close_signal( data,flag )
	
	if flag["position"]["side"] == "BUY":
		if signal:
			if signal["side"] == "SELL":				
				# 決済の成行注文コードを入れる
				
				records( flag,data )
				flag["position"]["exist"] = False
				flag["position"]["count"] = 0
			
	if flag["position"]["side"] == "SELL":
		if signal:
			if signal["side"] == "BUY":
				# 決済の成行注文コードを入れる
				
				records( flag,data )
				flag["position"]["exist"] = False
				flag["position"]["count"] = 0
			
	return flag


# 各トレードのパフォーマンスを記録する関数
def records(flag,data):
	
	# 取引手数料等の計算
	entry_price = flag["position"]["price"]
	exit_price = round(data["close_price"] * lot)
	trade_cost = round( exit_price * slippage )
	flag["records"]["slippage"].append(trade_cost)
	
	# 手仕舞った日時と保有期間を記録
	flag["records"]["date"].append(data["close_time_dt"])
	flag["records"]["holding-periods"].append( flag["position"]["count"] )
	
	# 値幅の計算
	buy_profit = exit_price - entry_price - trade_cost
	sell_profit = entry_price - exit_price - trade_cost
	
	# 利益が出てるかの計算
	if flag["position"]["side"] == "BUY":
		flag["records"]["side"].append( "BUY" )
		flag["records"]["profit"].append( buy_profit )
		flag["records"]["return"].append( round( buy_profit / entry_price * 100, 4 ))
	
	if flag["position"]["side"] == "SELL":
		flag["records"]["side"].append( "SELL" )
		flag["records"]["profit"].append( sell_profit )
		flag["records"]["return"].append( round( sell_profit / entry_price * 100, 4 ))
	
	return flag

# バックテストの集計用の関数
def backtest(flag):	
	# 成績を記録したpandas DataFrameを作成
	records = pd.DataFrame({
		"Date"     :  pd.to_datetime(flag["records"]["date"]),
		"Profit"   :  flag["records"]["profit"],
		"Side"     :  flag["records"]["side"],
		"Rate"     :  flag["records"]["return"],
		"Periods"  :  flag["records"]["holding-periods"],
		"Slippage" :  flag["records"]["slippage"]
	})
	
	# 総損益の列を追加する
	records["Gross"] = records.Profit.cumsum()
	
	# 最大ドローダウンの列を追加する
	records["Drawdown"] = records.Gross.cummax().subtract(records.Gross)
	records["DrawdownRate"] = round(records.Drawdown / records.Gross.cummax() * 100,1)

	print("バックテストの結果")
	print("-----------------------------------")
	print("総合の成績")
	print("-----------------------------------")
	print("全トレード数       :  {}回".format(len(records) ))
	print("勝率               :  {}％".format(round(len(records[records.Profit>0]) / len(records) * 100,1)))
	print("平均リターン       :  {}％".format(round(records.Rate.mean(),2)))
	print("平均保有期間       :  {}足分".format( round(records.Periods.mean(),1) ))
	print("")
	print("最大の勝ちトレード :  {}円".format(records.Profit.max()))
	print("最大の負けトレード :  {}円".format(records.Profit.min()))
	print("最大ドローダウン   :  {0}円 / {1}％".format(-1 * records.Drawdown.max(), -1 * records.DrawdownRate.loc[records.Drawdown.idxmax()]  ))
	print("利益合計           :  {}円".format( records[records.Profit>0].Profit.sum() ))
	print("損失合計           :  {}円".format( records[records.Profit<0].Profit.sum() ))
	print("")
	print("最終損益           :  {}円".format( records.Profit.sum() ))
	print("手数料合計         :  {}円".format( -1 * records.Slippage.sum() ))

	try:
		profit_factor = round( -1 * (records[records.Profit>0].Profit.sum() / records[records.Profit<0].Profit.sum()) ,2)
	except:
		profit_factor = 0
	
	# バックテストの計算結果を返す
	result = {
		"トレード回数"     : len(records),
		"勝率"             : round(len(records[records.Profit>0]) / len(records) * 100,1),
		"平均リターン"     : round(records.Rate.mean(),2),
		"最大ドローダウン" : -1 * records.Drawdown.max(),
		"最終損益"         : records.Profit.sum(),
		"プロフィットファクタ―" : profit_factor
	}
	
	return result
	

def add_ma(price, chart_sec, ma):
	df = pd.DataFrame(price)
	df["ma"] = df["close_price"].rolling(window=ma).mean()
	
	return df.to_dict(orient='records')


# ここからメイン処理

# バックテストに必要な時間軸のチャートをすべて取得
price_list = {}

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
for chart_sec in chart_sec_list:
	price_list[ chart_sec ] = {}
	for ma in ma_list:
		price_list[ chart_sec ][ ma ]= get_candle_data_from_file("./candle_data/btc_usdt.json", chart_sec)
		price_list[ chart_sec ][ ma ] = add_ma(price_list[ chart_sec ][ ma ], chart_sec, ma)

# テストごとの各パラメーターの組み合わせと結果を記録する配列を準備
param_chart_sec = []
param_ma = []
param_ma_buffer = []
param_hige_buffer = []

result_count = []
result_winRate = []
result_returnRate = []
result_drawdown = []
result_profitFactor = []
result_gross = []

# 総当たりのためのfor文の準備
combinations = [(chart_sec, ma, ma_buffer, hige_buffer)
	for chart_sec in chart_sec_list
	for ma in ma_list
	for ma_buffer in ma_buffer_list
	for hige_buffer in hige_buffer_list]

for chart_sec, ma, ma_buffer, hige_buffer in combinations:

	price = price_list[ chart_sec ][ ma ]
	i = 0

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
			"date":[],
			"profit":[],
			"return":[],
			"side":[],
			"holding-periods":[],
			"slippage":[]
		}
	}

	# dataは今の価格
	while i < len(price):

		# 過去〇〇足分の安値・高値データを準備する
		if i < ma:
			time.sleep(wait)
			i += 1
			continue
		
		data = price[i]		
		
		if flag["order"]["exist"]:
			flag = check_order( flag )

		if flag["position"]["exist"]:
			flag = close_position( data,flag )
		else:
			flag = entry_signal( data, flag, ma_buffer, hige_buffer )

		i += 1
		time.sleep(wait)


	print("--------------------------")
	print("テスト期間：")
	print("開始時点 : " + str(price[0]["close_time_dt"]))
	print("終了時点 : " + str(price[-1]["close_time_dt"]))
	print("時間軸       : " + str(int(chart_sec)) + "分足で検証")
	print("移動平均線       : " + str(ma) + "ma")
	print("移動平均線バッファ       : " + str(ma_buffer) + "ma_buffer")
	print("ひげのバッファ       : " + str(hige_buffer) + "hige_buffer")
	print(str(len(price)) + "件のローソク足データで検証")
	print("--------------------------")

	# 取引が少なかったらスキップ
	if len(flag["records"]["date"]) < 19:
		i += 1
		continue

	result = backtest( flag )

	# 今回のループで使ったパラメータの組み合わせを配列に記録する
	param_chart_sec.append( chart_sec )
	param_ma.append( ma )
	param_ma_buffer.append( ma_buffer )
	param_hige_buffer.append( hige_buffer )

	# 今回のループのバックテスト結果を配列に記録する
	result_count.append( result["トレード回数"] )
	result_winRate.append( result["勝率"] )
	result_returnRate.append( result["平均リターン"] )
	result_drawdown.append( result["最大ドローダウン"] )
	result_profitFactor.append( result["プロフィットファクタ―"] )
	result_gross.append( result["最終損益"] )

# 全てのパラメータによるバックテスト結果をPandasで１つの表にする
df = pd.DataFrame({
	"時間軸"        :  param_chart_sec,
	"移動平均線"        :  param_ma,
	"移動平均線バッファ"        :  param_ma_buffer,
	"ひげバッファ"        :  param_hige_buffer,
	"トレード回数"  :  result_count,
	"勝率"          :  result_winRate,
	"平均リターン"  :  result_returnRate,
	"ドローダウン"  :  result_drawdown,
	"PF"            :  result_profitFactor,
	"最終損益"      :  result_gross
})

# 列の順番を固定する
df = df[[ "時間軸","移動平均線","移動平均線バッファ","ひげバッファ","トレード回数","勝率","平均リターン","ドローダウン","PF","最終損益"  ]]

# 最終結果をcsvファイルに出力
df.to_csv("sma/log/result-{}.csv".format(datetime.now().strftime("%Y-%m-%d-%H-%M")) )
