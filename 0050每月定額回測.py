# 1. 匯入外部程式庫（Libraries）
import numpy as np
# 這行程式碼的作用是匯入一個叫做 NumPy 的數學運算程式庫，並把它的名字縮寫成 np。
# 例如，若你要使用 NumPy 提供的函數，就可以寫 np.函數名稱。 NumPy 常用來處理數字和陣列（像是一堆數字的容器）。
import pandas as pd
# 匯入 Pandas 程式庫，縮寫成 pd。
# Pandas 主要用於處理表格型的資料（稱為 DataFrame），像是 Excel 表格的資料都可以用它處理。
import datetime
# 匯入 Python 的 datetime 模組，這個模組幫助你處理日期和時間的資料。
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
# 第一行與第二行是匯入 Matplotlib 這個繪圖程式庫，mpl 代表整個 Matplotlib，plt 是常用來畫圖的子模組。
# 第三行則從 Matplotlib 裡面拿出一個叫做 MultipleLocator 的工具，這個工具用來設定圖表中的刻度間隔。

# 2. 設定 Pandas 的警告模式
pd.set_option('mode.chained_assignment', None) 
#這行程式設定 Pandas 的選項，將「連鎖賦值警告」（chained assignment warning）關掉。
# 3. 讀取資料檔案
stock = pd.read_csv(r'C:\Users\Public\stock\0050股市資料\0050歷史股價2008.csv', encoding='utf-8', low_memory=False, index_col=False)
dividend = pd.read_csv(r'C:\Users\Public\stock\0050股市資料\0050歷史股利2008.csv', encoding='utf-8', low_memory=False, index_col=False)
# 這行利用 Pandas 讀取一個 CSV 檔案，檔案路徑是 C:\Users\Public\stock\0050股市資料\0050歷史股價.csv。
# encoding='utf-8'：表示檔案使用 UTF-8 的編碼（確保中文能正確讀取）。
# low_memory=False：告訴 Pandas 不用分批讀取資料，可以一次讀完。
# index_col=False：表示不把某一欄設定成索引，而是保留所有欄位。

# 4. 初始化變數與設定初始值
max_price = stock.loc[0, '收盤價(元)']
# 從資料的第 0 筆（第一筆資料）中，讀取欄位名稱為「收盤價(元)」的值，並把它存入變數 max_price，用來記錄過去見到的最高股價。
dd = 0
# 建立變數 dd，初始值設定為 0。這個變數之後用來計算股價下跌的比例（也稱為「跌幅比率」）
cost = [0]
# 記錄投資成本。
# cost：正常定期定額的成本。
# 每個清單先放一個 0 作為起始值，方便之後累加使用。
cum_dividend = [0]
# 這四個清單記錄累積收到的股利金額（股利是公司分配給股東的現金）。
# 分別針對不同策略：正常、減碼、加碼、股利再投資。
shares = [0]
# 這四個清單記錄累計購買的股數（手上有多少股票）。
# 同樣依策略分成四種，初始都放 0。
market_value = []
# 這幾個空清單用來記錄市值，也就是當天股票的總價值（股價乘以持有股數）。
stock_price = []
# 此清單用來儲存歷史中每一筆資料的「收盤價」，即每天的交易結束時價格。
date = []
# 這個清單用來存放日期，之後會用於 x 軸繪圖。
count=0
# 建立一個計數變數 count，用來計算處理了多少筆資料。

# 5. 處理日期字串，確定起始月份
date_str = stock.loc[0, '年月日']
# 從第一筆股市資料中，取出日期欄位「年月日」，存入變數 date_str。
print("Date string:", date_str)
# 將讀取到的日期字串印出來，方便檢查資料內容。
month_check = int(date_str.split('/')[1])
month_check = int(stock.loc[0, '年月日'].split('/')[1])
# 這兩行程式碼利用 split('/') 將日期字串依照 / 分割成「年」、「月」、「日」。
# split('/')[1] 取出分割後的第二部分，也就是「月」。
# 使用 int() 轉換為整數型態，並將此值存入變數 month_check，用來記錄目前應該買進股票的月份。

