# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
测试环境变量配置的脚本
演示如何使用不同的环境变量设置
"""

import os
from config import get_eodhd_api_token, get_max_concurrent_requests, print_config_info


def test_default_config():
    """测试默认配置"""
    print("1. 测试默认配置（无环境变量）")
    print("=" * 40)

    # 清除环境变量
    for key in ["EODHD_API_TOKEN", "MAX_CONCURRENT_REQUESTS", "TIMEOUT_SECONDS"]:
        if key in os.environ:
            del os.environ[key]

    # 重新导入配置以获取最新值
    from importlib import reload
    import config

    reload(config)

    config.print_config_info()


def test_custom_config():
    """测试自定义配置"""
    print("2. 测试自定义环境变量配置")
    print("=" * 40)

    # 设置自定义环境变量
    os.environ["EODHD_API_TOKEN"] = "custom_test_token_12345"
    os.environ["MAX_CONCURRENT_REQUESTS"] = "10"
    os.environ["TIMEOUT_SECONDS"] = "60"

    # 重新导入配置
    from importlib import reload
    import config

    reload(config)

    config.print_config_info()

    # 测试各个函数
    print("直接调用配置函数:")
    print(f"API Token: {config.get_eodhd_api_token()}")
    print(f"最大并发数: {config.get_max_concurrent_requests()}")
    print(f"超时时间: {config.get_timeout_seconds()}秒")


def test_partial_config():
    """测试部分环境变量配置"""
    print("\n3. 测试部分环境变量配置")
    print("=" * 40)

    # 只设置部分环境变量
    os.environ["MAX_CONCURRENT_REQUESTS"] = "15"
    if "EODHD_API_TOKEN" in os.environ:
        del os.environ["EODHD_API_TOKEN"]  # 移除 API token，使用默认值

    # 重新导入配置
    from importlib import reload
    import config

    reload(config)

    config.print_config_info()


def demo_usage():
    """演示实际使用场景"""
    print("\n4. 实际使用场景演示")
    print("=" * 40)

    # 模拟在脚本中的使用
    print("模拟在异步脚本中的使用:")
    print(f"准备发起 API 请求...")
    print(f"使用 Token: {'*' * 10}{get_eodhd_api_token()[-6:]}")
    print(f"最大并发数: {get_max_concurrent_requests()}")
    print(f"这相当于同时最多 {get_max_concurrent_requests()} 个 HTTP 请求")


if __name__ == "__main__":
    print("🧪 环境变量配置测试脚本")
    print("=" * 50)

    # 保存原始环境变量
    original_env = {
        key: os.environ.get(key)
        for key in ["EODHD_API_TOKEN", "MAX_CONCURRENT_REQUESTS", "TIMEOUT_SECONDS"]
    }

    try:
        test_default_config()
        test_custom_config()
        test_partial_config()
        demo_usage()

        print("\n✅ 所有测试完成！")
        print("\n💡 使用提示:")
        print("- 在生产环境中设置 EODHD_API_TOKEN 环境变量")
        print("- 根据网络和API限制调整 MAX_CONCURRENT_REQUESTS")
        print("- 根据需要调整 TIMEOUT_SECONDS")

    finally:
        # 恢复原始环境变量
        for key, value in original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]
