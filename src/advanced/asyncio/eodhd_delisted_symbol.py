# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "aiohttp",
#     "pandas",
# ]
# ///

import asyncio
import aiohttp
import pandas as pd
from typing import List, Dict, Any

from config import get_eodhd_api_token, get_max_concurrent_requests, print_config_info


async def fetch_us_symbols(api_token: str) -> List[Dict[str, Any]]:
    """
    异步获取所有美国股票代码

    Args:
        api_token: EODHD API 密钥

    Returns:
        股票代码列表
    """
    url = f"https://eodhd.com/api/exchange-symbol-list/US?delisted=1&api_token={api_token}&fmt=json"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"成功获取到 {len(data)} 个股票代码")
                    return data
                else:
                    print(f"请求失败，状态码: {response.status}")
                    return []
    except Exception as e:
        print(f"获取股票代码时出错: {e}")
        return []


async def fetch_symbol_details(api_token: str, symbol: str) -> Dict[str, Any]:
    """
    异步获取单个股票的详细信息

    Args:
        api_token: EODHD API 密钥
        symbol: 股票代码

    Returns:
        股票详细信息
    """
    url = (
        f"https://eodhd.com/api/fundamentals/{symbol}.US?api_token={api_token}&fmt=json"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"获取 {symbol} 详情失败，状态码: {response.status}")
                    return {}
    except Exception as e:
        print(f"获取 {symbol} 详情时出错: {e}")
        return {}