# 6. 新增欄位：除息金額
stock['除息金額'] = 0
# 在股市資料的 DataFrame 中，新增一個欄位名稱為「除息金額」，並預設所有資料的值都為 0。
# 這個欄位用來記錄在除息（公司派股利日）時，每股所得到的股利金額。

# 7. 進入迴圈：逐筆處理每一天的資料
# 整個 for 迴圈會針對股市中每一筆資料進行計算與記錄。
for i in range(0, len(stock)):#這行表示從 i=0 到 i=（資料筆數-1），逐筆讀取每一天的資料。

# 7.1 取得股票當天價格與更新最高價及跌幅比例
    if stock.loc[i, '收盤價(元)'] >= max_price:     # 判斷DD
        max_price = stock.loc[i, '收盤價(元)']
        dd = 0
    else:
        dd = stock.loc[i, '收盤價(元)'] / max_price
# 讀取第 i 行資料中，「收盤價(元)」（當天收盤價）。
# 如果當天的股價大於或等於目前記錄的 max_price（最高價），就更新 max_price 為當天價格，並將 dd 設定為 0，代表沒有下跌。
# 否則（股價低於最高價），計算 dd 為當天價格除以最高價，這個比例表示從最高價跌了多少。

# 7.3 儲存當天的股價
    stock_price.append(stock.loc[i, '收盤價(元)'])
# 將當天的收盤價加入 stock_price 清單，日後可以用來繪圖或做分析。
    # t_date = stock.loc[i, '年月日'].split('/')

# 7.4 擷取並處理日期中的「月」
    month = int(stock.loc[i, '年月日'].split('/')[1])
# 與先前相同，從當天的日期字串中分割出月份，轉為整數後存入變數 month。

# 7.5 判斷是否是每月買入日（定期定額）
    if month == month_check:      # 每月第一天定額買入
# 如果當天的月份等於 month_check（代表是預定的買入月份），進入以下區塊執行定期定額買入策略：
        shares.append(int(10000 / stock.loc[i, '收盤價(元)']) + shares[-1])
# 計算用 10000 元能買到多少股：用 10000 除以當天的收盤價，用 int() 取整數（因為不能買零碎的股數）。
# 再加上上一次累積的股數（shares[-1] 表示清單中的最後一個數），更新 shares 清單。

        count+=1
# 每完成一次定期買入，計數器 count 加 1。
        cost.append(int(stock.loc[i, '收盤價(元)'] * int(10000 / stock.loc[i, '收盤價(元)'])) + cost[-1])
# 計算當天購買股票所花的金額：以購買股數乘上當天股價，並累加上前面的成本。
# 這裡用 int(10000 / 股價) 來確定買進多少股，再乘上股價得當天花費金額。

        month_check += 1
        if month_check == 13:
            month_check = 1
# 完成一筆定期買入後，將 month_check 加 1，準備下個月再買。
# 若 month_check 達到 13（表示月份超出 12 個月），則重設為 1，回到一月。
    else:
        cost.append(cost[-1])
        shares.append(shares[-1])
        count+=1
# 如果當天的月份不符合 month_check（表示非預定買入日），那麼所有與買進相關的變數（成本與股數）就不變，直接將前一天的數值再加到清單中保持長度一致。
# 此外，也增加計數器 count，表示依然處理了這一天的資料。

# 7.6 處理除息（派發股利）的部分
    if stock.loc[i, '年月日'] in dividend['除息日'].tolist():    # 除息資料
# 檢查當天的日期是否出現在股利資料的「除息日」列表中，也就是判斷今天公司有沒有發放股利。
        money = dividend.loc[dividend['除息日'] == stock.loc[i, '年月日'], '息值(元)']
# 如果是除息日，就從股利資料中取出當天的股利金額（欄位「息值(元)」），存入 money。
        stock.loc[i, '除息金額'] = float(money)
# 將股利金額轉換成浮點數（小數），存回到股市資料的「除息金額」欄位。

# 7.7 更新其他策略的累積股利與市值
    cum_dividend.append(stock.loc[i, '除息金額'] * shares[-1] + cum_dividend[-1])
