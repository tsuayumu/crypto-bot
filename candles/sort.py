import json
import ndjson

def sort_ndjson(input_file, output_file, sort_key):
  with open(input_file, 'r') as f:
    data = ndjson.reader(f)
    sorted_data = sorted(data, key=lambda x: x[sort_key])

  with open(output_file, 'w') as f:
    ndjson.writer(f).writerow(sorted_data)

input_file = "candles.ndjson"
output_file = "sorted_candles.ndjson"
sort_key = "close_time_dt"  # ここにソートしたいキーを入力してください

sort_ndjson(input_file, output_file, sort_key)