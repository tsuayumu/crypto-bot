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
