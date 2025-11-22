import akshare as ak
import pandas as pd
import datetime
import requests

# ---------------------------------------------------------
#                微信推送函数（已加入你的 SendKey）
# ---------------------------------------------------------
def send_msg(message):
    key = "SCT303372TduosM0NoLHMhqmID6vAOwe5W"
    url = f"https://sctapi.ftqq.com/{key}.send"
    data = {
        "title": "A股选股监控通知",
        "desp": message
    }
    requests.post(url, data=data)


# ---------------------------------------------------------
#                核心选股逻辑
# ---------------------------------------------------------
def check_signals():
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # 获取全部 A 股列表
    stock_list = ak.stock_zh_a_spot()
    codes = stock_list["代码"].tolist()

    signals = []

    for code in codes:
        try:
            df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20240101")
            df.rename(columns={
                "收盘": "close",
                "开盘": "open",
                "最高": "high",
                "最低": "low",
            }, inplace=True)

            if len(df) < 3:
                continue

            # 涨停（≥ 9.9%）
            df["zt"] = (df["close"] / df["close"].shift(1)) >= 1.099

            # 跳空涨停（第二天开盘 > 前一天最高）
            df["jump_zt"] = df["zt"] & (df["open"] > df["high"].shift(1))

            # 连续两天涨停 + 第2天跳空涨停
            df["signal"] = df["zt"].shift(1) & df["jump_zt"]

            if df.iloc[-1]["signal"]:
                name = stock_list[stock_list["代码"] == code]["名称"].values[0]
                signals.append(f"{name}（{code}）")

        except Exception:
            continue

    return signals


# ---------------------------------------------------------
#                主程序
# ---------------------------------------------------------
def main():
    stocks = check_signals()
    if stocks:
        msg = "今日信号：\n" + "\n".join(stocks)
    else:
        msg = "今日无符合条件的股票"

    send_msg(msg)


if __name__ == "__main__":
    main()
