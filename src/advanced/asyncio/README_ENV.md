# 环境变量配置说明

本项目支持通过环境变量来配置 EODHD API 参数，提高安全性和灵活性。

## 支持的环境变量

| 变量名 | 描述 | 默认值 | 必需 |
|--------|------|--------|------|
| `EODHD_API_TOKEN` | EODHD API 访问令牌 | 内置默认值 | 推荐 |
| `MAX_CONCURRENT_REQUESTS` | 最大并发请求数 | 5 | 否 |
| `TIMEOUT_SECONDS` | 请求超时时间（秒） | 30 | 否 |

## 设置环境变量的方法

### 方法1：在终端中临时设置

```bash
# macOS/Linux
export EODHD_API_TOKEN="your_api_token_here"
export MAX_CONCURRENT_REQUESTS="10"

# Windows Command Prompt
set EODHD_API_TOKEN=your_api_token_here
set MAX_CONCURRENT_REQUESTS=10

# Windows PowerShell
$env:EODHD_API_TOKEN="your_api_token_here"
$env:MAX_CONCURRENT_REQUESTS="10"
```

### 方法2：创建 .env 文件（推荐）

在项目根目录或脚本目录创建 `.env` 文件：

```bash
# .env 文件内容
EODHD_API_TOKEN=your_api_token_here
MAX_CONCURRENT_REQUESTS=10
TIMEOUT_SECONDS=60
```

**注意**：`.env` 文件应该添加到 `.gitignore` 中，避免敏感信息泄露。

### 方法3：在 shell 配置文件中设置

将环境变量添加到你的 shell 配置文件中：

```bash
# ~/.bashrc 或 ~/.zshrc
export EODHD_API_TOKEN="your_api_token_here"
export MAX_CONCURRENT_REQUESTS="10"
```

## 运行脚本

设置环境变量后，正常运行脚本：

```bash
# 获取正常股票数据
uv run src/advanced/asyncio/eodhd_symbol.py

# 获取退市股票数据
uv run src/advanced/asyncio/eodhd_delisted_symbol.py
```

## 验证配置

可以运行配置模块来查看当前设置：

```bash
uv run src/advanced/asyncio/config.py
```

输出示例：
```
=== 当前配置 ===
API Token: **********ea7.16
最大并发数: 10
超时时间: 60秒
================
```

## 安全提醒

1. **不要在代码中硬编码 API 密钥**
2. **将 .env 文件添加到 .gitignore**
3. **使用环境变量管理敏感配置**
4. **定期轮换 API 密钥**

## 故障排除

### 问题：脚本提示使用默认 token
**解决方案**：检查环境变量是否正确设置
```bash
echo $EODHD_API_TOKEN  # macOS/Linux
echo %EODHD_API_TOKEN% # Windows
```

### 问题：API 请求频率过高被限制
**解决方案**：降低并发数
```bash
export MAX_CONCURRENT_REQUESTS=3
```

### 问题：请求超时
**解决方案**：增加超时时间
```bash
export TIMEOUT_SECONDS=60
``` 