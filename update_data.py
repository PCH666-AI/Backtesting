# update_data.py  ── 增量更新：只補最新股價 / 股利
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

TICKERS = {
    '0056': '0056.TW',
}

def append_latest(code, yf_code):
    price_csv    = f'{code}歷史股價.csv'
    dividend_csv = f'{code}歷史股利.csv'

    # ---------- 讀現有股價，找最後日期 ----------
    old_price = pd.read_csv(price_csv, encoding='utf-8-sig')
    last_day  = pd.to_datetime(old_price['年月日']).max()         # ex: 2024-05-10
    start     = (last_day + timedelta(days=1)).strftime('%Y-%m-%d')
    today     = datetime.today().strftime('%Y-%m-%d')

    # ---------- 抓新股價 ----------
    tkr = yf.Ticker(yf_code)
    new_px = tkr.history(start=start, end=today)[['Close']]
    new_px = (
        new_px.rename(columns={'Close': '收盤價(元)'})
              .reset_index()
              .assign(年月日=lambda df: df['Date'].dt.strftime('%Y/%m/%d'))
              [['年月日', '收盤價(元)']]
    )

    # ---------- 合併 & 去重 ----------
    price_all = pd.concat([old_price, new_px]).drop_duplicates('年月日')
    price_all.to_csv(price_csv, index=False, encoding='utf-8-sig')

    # ---------- 股利 ----------
    old_div = pd.read_csv(dividend_csv, encoding='utf-8-sig')
    last_ex = pd.to_datetime(old_div['除息日']).max()
    start_d = (last_ex + timedelta(days=1)).strftime('%Y-%m-%d')

    new_div = tkr.dividends[tkr.dividends.index >= start_d].reset_index()
    new_div = (
        new_div.rename(columns={'Date': '除息日', 'Dividends': '息值(元)'})
               .assign(除息日=lambda df: df['除息日'].dt.strftime('%Y/%m/%d'))
    )

    div_all = pd.concat([old_div, new_div]).drop_duplicates('除息日')
    div_all.to_csv(dividend_csv, index=False, encoding='utf-8-sig')

def main():
    for code, yf_code in TICKERS.items():
        append_latest(code, yf_code)

if __name__ == '__main__':
    main()
