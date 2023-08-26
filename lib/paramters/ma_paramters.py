import itertools

class MaParamters:
  def __init__(self, chart_sec_list, ma_list, ma_buffer_list, hige_buffer_list):
    self.chart_sec_list = chart_sec_list
    self.ma_list = ma_list
    self.ma_buffer_list = ma_buffer_list
    self.hige_buffer_list = hige_buffer_list

    self.result_chart_sec_list = []
    self.result_ma_list = []
    self.result_ma_buffer_list = []
    self.result_hige_buffer_list = []

  def combinations(self):
    return list(
      itertools.product(
        self.chart_sec_list,
        self.ma_list,
        self.ma_buffer_list,
        self.hige_buffer_list
      )
    )

  def save_result(self, chart_sec, ma, ma_buffer, hige_buffer):
    self.result_chart_sec_list.append( chart_sec )
    self.result_ma_list.append( ma )
    self.result_ma_buffer_list.append( ma_buffer )
    self.result_hige_buffer_list.append( hige_buffer )

  def result(self):
    return {
      "時間軸": self.result_chart_sec_list,
      "移動平均線": self.result_ma_list,
      "移動平均線バッファ": self.result_ma_buffer_list,
      "ひげバッファ": self.result_hige_buffer_list
    }

  def headers(self):
    return [
      "時間軸",
      "移動平均線",
      "移動平均線バッファ",
      "ひげバッファ"
    ]


  
