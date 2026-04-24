"""
Qwen3-VL API 使用示例

本文件展示了如何使用 Qwen3-VL 大模型服务的各种方法。
"""

import requests
import json
from typing import Optional, List, Dict


class Qwen3VLClient:
    """Qwen3-VL API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            self.headers["X-API-Key"] = api_key
    
    def health_check(self) -> Dict:
        """健康检查"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def chat(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        max_new_tokens: int = 128,
        temperature: float = 0.7,
        top_p: float = 0.95
    ) -> Dict:
        """
        发送聊天请求
        
        Args:
            prompt: 用户输入的文本提示
            image_url: 图片 URL 地址（可选）
            max_new_tokens: 最大生成 token 数
            temperature: 温度参数
            top_p: top_p 采样参数
        
        Returns:
            API 响应
        """
        data = {
            "prompt": prompt,
            "image_url": image_url,
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=data,
            headers=self.headers
        )
        return response.json()
    
    def chat_with_history(
        self,
        messages: List[Dict],
        max_new_tokens: int = 128,
        temperature: float = 0.7,
        top_p: float = 0.95
    ) -> Dict:
        """
        发送带历史记录的聊天请求
        
        Args:
            messages: 消息历史列表
            max_new_tokens: 最大生成 token 数
            temperature: 温度参数
            top_p: top_p 采样参数
        
        Returns:
            API 响应
        """
        data = {
            "messages": messages,
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat/history",
            json=data,
            headers=self.headers
        )
        return response.json()


def example_1_simple_chat():
    """示例 1: 简单文本对话"""
    print("=" * 60)
    print("示例 1: 简单文本对话")
    print("=" * 60)
    
    client = Qwen3VLClient()
    
    response = client.chat(
        prompt="你好，请简单介绍一下你自己",
        max_new_tokens=64
    )
    
    if response["success"]:
        print(f"AI 回复: {response['response']}")
    else:
        print(f"错误: {response['error']}")
    
    print()


def example_2_image_understanding():
    """示例 2: 图像理解"""
    print("=" * 60)
    print("示例 2: 图像理解")
    print("=" * 60)
    
    client = Qwen3VLClient()
    
    image_url = "https://pics5.baidu.com/feed/962bd40735fae6cdc3a098830069193543a70f22.jpeg"
    
    response = client.chat(
        prompt="请简单描述这张图片",
        image_url=image_url,
        max_new_tokens=64
    )
    
    if response["success"]:
        print(f"AI 回复: {response['response']}")
    else:
        print(f"错误: {response['error']}")
    
    print()


def example_3_multi_turn_conversation():
    """示例 3: 多轮对话"""
    print("=" * 60)
    print("示例 3: 多轮对话")
    print("=" * 60)
    
    client = Qwen3VLClient()
    
    messages = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什么我可以帮助你的吗？"},
        {"role": "user", "content": "请告诉我什么是人工智能"}
    ]
    
    response = client.chat_with_history(
        messages=messages,
        max_new_tokens=64
    )
    
    if response["success"]:
        print(f"AI 回复: {response['response']}")
    else:
        print(f"错误: {response['error']}")
    
    print()


def example_4_image_with_question():
    """示例 4: 图片问答"""
    print("=" * 60)
    print("示例 4: 图片问答")
    print("=" * 60)
    
    client = Qwen3VLClient()
    
    image_url = "https://pics5.baidu.com/feed/962bd40735fae6cdc3a098830069193543a70f22.jpeg"
    
    response = client.chat(
        prompt="图片中有几个人？他们在做什么？",
        image_url=image_url,
        max_new_tokens=64
    )
    
    if response["success"]:
        print(f"AI 回复: {response['response']}")
    else:
        print(f"错误: {response['error']}")
    
    print()


def example_5_creative_writing():
    """示例 5: 创意写作"""
    print("=" * 60)
    print("示例 5: 创意写作")
    print("=" * 60)
    
    client = Qwen3VLClient()
    
    response = client.chat(
        prompt="请写一首关于春天的短诗",
        max_new_tokens=128,
        temperature=0.9,
        top_p=0.95
    )
    
    if response["success"]:
        print(f"AI 回复:\n{response['response']}")
    else:
        print(f"错误: {response['error']}")
    
    print()


