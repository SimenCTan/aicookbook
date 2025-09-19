# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-dotenv",
#     "requests",
# ]
# ///

import os
import requests
import json
import time
import sys
import math
from dotenv import load_dotenv

# API 配置
load_dotenv()
EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL")
EMBEDDING_API_URL_IMAGE = os.getenv("EMBEDDING_API_URL_IMAGE")
REANK_API_URL = os.getenv("REANK_API_URL")
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY")


def test_health():
    """测试健康检查端点"""
    print("测试健康检查...")
    response = requests.get(f"{EMBEDDING_API_URL}/health")
    if response.status_code == 200:
        print("✓ 健康检查通过")
        return True
    else:
        print("✗ 健康检查失败")
        return False


def test_models():
    """获取模型信息"""
    print("\n获取模型信息...")
    headers = {"Content-Type": "application/json"}
    if EMBEDDING_API_KEY:
        headers["Authorization"] = f"Bearer {EMBEDDING_API_KEY}"
    response = requests.get(f"{EMBEDDING_API_URL}/models", headers=headers)
    if response.status_code == 200:
        models = response.json()
        print(f"✓ 可用模型: {json.dumps(models, indent=2)}")
        return True
    else:
        print("✗ 无法获取模型信息")
        return False


def test_embedding():
    """测试嵌入生成"""
    print("\n测试嵌入生成...")

    headers = {"Content-Type": "application/json"}
    if EMBEDDING_API_KEY:
        headers["Authorization"] = f"Bearer {EMBEDDING_API_KEY}"

    # 测试数据
    data = {
        "model": "BAAI/bge-m3",
        "input": [
            "BGE M3 is a versatile embedding model",
            "它支持多语言、多粒度和多功能",
            "Supports dense, sparse, and multi-vector retrieval",
        ],
    }

    start_time = time.time()
    response = requests.post(
        f"{EMBEDDING_API_URL}/embeddings", headers=headers, json=data
    )
    elapsed_time = time.time() - start_time

    if response.status_code == 200:
        result = response.json()
        print(f"✓ 嵌入生成成功")
        print(f"  - 生成 {len(result['data'])} 个嵌入")
        print(f"  - 维度: {len(result['data'][0]['embedding'])}")
        # print(f"  - 结果: {result['data'][0]['embedding']}")
        print(f"  - 耗时: {elapsed_time:.2f} 秒")
        print(f"  - Token 使用: {result.get('usage', {})}")
        return True
    else:
        print(f"✗ 嵌入生成失败: {response.status_code}")
        print(f"  错误: {response.text}")
        return False


def test_image_embedding():
    """测试图片嵌入生成"""
    print("\n测试图片嵌入生成...")

    headers = {"Content-Type": "application/json"}
    if EMBEDDING_API_KEY:
        headers["Authorization"] = f"Bearer {EMBEDDING_API_KEY}"

    data = {
        "model": "google/siglip-so400m-patch14-384",
        # "encoding_format": "base64",
        "input": [
            "http://images.cocodataset.org/val2017/000000039769.jpg",
        ],
        "modality": "image",
    }

    start_time = time.time()
    response = requests.post(
        f"{EMBEDDING_API_URL_IMAGE}/embeddings", headers=headers, json=data
    )
    elapsed_time = time.time() - start_time

    if response.status_code == 200:
        result = response.json()
        print("✓ 图片嵌入生成成功")
        embedding_value = result["data"][0]["embedding"]
        if isinstance(embedding_value, list):
            print(f"  - 维度: {len(embedding_value)}")
        else:
            print(f"  - 返回编码: base64 字符串, 长度 {len(embedding_value)}")
        print(f"  - 耗时: {elapsed_time:.2f} 秒")
        print(f"  - Token 使用: {result.get('usage', {})}")
        return True
    else:
        print(f"✗ 图片嵌入生成失败: {response.status_code}")
        print(f"  错误: {response.text}")
        return False