# 分別針對正常定期定額、減碼與加碼策略，計算當天根據該策略持有的股數所得的股利，再加上之前累計的股利。
    cost[-1] -= stock.loc[i, '除息金額'] * shares[-1]  # 扣除相應的股利金額

    
    market_value.append(int(stock.loc[i, '收盤價(元)'] * shares[-1]))
# 根據當天的收盤價與各策略持有的股票數量，計算市值（價值）並存入對應的清單。
# int(...) 取整數，這裡市值可能是一個整數數字。
    date.append(stock.loc[i, '年月日'].split('/')[0] + '/' + stock.loc[i, '年月日'].split('/')[1])
# 將當天的日期字串用 / 分割後，只取「年」和「月」再組合成新字串（例如 "2023/07"），存入 date 清單。
# 這樣可以在圖表上顯示簡化的日期軸，不需要每天細分。
    # date.append(datetime.datetime.strptime(stock.loc[i, '年月日'], '%Y-%m-%d').date())
    # 原本是將日期字串轉換成日期型態，不過這裡已改成只取年/月。
# 8. 迴圈結束後的後處理
print("count=",count)
# 印出整個資料中一共處理了多少天（count的值）。
# 接下來移除各清單第一個元素 0（這些 0 僅作為初始值，現在需要移除以免影響累計結果）：
cost.remove(0)
shares.remove(0)
cum_dividend.remove(0)
print(cost)
# 印出現在的成本清單，讓使用者可以檢查累積的成本數據。
# 市值成本折線圖
# fig, ax1 = plt.subplots()


# 9. 繪製圖表（視覺化結果）
# 9.1 建立繪圖區與設定字型
fig, (ax1) = plt.subplots(nrows=1, figsize=(6, 5))
# 使用 plt.subplots 建立一個圖表區域（畫布）包含兩個子圖（左右並排），圖表大小設為 12 x 5 吋。
# fig 為整個圖表，ax1 與 ax2 分別代表第一個和第二個子圖。
fig.suptitle('0050每月定額$10000 (2003/06/30 ~ 2025/04/10)', fontsize=16)
# 設定整張圖的標題（suptitle），標題中描述了投資對象、定期定額金額以及日期範圍，字型大小設為 16。
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
# 設定 Matplotlib 使用的中文字型為「微軟正黑體」以正確顯示中文。

# 9.2 繪製第一個子圖：累積交易績效
ax1.set_title('累積交易績效', size=14)
ax1.set_xlabel('Date')
# 設定第一個子圖的標題為「累積交易績效」，並標示 x 軸為「Date」（日期）。
for tick in ax1.get_xticklabels():
    tick.set_rotation(45)
# 將 x 軸的所有刻度標籤（日期文字）旋轉 45 度，這樣避免文字重疊，看起來比較清楚。
ax1.xaxis.set_major_locator(MultipleLocator(12))
# 使用 MultipleLocator 設定 x 軸的主刻度間隔為 12 個單位（這裡可能代表每 12 個點標示一次）。
ax1.set_ylabel('Value')
# 設定 y 軸標籤為「Value」（價值）。
# 接著分別繪製各種策略的市值線圖：
ax1.plot(date, market_value, label='市值(正常定期定額)', color='indianred')
# 每一行使用 plot() 函數：
# 第一個參數 date 為 x 軸資料（年月），
# 第二個參數為 y 軸資料（市值），
# label 是圖例說明（方便辨識哪條線代表哪個策略），
# color 則設定線條顏色。

# 再用長條圖呈現成本與累積股利：
ax1.bar(date, cost, color='orange', label='成本(正常定期定額)')
ax1.bar(date, cum_dividend, bottom=cost, color='red', label='累積股利(正常定期定額)')
# 第一行用 bar() 畫出成本的長條圖，顏色為橙色。
# 第二行再畫出累積股利的長條圖，並用 bottom=cost 指定長條圖從成本數值的上方開始堆疊，形成堆疊圖。
ax1.legend(loc='upper left')
# 顯示圖例，並設定位於左上角。
ax1.grid(linewidth=0.5)
# 在圖上加入網格線，讓看圖時更容易看清各數值。
plt.tight_layout()
# 自動調整圖中各物件的位置，避免標籤或圖例重疊。

plt.show()