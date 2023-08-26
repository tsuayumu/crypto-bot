import sys
sys.path.insert(0, "/Users/tsuda_ayumu/Develop/crypto_bot/lib")

from candles import Candles
from position import Position
from order import Order
from multi_record import MultiRecord
from signal import Signal
from judge.ma import MaJudge
from paramters.ma_paramters import MaParamters
from trade import execute_trading

from datetime import datetime
import time
import pandas as pd
import itertools

SYMBOL = 'BTC/USDT'
CANDLES_FILE_PATH = '../candle_data/btc_usdt.ndjson'

#-----設定項目

wait = 0            # ループの待機時間
LOT = 1             # BTCの注文枚数
SLIPPAGE = 0.001    # 手数料・スリッページ

# バックテストのパラメーター設定
#---------------------------------------------------------------------------------------------
chart_sec_list  = [ 5, 15, 60, 120, 240 ] 
ma_list = [5,10,20,50]
ma_buffer_list = [0, 50, 100] # 移動平均線のバッファ
hige_buffer_list = [10,25,100,300,100000] # ひげが長い場合に売買しないためのバッファ
#---------------------------------------------------------------------------------------------


# 総当たりのためのfor文の準備
ma_paramters = MaParamters(
	chart_sec_list=chart_sec_list,
	ma_list=ma_list,
	ma_buffer_list=ma_buffer_list,
	hige_buffer_list=hige_buffer_list
)
record = MultiRecord()
judge = MaJudge()

for chart_sec, ma, ma_buffer, hige_buffer in ma_paramters.combinations():

	order = Order(SYMBOL)
	position = Position(SYMBOL)
	candles = Candles(CANDLES_FILE_PATH, chart_sec)
	candles.add_ma()

	# dataは今の価格
	i = 0
	while i < len(candles.list):
		signal = Signal()

		# 過去〇〇足分の安値・高値データを準備する
		if i < ma:
			i += 1
			continue

		judge.set_params(
			signal=signal,
			candle=candles.list[i],
			ma=ma,
			ma_buffer=ma_buffer,
			hige_buffer=hige_buffer,
			position=position
		)

		execute_trading(
			latest_candle=candles.list[i],
			order=order,
			position=position,
			judge=judge,
			signal=signal,
			record=record,
			lot=LOT,
			slippage=SLIPPAGE
		)

		i += 1
		time.sleep(wait)


	print("--------------------------")
	print("テスト期間：")
	print("開始時点 : " + str(candles.list[0]["close_time_dt"]))
	print("終了時点 : " + str(candles.list[-1]["close_time_dt"]))
	print("時間軸       : " + str(int(chart_sec)) + "分足で検証")
	print("移動平均線       : " + str(ma) + "ma")
	print("移動平均線バッファ       : " + str(ma_buffer) + "ma_buffer")
	print("ひげのバッファ       : " + str(hige_buffer) + "hige_buffer")
	print(str(len(candles.list)) + "件のローソク足データで検証")
	print("--------------------------")

	# 取引が少なかったらスキップ
	if len(record.date) < 19:
		i += 1
		continue

	ma_paramters.save_result(
		chart_sec=chart_sec,
		ma=ma,
		ma_buffer=ma_buffer,
		hige_buffer=hige_buffer
	)

	record.backtest()
	record.reset()

result_dataframe = ma_paramters.result()
result_dataframe.update(record.result())

# 全てのパラメータによるバックテスト結果をPandasで１つの表にする
df = pd.DataFrame(result_dataframe)

# 列の順番を固定する
df = df[ma_paramters.headers() + record.headers()]

# 最終結果をcsvファイルに出力
df.to_csv("../../log/result-{}.csv".format(datetime.now().strftime("%Y-%m-%d-%H-%M")) )
