import sys
sys.path.insert(0, "../../lib")

from candles import Candles
from candles_file import CandlesFile
from position import Position
from order import Order
from record import Record
from signal import Signal
from judge.ma import MaJudge
from trade import execute_trading

from datetime import datetime
import time

SYMBOL = 'BTC/USDT'
CANDLES_FILE_PATH = '../../candles/candles.ndjson'

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
judge = MaJudge()

while True:
	candles = Candles(CANDLES_FILE_PATH, CHART_SEC)
	candles.add_ma()

	latest_candle = candles.latest_candle()
	signal = Signal()

	record.set_log(
		"時間： " + datetime.fromtimestamp(latest_candle["close_time"] / 1000).strftime('%Y/%m/%d %H:%M') + " 始値： " + str(latest_candle["open_price"]) + " 終値： " + str(latest_candle["close_price"]) + " 移動平均線： " + str(latest_candle["{}ma".format(MA)]) + "\n"
	)

	judge.set_params(
		signal=signal,
		candle=latest_candle,
		ma=MA,
		ma_buffer=MA_BUFFER,
		hige_buffer=HIGE_BUFFER,
		position=position
	)

	execute_trading(
		latest_candle=latest_candle,
		order=order,
		position=position,
		judge=judge,
		signal=signal,
		record=record,
		lot=LOT,
		slippage=SLIPPAGE
	)

	time.sleep(60)
