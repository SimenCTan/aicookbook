"""
配置管理模块
支持从环境变量和配置文件读取配置
"""

import os
from typing import Optional


def get_eodhd_api_token() -> str:
    """
    获取 EODHD API Token
    优先级：环境变量 > 默认值

    Returns:
        API Token 字符串
    """
    # 首先尝试从环境变量获取
    token = os.getenv("EODHD_API_TOKEN")

    if token:
        return token
    raise ValueError("未找到环境变量 EODHD_API_TOKEN")


def get_max_concurrent_requests() -> int:
    """
    获取最大并发请求数

    Returns:
        最大并发请求数
    """
    try:
        return int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    except ValueError:
        return 5


def get_timeout_seconds() -> int:
    """
    获取请求超时时间（秒）

    Returns:
        超时时间
    """
    try:
        return int(os.getenv("TIMEOUT_SECONDS", "30"))
    except ValueError:
        return 30


# 配置字典
CONFIG = {
    "api_token": get_eodhd_api_token(),
    "max_concurrent": get_max_concurrent_requests(),
    "timeout": get_timeout_seconds(),
}


def print_config_info():
    """打印当前配置信息（隐藏敏感信息）"""
    print("\n=== 当前配置 ===")
    print(
        f"API Token: {'*' * 10}{CONFIG['api_token'][-6:] if len(CONFIG['api_token']) > 6 else '****'}"
    )
    print(f"最大并发数: {CONFIG['max_concurrent']}")
    print(f"超时时间: {CONFIG['timeout']}秒")
    print("================\n")


if __name__ == "__main__":
    print_config_info()