def example_6_error_handling():
    """示例 6: 错误处理"""
    print("=" * 60)
    print("示例 6: 错误处理")
    print("=" * 60)
    
    client = Qwen3VLClient(api_key="wrong_key")
    
    try:
        response = client.chat(prompt="测试")
        
        if not response["success"]:
            print(f"请求失败: {response.get('error', '未知错误')}")
        else:
            print(f"AI 回复: {response['response']}")
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请检查服务是否启动")
    except Exception as e:
        print(f"错误: {e}")
    
    print()


def example_7_batch_requests():
    """示例 7: 批量请求"""
    print("=" * 60)
    print("示例 7: 批量请求")
    print("=" * 60)
    
    client = Qwen3VLClient()
    
    questions = [
        "什么是机器学习？",
        "什么是深度学习？",
        "什么是神经网络？"
    ]
    
    results = []
    for question in questions:
        response = client.chat(prompt=question, max_new_tokens=32)
        if response["success"]:
            results.append((question, response["response"]))
        else:
            results.append((question, f"错误: {response['error']}"))
    
    for question, answer in results:
        print(f"问题: {question}")
        print(f"回答: {answer}\n")


def example_8_with_api_key():
    """示例 8: 使用 API 密钥"""
    print("=" * 60)
    print("示例 8: 使用 API 密钥")
    print("=" * 60)
    
    api_key = "your_secure_api_key_here"
    client = Qwen3VLClient(api_key=api_key)
    
    response = client.chat(
        prompt="你好，请介绍一下你自己",
        max_new_tokens=64
    )
    
    if response["success"]:
        print(f"AI 回复: {response['response']}")
    else:
        print(f"错误: {response['error']}")
    
    print()


def example_9_custom_parameters():
    """示例 9: 自定义生成参数"""
    print("=" * 60)
    print("示例 9: 自定义生成参数")
    print("=" * 60)
    
    client = Qwen3VLClient()
    
    prompt = "请写一个简短的故事"
    
    print("使用不同的温度参数:")
    temperatures = [0.3, 0.7, 1.0]
    
    for temp in temperatures:
        response = client.chat(
            prompt=prompt,
            max_new_tokens=64,
            temperature=temp
        )
        
        if response["success"]:
            print(f"\n温度 {temp}:")
            print(response['response'])
    
    print()


def example_10_health_check():
    """示例 10: 健康检查"""
    print("=" * 60)
    print("示例 10: 健康检查")
    print("=" * 60)
    
    client = Qwen3VLClient()
    
    health = client.health_check()
    
    print(f"服务状态: {health['status']}")
    print(f"模型已加载: {health['model_loaded']}")
    print(f"设备: {health['device']}")
    print(f"时间戳: {health['timestamp']}")
    
    print()


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("Qwen3-VL API 使用示例")
    print("=" * 60)
    print()
    
    examples = [
        ("简单文本对话", example_1_simple_chat),
        ("图像理解", example_2_image_understanding),
        ("多轮对话", example_3_multi_turn_conversation),
        ("图片问答", example_4_image_with_question),
        ("创意写作", example_5_creative_writing),
        ("错误处理", example_6_error_handling),
        ("批量请求", example_7_batch_requests),
        ("使用 API 密钥", example_8_with_api_key),
        ("自定义生成参数", example_9_custom_parameters),
        ("健康检查", example_10_health_check)
    ]
    
    print("可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\n输入示例编号运行特定示例，或输入 'all' 运行所有示例:")
    choice = input("> ").strip()
    
    if choice.lower() == "all":
        for name, example_func in examples:
            try:
                example_func()
            except Exception as e:
                print(f"示例执行失败: {e}\n")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        idx = int(choice) - 1
        name, example_func = examples[idx]
        try:
            example_func()
        except Exception as e:
            print(f"示例执行失败: {e}")
    else:
        print("无效的选择")


if __name__ == "__main__":
    main()
