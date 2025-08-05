## 一、异步编程基础概念

### 1. 理解同步vs异步
- **同步编程**：代码按顺序执行，一个任务完成后才执行下一个
- **异步编程**：任务可以在等待期间让出控制权，让其他任务执行
- **适用场景**：I/O密集型任务（网络请求、文件读写、数据库查询）

### 2. 核心概念
```python
# 事件循环（Event Loop）：是整个异步系统的引擎，负责调度和执行所有异步操作
# 协程（Coroutine）：是异步编程的基本单位，定义了可以暂停和恢复的操作，可以暂停和恢复的函数
# 任务（Task）：是协程的运行时封装，使协程能在事件循环中并发执行
# Future：代表将来会有结果的对象
```

## 二、asyncio基础入门

### 1. 基本语法
```python
import asyncio
import time

# 定义异步函数
async def hello_world():
    print("Hello")
    await asyncio.sleep(1)  # 异步等待
    print("World")

# 运行异步函数
asyncio.run(hello_world())
```

### 2. await关键字
```python
async def fetch_data():
    print("开始获取数据...")
    await asyncio.sleep(2)  # 模拟网络请求
    return {"data": "some data"}

async def main():
    # await必须在async函数中使用
    result = await fetch_data()
    print(f"获取到数据: {result}")

asyncio.run(main())
```

### 3. 并发执行多个任务
```python
async def task(name, delay):
    print(f"任务 {name} 开始")
    await asyncio.sleep(delay)
    print(f"任务 {name} 完成")
    return f"{name} 结果"

async def main():
    # 方法1：使用gather
    results = await asyncio.gather(
        task("A", 2),
        task("B", 1),
        task("C", 3)
    )
    print(f"所有结果: {results}")
    
    # 方法2：使用create_task
    task1 = asyncio.create_task(task("D", 2))
    task2 = asyncio.create_task(task("E", 1))
    
    result1 = await task1
    result2 = await task2
```

## 三、进阶应用

### 1. 异步上下文管理器
```python
class AsyncResource:
    async def __aenter__(self):
        print("获取资源")
        await asyncio.sleep(1)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("释放资源")
        await asyncio.sleep(0.5)
    
    async def do_something(self):
        print("使用资源")
        await asyncio.sleep(1)

async def main():
    async with AsyncResource() as resource:
        await resource.do_something()
```

### 2. 异步迭代器
```python
class AsyncCounter:
    def __init__(self, start, stop):
        self.current = start
        self.stop = stop
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.current < self.stop:
            await asyncio.sleep(0.5)
            self.current += 1
            return self.current - 1
        else:
            raise StopAsyncIteration

async def main():
    async for i in AsyncCounter(1, 5):
        print(f"计数: {i}")
```

### 3. 异步队列
```python
async def producer(queue, n):
    for i in range(n):
        await asyncio.sleep(1)
        await queue.put(f"item_{i}")
        print(f"生产: item_{i}")
    await queue.put(None)  # 结束信号

async def consumer(queue, name):
    while True:
        item = await queue.get()
        if item is None:
            await queue.put(None)  # 传递结束信号
            break
        print(f"{name} 消费: {item}")
        await asyncio.sleep(2)

async def main():
    queue = asyncio.Queue(maxsize=3)
    
    await asyncio.gather(
        producer(queue, 5),
        consumer(queue, "消费者1"),
        consumer(queue, "消费者2")
    )
```

## 四、实战项目示例

### 1. 异步HTTP请求
```python
import aiohttp
import asyncio

async def fetch_url(session, url):
    try:
        async with session.get(url) as response:
            return await response.text()
    except Exception as e:
        return f"Error: {e}"

async def fetch_multiple_urls(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

# 使用示例
urls = [
    "https://api.github.com",
    "https://httpbin.org/delay/1",
    "https://jsonplaceholder.typicode.com/posts/1"
]

results = asyncio.run(fetch_multiple_urls(urls))
```

### 2. 异步Web服务器
```python
from aiohttp import web

async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    await asyncio.sleep(1)  # 模拟异步处理
    text = f"Hello, {name}!"
    return web.Response(text=text)

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            await ws.send_str(f"Echo: {msg.data}")
        elif msg.type == web.WSMsgType.ERROR:
            print(f'Error: {ws.exception()}')
    
    return ws

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/{name}', handle)
app.router.add_get('/ws', websocket_handler)

# web.run_app(app, host='localhost', port=8080)
```

## 五、性能优化技巧

### 1. 限制并发数
```python
async def fetch_with_semaphore(url, session, semaphore):
    async with semaphore:  # 限制并发数
        async with session.get(url) as response:
            return await response.text()

async def limited_concurrent_fetch(urls, max_concurrent=5):
    semaphore = asyncio.Semaphore(max_concurrent)
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_with_semaphore(url, session, semaphore) 
            for url in urls
        ]
        return await asyncio.gather(*tasks)
```

### 2. 超时控制
```python
async def task_with_timeout():
    try:
        await asyncio.wait_for(
            some_long_operation(), 
            timeout=5.0
        )
    except asyncio.TimeoutError:
        print("操作超时")
```

### 3. 错误处理
```python
async def safe_task(name):
    try:
        await asyncio.sleep(1)
        if name == "error":
            raise ValueError("模拟错误")
        return f"{name} 成功"
    except Exception as e:
        return f"{name} 失败: {e}"

async def main():
    results = await asyncio.gather(
        safe_task("task1"),
        safe_task("error"),
        safe_task("task3"),
        return_exceptions=True  # 不会因为异常而中断
    )
```

## 六、学习资源和实践建议

### 1. 推荐学习路径
1. **基础阶段**（1-2周）
   - 理解事件循环概念
   - 掌握async/await语法
   - 练习简单的异步函数

2. **进阶阶段**（2-3周）
   - 学习asyncio高级特性
   - 实践异步网络编程
   - 理解并发控制

3. **实战阶段**（3-4周）
   - 构建异步Web应用
   - 异步数据库操作
   - 性能优化实践

### 2. 推荐实践项目
- 异步爬虫系统
- 实时聊天服务器
- 异步任务队列
- 高并发API网关

### 3. 注意事项
- 不要在异步函数中使用阻塞操作
- 合理使用异步库（aiohttp、aiofiles、asyncpg等）
- 注意内存管理，避免创建过多任务
- 使用日志调试异步代码

### 4. 推荐学习资源
- 官方文档：Python asyncio
- 书籍：《Python Asyncio并发编程》
- 实践项目：参考优秀的异步框架源码（FastAPI、Sanic）

通过系统学习和大量实践，你将能够熟练掌握Python异步编程，构建高性能的并发应用。记住，异步编程的核心是"等待时不要阻塞"，让CPU始终保持忙碌状态。