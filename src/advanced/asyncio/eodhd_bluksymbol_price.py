# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-dotenv",
#     "requests",
# ]
# ///


import os
import requests
from dotenv import load_dotenv
import json

# 加载 .env 文件中的环境变量 (API_TOKEN)
load_dotenv()

# 从环境变量中获取 API Token
API_TOKEN = os.getenv("EODHD_API_TOKEN")
BASE_URL = "https://eodhd.com/api"


def get_bulk_eod_prices(
    exchange: str, date: str, symbols: list[str]
) -> list[dict] | None:
    """
    使用 EODHD 的 Bulk API 获取多个股票在指定日期的日终价格。

    Args:
        exchange (str): 交易所代码, 例如 'US'。
        date (str): 查询日期，格式为 'YYYY-MM-DD'。
        symbols (list[str]): 包含股票代码的列表，例如 ['AAPL.US', 'MSFT.US']。

    Returns:
        list[dict] | None: 包含价格数据的字典列表，如果请求失败则返回 None。
    """
    if not API_TOKEN:
        print("错误: 未找到 EODHD_API_TOKEN。请检查您的 .env 文件。")
        return None

    # 将股票代码列表转换为逗号分隔的字符串
    symbols_str = ",".join(symbols)

    # 构建 API 请求的 URL 和参数
    endpoint = f"/eod-bulk-last-day/{exchange}"
    url = f"{BASE_URL}{endpoint}"

    params = {
        "api_token": API_TOKEN,
        "date": date,
        "symbols": symbols_str,
        "fmt": "json",
    }

    print(f"正在请求数据，URL: {url}")
    print(f"参数: date={date}, symbols={symbols_str}")

    try:
        response = requests.get(url, params=params)
        # 检查响应状态码，如果不是 200 OK，则抛出异常
        response.raise_for_status()

        # 将响应的 JSON 文本解析为 Python 对象
        data = response.json()
        return data

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误: {http_err}")
        print(f"响应内容: {response.text}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求错误: {req_err}")
    except json.JSONDecodeError:
        print("错误: 无法解析返回的 JSON 数据。可能是 API 响应格式不正确。")
        print(f"原始响应内容: {response.text}")

    return None


if __name__ == "__main__":
    # --- 在这里修改为您想查询的参数 ---
    TARGET_DATE = "2025-01-27"  # 您想查询的日期
    EXCHANGE_CODE = "US"  # 目标交易所 (US 包括 NYSE, NASDAQ 等)
    SYMBOLS_TO_GET = [  # 您想查询的股票代码列表
        "AAPL.US",
        "MSFT.US",
        "GOOGL.US",
        "TSLA.US",
    ]
    # ------------------------------------

    price_data = get_bulk_eod_prices(EXCHANGE_CODE, TARGET_DATE, SYMBOLS_TO_GET)

    if price_data:
        print("\n--- 数据获取成功 ---")
        # 遍历返回的列表并打印关键信息
        for stock_info in price_data:
            print(
                f"代码: {stock_info.get('code'):<10} "
                f"日期: {stock_info.get('date')} | "
                f"收盘价: {stock_info.get('close'):<8} "
                f"成交量: {stock_info.get('volume')}"
            )

        # 打印第一个返回的完整 JSON 对象，以便您查看所有可用字段
        if len(price_data) > 0:
            print("\n--- 第一个对象的完整数据示例 ---")
            print(json.dumps(price_data[0], indent=2))
    else:
        print("\n--- 数据获取失败 ---")
