# 売買判定する関数
def judge_open_signal( data,ma_buffer,hige_buffer ):

	# 移動平均線よりも下に位置してる
	if data["open_price"] < data["ma"]:
		# 移動平均線を上抜ける
		if data["close_price"] > data["ma"] + ma_buffer:
			# 上ひげが長い時は入らない
			if data["high_price"] - data["close_price"] < hige_buffer:
				return {
					"side" : "BUY",
					"price" : data["close_price"]
				}

	# 移動平均線よりも上に位置してる
	if data["open_price"] > data["ma"]:
		# 移動平均線を下抜ける
		if data["close_price"] < data["ma"] - ma_buffer:
			# 下ひげが長い時は入らない
			if data["close_price"] - data["low_price"] < hige_buffer:
				return {
					"side" : "SELL",
					"price" : data["close_price"]
				}
	
	return {"side" : None , "price":0}