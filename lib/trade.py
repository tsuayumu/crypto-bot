from multi_record import MultiRecord

def execute_trading(latest_candle, order, position, judge, signal, record, lot, slippage):
  order.check_order(position)	
		
  if position.exist:
    judge.judge_close_signal()
    if signal.is_exists():
      position.close(
        signal=signal,
        record=record,
        latest_candle=latest_candle,
        lot=lot,
        slippage=slippage,
        test=True
      )
      if type(record) is MultiRecord:
        record.add(
          position=position,
          candle=latest_candle,
          lot=lot,
          slippage=slippage,
        )

  else:
    judge.judge_open_signal()

    if signal.is_exists():
      order.entry(
        signal=signal,
        order_type="market",
        record=record,
        lot=lot,
        test=True
      )