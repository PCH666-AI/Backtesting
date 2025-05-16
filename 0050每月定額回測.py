# ------------------------------------------------------------
# 0050 / 0056 每月定額 NT$10,000 回測（簡化版）
# ------------------------------------------------------------
import streamlit as st
st.set_page_config(page_title='台股 ETF 定期定額回測', layout='wide')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
import matplotlib.font_manager as fm
from pathlib import Path

# ─── 中文字型（與 .py 同層） ─────────────────────────────
font_path = Path(__file__).parent / 'NotoSansTC-Regular.otf'
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Noto Sans TC'

pd.set_option('mode.chained_assignment', None)

# ─── Streamlit 側邊欄 ───────────────────────────────────
etf = st.sidebar.selectbox('選擇 ETF', ('0050', '0056'), index=0)

price_file    = f'{etf}歷史股價.csv'
dividend_file = f'{etf}歷史股利.csv'
MONTHLY_QUOTA = 10_000    # ← 固定投入金額

# ─── 回測函式（加快取）──────────────────────────────────
@st.cache_data(show_spinner='回測運算中…')
def backtest(price_path, div_path, quota=MONTHLY_QUOTA):
    stock    = pd.read_csv(price_path, encoding='utf-8-sig')
    dividend = pd.read_csv(div_path,  encoding='utf-8-sig')

    month_check = int(stock.loc[0, '年月日'].split('/')[1])
    stock['除息金額'] = 0

    cost, cum_div, shares = [0], [0], [0]
    mkt_value, date = [], []

    for i in range(len(stock)):
        close = stock.loc[i, '收盤價(元)']
        # 每月第一天買進
        month = int(stock.loc[i, '年月日'].split('/')[1])
        if month == month_check:
            buy = int(quota / close)
            shares.append(shares[-1] + buy)
            cost.append(cost[-1] + buy * close)
            month_check = 1 if month_check == 12 else month_check + 1
        else:
            shares.append(shares[-1])
            cost.append(cost[-1])

        # 除息
        if stock.loc[i, '年月日'] in dividend['除息日'].tolist():
            cash = float(dividend.loc[
                dividend['除息日'] == stock.loc[i, '年月日'], '息值(元)'])
            stock.loc[i, '除息金額'] = cash

        cum_div.append(cum_div[-1] + stock.loc[i, '除息金額'] * shares[-1])
        cost[-1] -= stock.loc[i, '除息金額'] * shares[-1]

        mkt_value.append(int(close * shares[-1]))
        y, m, _ = stock.loc[i, '年月日'].split('/')
        date.append(f'{y}/{m}')

    cost.pop(0); shares.pop(0); cum_div.pop(0)
    n = min(len(date), len(cost), len(cum_div), len(mkt_value))
    return date[:n], cost[:n], cum_div[:n], mkt_value[:n]

# ─── 畫圖 ───────────────────────────────────────────────
def plot(date, cost, div, value, etf):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(f'{etf} 每月定額 NT$10,000 回測', size=16)
    ax.set_xlabel('Date'); ax.set_ylabel('Value (NTD)')
    ax.xaxis.set_major_locator(MultipleLocator(12))
    for t in ax.get_xticklabels(): t.set_rotation(45)

    ax.plot(date, value, label='市值', color='indianred')
    ax.bar(date, cost, color='orange', label='成本')
    ax.bar(date, div, bottom=cost, color='red', label='累積股利')

    ax.legend(loc='upper left'); ax.grid(linewidth=0.5)
    plt.tight_layout()
    return fig

# ─── Streamlit 介面入口 ─────────────────────────────────
st.title('台股 ETF 定期定額回測工具（固定 NT$10,000）')

if st.button('開始回測'):
    d, c, dv, v = backtest(price_file, dividend_file)
    st.pyplot(plot(d, c, dv, v, etf))
