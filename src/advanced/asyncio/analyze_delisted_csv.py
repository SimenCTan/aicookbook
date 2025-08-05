# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pandas",
# ]
# ///

import pandas as pd
from typing import Optional


def analyze_csv_data_quality(csv_file: str) -> None:
    """
    分析CSV文件的数据质量，检查空值和数据分布

    Args:
        csv_file: CSV文件路径
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_file)
        print(f"成功读取文件: {csv_file}")

    except FileNotFoundError:
        print(f"文件不存在: {csv_file}")
        return
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return

    print(f"\n=== {csv_file} 数据质量分析 ===")
    print(f"总行数: {len(df):,}")
    print(f"总列数: {len(df.columns)}")
    print(f"列名: {list(df.columns)}")

    # 检查空值
    print(f"\n{'='*50}")
    print("空值详细分析:")
    print(f"{'='*50}")

    null_summary = []
    for col in df.columns:
        null_count = df[col].isnull().sum()
        null_percentage = (null_count / len(df) * 100).round(2)

        # 检查空字符串
        if df[col].dtype == "object":
            empty_string_count = (df[col] == "").sum()
            whitespace_count = (
                df[col].str.strip().eq("").sum() if df[col].dtype == "object" else 0
            )
        else:
            empty_string_count = 0
            whitespace_count = 0

        total_missing = null_count + empty_string_count
        total_missing_percentage = (total_missing / len(df) * 100).round(2)

        null_summary.append(
            {
                "column": col,
                "null_count": null_count,
                "null_percentage": null_percentage,
                "empty_string_count": empty_string_count,
                "total_missing": total_missing,
                "total_missing_percentage": total_missing_percentage,
            }
        )

        status = "❌" if total_missing > 0 else "✅"
        print(f"{status} {col}:")
        print(f"    NULL值: {null_count:,} ({null_percentage}%)")
        if empty_string_count > 0:
            print(f"    空字符串: {empty_string_count:,}")
        print(f"    总缺失: {total_missing:,} ({total_missing_percentage}%)")
        print()

    # 按缺失率排序
    null_summary.sort(key=lambda x: x["total_missing_percentage"], reverse=True)
    print(f"\n{'='*50}")
    print("缺失率排序 (从高到低):")
    print(f"{'='*50}")
    for item in null_summary:
        if item["total_missing"] > 0:
            print(
                f"{item['column']}: {item['total_missing_percentage']}% "
                f"({item['total_missing']:,}/{len(df):,})"
            )

    # 检查重复值
    duplicates = df.duplicated().sum()
    print(f"\n重复行数: {duplicates:,}")

    # 检查Code字段的唯一性
    if "Code" in df.columns:
        unique_codes = df["Code"].nunique()
        print(f"唯一股票代码数: {unique_codes:,}")
        duplicate_codes = len(df) - unique_codes
        if duplicate_codes > 0:
            print(f"重复的股票代码: {duplicate_codes:,} 个")
            # 显示重复的代码
            duplicated_codes = df[df["Code"].duplicated(keep=False)]["Code"].unique()
            print(f"重复代码示例: {list(duplicated_codes[:5])}")

    # 显示每列的数据类型和基本统计
    print(f"\n{'='*50}")
    print("数据类型和基本统计:")
    print(f"{'='*50}")
    for col in df.columns:
        dtype = df[col].dtype
        unique_count = df[col].nunique()
        print(f"{col}: {dtype}, {unique_count:,} 个唯一值")

        if dtype == "object" and unique_count < 20:
            # 显示分类字段的值分布
            value_counts = df[col].value_counts().head(10)
            print(f"  前10个值分布:")
            for value, count in value_counts.items():
                percentage = round((count / len(df) * 100), 1)
                display_value = (
                    str(value)[:30] + "..." if len(str(value)) > 30 else str(value)
                )
                print(f"    '{display_value}': {count:,} ({percentage}%)")
        print()

    # 数据样本展示
    print(f"\n{'='*50}")
    print("数据样本 (前5行):")
    print(f"{'='*50}")
    print(df.head().to_string(index=False))

    if len(df) > 5:
        print(f"\n数据样本 (后5行):")
        print(df.tail().to_string(index=False))


def main():
    """主函数"""
    # 分析退市股票文件
    delisted_file = "src/advanced/asyncio/us_delisted_stock_symbols_full.csv"
    analyze_csv_data_quality(delisted_file)

    # 如果存在正常股票文件，也进行比较分析
    normal_file = "src/advanced/asyncio/us_stock_symbols_full.csv"
    try:
        df_normal = pd.read_csv(normal_file)
        df_delisted = pd.read_csv(delisted_file)

        print(f"\n{'='*60}")
        print("对比分析: 正常股票 vs 退市股票")
        print(f"{'='*60}")
        print(f"正常股票数量: {len(df_normal):,}")
        print(f"退市股票数量: {len(df_delisted):,}")

        # 比较各字段的空值率
        print(f"\n空值率对比:")
        print(f"{'字段':<15} {'正常股票':<15} {'退市股票':<15} {'差异':<15}")
        print("-" * 60)

        for col in df_normal.columns:
            if col in df_delisted.columns:
                normal_null_rate = (
                    df_normal[col].isnull().sum() / len(df_normal) * 100
                ).round(2)
                delisted_null_rate = (
                    df_delisted[col].isnull().sum() / len(df_delisted) * 100
                ).round(2)
                diff = delisted_null_rate - normal_null_rate

                print(
                    f"{col:<15} {normal_null_rate:<15}% {delisted_null_rate:<15}% {diff:<15.2f}%"
                )

    except FileNotFoundError:
        print(f"\n注意: 找不到正常股票文件 {normal_file}，跳过对比分析")


if __name__ == "__main__":
    main()