async def fetch_multiple_symbols_details(
    api_token: str, symbols: List[str], max_concurrent: int = 5
) -> List[Dict[str, Any]]:
    """
    异步批量获取多个股票的详细信息，使用信号量控制并发数

    Args:
        api_token: EODHD API 密钥
        symbols: 股票代码列表
        max_concurrent: 最大并发数

    Returns:
        股票详细信息列表
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore(symbol: str) -> Dict[str, Any]:
        async with semaphore:
            return await fetch_symbol_details(api_token, symbol)

    tasks = [fetch_with_semaphore(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 过滤掉异常结果
    valid_results = [r for r in results if isinstance(r, dict) and r]
    print(f"成功获取 {len(valid_results)} 个股票的详细信息")
    return valid_results


async def save_symbols_to_csv(
    df: pd.DataFrame,
    filename: str = "us_stock_symbols.csv",
    columns: List[str] = None,
    filter_condition: str = None,
) -> None:
    """
    将股票数据保存为CSV文件

    Args:
        df: 股票数据DataFrame
        filename: CSV文件名
        columns: 要保存的列名列表，None表示保存所有列
        filter_condition: 过滤条件，例如 "Type == 'Common Stock'"
    """
    # 复制数据框避免修改原始数据
    output_df = df.copy()

    # 应用过滤条件
    if filter_condition:
        try:
            output_df = output_df.query(filter_condition)
            print(f"应用过滤条件 '{filter_condition}' 后，剩余 {len(output_df)} 行数据")
        except Exception as e:
            print(f"过滤条件应用失败: {e}")
            return

    # 选择指定列
    if columns:
        available_columns = [col for col in columns if col in output_df.columns]
        missing_columns = [col for col in columns if col not in output_df.columns]
        if missing_columns:
            print(f"警告: 以下列不存在: {missing_columns}")
        if available_columns:
            output_df = output_df[available_columns]
            print(f"选择了 {len(available_columns)} 列: {available_columns}")

    # 保存为CSV
    output_df.to_csv(filename, index=False, encoding="utf-8")
    print(f"股票数据已保存到: {filename}")
    print(f"文件包含 {len(output_df)} 行数据，{len(output_df.columns)} 列")
    print(f"文件大小: {output_df.memory_usage(deep=True).sum() / 1024:.2f} KB")


async def analyze_data_quality(df: pd.DataFrame) -> None:
    """
    分析数据质量，检查空值和数据分布

    Args:
        df: 股票数据DataFrame
    """
    print("\n=== 数据质量分析 ===")
    print(f"总行数: {len(df)}")
    print(f"总列数: {len(df.columns)}")

    # 检查空值
    print("\n空值统计:")
    null_counts = df.isnull().sum()
    null_percentages = (df.isnull().sum() / len(df) * 100).round(2)

    for col in df.columns:
        null_count = null_counts[col]
        null_percentage = null_percentages[col]
        if null_count > 0:
            print(f"  {col}: {null_count} 个空值 ({null_percentage}%)")
        else:
            print(f"  {col}: 无空值 ✓")

    # 检查重复值
    duplicates = df.duplicated().sum()
    print(f"\n重复行数: {duplicates}")

    # 检查Code字段的唯一性
    if "Code" in df.columns:
        unique_codes = df["Code"].nunique()
        print(f"唯一股票代码数: {unique_codes}")
        duplicate_codes = len(df) - unique_codes
        if duplicate_codes > 0:
            print(f"重复的股票代码: {duplicate_codes} 个")

    # 显示每列的数据类型
    print(f"\n数据类型:")
    for col in df.columns:
        print(f"  {col}: {df[col].dtype}")

    # 显示一些统计信息
    if "Type" in df.columns:
        print(f"\n股票类型分布:")
        type_counts = df["Type"].value_counts().head(10)
        for stock_type, count in type_counts.items():
            percentage = (count / len(df) * 100).round(1)
            print(f"  {stock_type}: {count} ({percentage}%)")

    if "Exchange" in df.columns:
        print(f"\n交易所分布:")
        exchange_counts = df["Exchange"].value_counts().head(10)
        for exchange, count in exchange_counts.items():
            percentage = (count / len(df) * 100).round(1)
            print(f"  {exchange}: {count} ({percentage}%)")


async def main():
    """主函数"""
    # 显示配置信息
    print_config_info()

    # 从配置获取API密钥
    api_token = get_eodhd_api_token()

    # 1. 获取所有美国退市股票代码
    print("正在获取美国退市股票代码...")
    symbols_data = await fetch_us_symbols(api_token)

    if not symbols_data:
        print("无法获取股票代码数据")
        return

    # 转换为DataFrame
    df = pd.DataFrame(symbols_data)
    print(f"总计获取到 {len(df)} 个股票代码")
    print("前5个股票代码:")
    print(df.head())

    # 显示可用的列
    print(f"\n可用的列: {list(df.columns)}")

    # 保存完整数据
    await save_symbols_to_csv(df, "us_delisted_stock_symbols_full.csv")

    # # 保存常用列（如果存在）
    # common_columns = ["Code", "Name", "Type", "Exchange"]
    # available_common_columns = [col for col in common_columns if col in df.columns]
    # if available_common_columns:
    #     await save_symbols_to_csv(
    #         df, "us_stock_symbols_common.csv", columns=available_common_columns
    #     )

    # # 保存普通股票（如果Type列存在）
    # if "Type" in df.columns:
    #     await save_symbols_to_csv(
    #         df,
    #         "us_common_stocks.csv",
    #         columns=["Code", "Name", "Exchange"],
    #         filter_condition="Type == 'Common Stock'",
    #     )

    # 2. 获取前10个股票的详细信息（作为示例）
    # sample_symbols = df["Code"].head(10).tolist()
    # print(f"\n正在获取 {len(sample_symbols)} 个股票的详细信息...")

    # max_concurrent = get_max_concurrent_requests()
    # details = await fetch_multiple_symbols_details(
    #     api_token, sample_symbols, max_concurrent=max_concurrent
    # )

    # if details:
    #     print(f"\n成功获取 {len(details)} 个股票的详细信息")
    #     for detail in details[:3]:  # 只显示前3个
    #         symbol = detail.get("General", {}).get("Code", "Unknown")
    #         name = detail.get("General", {}).get("Name", "Unknown")
    #         print(f"股票: {symbol}, 名称: {name}")

    # 分析数据质量
    await analyze_data_quality(df)


if __name__ == "__main__":
    asyncio.run(main())
