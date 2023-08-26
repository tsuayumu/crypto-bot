import sys
sys.path.insert(0, "/Users/tsuda_ayumu/Develop/crypto_bot/lib")

from candles import Candles
from position import Position
from order import Order
from record import Record
from signal import Signal
from judge.ma import MaJudge
from trade import execute_trading

from datetime import datetime

SYMBOL = 'BTC/USDT'
CANDLES_FILE_PATH = '../candle_data/btc_usdt.ndjson'

# -----設定項目-----
CHART_SEC = 60    # n分足を使用
MA = 5        # 過去CHART_SEC*ｎ足の移動平均線
MA_BUFFER = 200 # 移動平均線のバッファ
HIGE_BUFFER = 50 # ひげが長い場合に売買しないためのバッファ
LOT = 1             # BTCの注文枚数
SLIPPAGE = 0.001    # 手数料・スリッページ
# -----------------

order = Order(SYMBOL)
position = Position(SYMBOL)
record = Record()
candles = Candles(CANDLES_FILE_PATH, CHART_SEC)
candles.add_ma()
judge = MaJudge()

i = 0
while i < len(candles.list):
	signal = Signal()

	# 過去〇〇足分の安値・高値データを準備する
	if i < MA:
		i += 1
		continue

	latest_candle = candles.list[i]

	record.set_log(
		"時間： " + datetime.fromtimestamp(latest_candle["close_time"] / 1000).strftime('%Y/%m/%d %H:%M') + " 始値： " + str(latest_candle["open_price"]) + " 終値： " + str(latest_candle["close_price"]) + " 移動平均線： " + str(latest_candle["{}ma".format(MA)]) + "\n"
	)

	judge.set_params(
		signal=signal,
		candle=candles.list[i],
		ma=MA,
		ma_buffer=MA_BUFFER,
		hige_buffer=HIGE_BUFFER,
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

print("--------------------------")
print("テスト期間：")
print("開始時点 : " + str(candles.list[0]["close_time_dt"]))
print("終了時点 : " + str(candles.list[-1]["close_time_dt"]))
print(str(len(candles.list)) + "件のローソク足データで検証")
print("--------------------------")


record.backtest()
	