def test_text_search_siglip():
    """使用 google/siglip-so400m-patch14-384 进行文本相似度搜索"""
    print("\n测试 SigLIP 文本搜索...")

    headers = {"Content-Type": "application/json"}
    if EMBEDDING_API_KEY:
        headers["Authorization"] = f"Bearer {EMBEDDING_API_KEY}"

    # 示例查询与文档
    query = "best city to visit in france"
    documents = [
        "Paris is the capital of France and a popular tourist destination.",
        "Berlin is known for its vibrant arts scene.",
        "The Eiffel Tower is located in Paris.",
        "Tokyo is a bustling city with amazing food.",
    ]

    inputs = [query] + documents
    data = {
        "model": "google/siglip-so400m-patch14-384",
        "input": inputs,
        # 文本默认即为 text 模态，可不显式设置
        # "modality": "text",
    }

    start_time = time.time()
    response = requests.post(
        f"{EMBEDDING_API_URL}/embeddings", headers=headers, json=data
    )
    elapsed_time = time.time() - start_time

    if response.status_code != 200:
        print(f"✗ SigLIP 文本搜索失败: {response.status_code}")
        print(f"  错误: {response.text}")
        return False

    result = response.json()
    vectors = [item["embedding"] for item in result["data"]]
    query_vec, doc_vecs = vectors[0], vectors[1:]

    def cosine_similarity(vec_a, vec_b):
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    scores = [
        (cosine_similarity(query_vec, v), doc) for v, doc in zip(doc_vecs, documents)
    ]
    scores.sort(key=lambda x: x[0], reverse=True)

    print("✓ SigLIP 文本搜索成功")
    print(f"  - 批次大小: {len(inputs)} (含 1 个查询 + {len(documents)} 个文档)")
    print(f"  - 耗时: {elapsed_time:.2f} 秒")
    print("  - Top 3 结果：")
    for rank, (score, doc) in enumerate(scores[:3], start=1):
        print(f"    {rank}. {score:.4f} - {doc}")

    return True


def test_rerank():
    """测试重排序（如果部署了重排序模型）"""
    print("\n测试重排序...")

    headers = {"Content-Type": "application/json"}
    if EMBEDDING_API_KEY:
        headers["Authorization"] = f"Bearer {EMBEDDING_API_KEY}"

    data = {
        "model": "BAAI/bge-reranker-v2-m3",
        "query": "What is BGE M3?",
        "documents": [
            "BGE M3 is an embedding model",
            "Paris is in France",
            "BGE M3 supports multiple languages and retrieval methods",
        ],
    }

    response = requests.post(f"{REANK_API_URL}/rerank", headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        print("✓ 重排序成功")
        print(f"  结果: {json.dumps(result, indent=2)}")
        return True
    elif response.status_code == 404:
        print("ℹ 重排序模型未部署")
        return True
    else:
        print(f"✗ 重排序失败: {response.status_code}")
        return False


def benchmark():
    """性能基准测试"""
    print("\n运行性能基准测试...")

    headers = {"Content-Type": "application/json"}
    if EMBEDDING_API_KEY:
        headers["Authorization"] = f"Bearer {EMBEDDING_API_KEY}"

    # 不同长度的文本
    test_cases = [
        ("短文本", ["Hello world"] * 10),
        (
            "中等文本",
            ["This is a medium length sentence for testing embedding generation."] * 10,
        ),
        (
            "长文本",
            ["This is a very long text that contains multiple sentences. " * 50] * 5,
        ),
    ]

    for name, texts in test_cases:
        data = {"model": "BAAI/bge-m3", "input": texts}

        start_time = time.time()
        response = requests.post(
            f"{EMBEDDING_API_URL}/embeddings", headers=headers, json=data
        )
        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            throughput = len(texts) / elapsed_time
            print(f"\n{name}:")
            print(f"  - 批次大小: {len(texts)}")
            print(f"  - 耗时: {elapsed_time:.2f} 秒")
            print(f"  - 吞吐量: {throughput:.2f} 文本/秒")
            print(f"  - Token 数: {result.get('usage', {}).get('total_tokens', 'N/A')}")


def main() -> None:
    """主函数"""
    print("=" * 50)
    print("BGE-M3 Infinity API 测试")
    print("=" * 50)

    # 允许自定义 API URL
    if len(sys.argv) > 1:
        global EMBEDDING_API_URL
        EMBEDDING_API_URL = sys.argv[1]
        print(f"使用自定义 API URL: {EMBEDDING_API_URL}")

    # 运行测试
    all_passed = True

    if not test_health():
        print("\n服务未就绪，请稍后再试")
        return 1

    all_passed &= test_models()
    all_passed &= test_embedding()
    all_passed &= test_image_embedding()
    all_passed &= test_text_search_siglip()
    test_rerank()  # 可选测试

    # 询问是否运行基准测试
    response = input("\n是否运行性能基准测试? (y/n): ")
    if response.lower() == "y":
        benchmark()

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有测试通过!")
        return 0
    else:
        print("✗ 部分测试失败")
        return 1


if __name__ == "__main__":
    main()
