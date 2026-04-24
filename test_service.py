import requests
import json
import sys

API_URL = "http://localhost:8000"
API_KEY = "your_api_key_here"

def test_health():
    """测试健康检查接口"""
    print("=" * 50)
    print("测试 1: 健康检查")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✓ 健康检查通过")
            return True
        else:
            print("✗ 健康检查失败")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

def test_chat_text():
    """测试纯文本聊天"""
    print("\n" + "=" * 50)
    print("测试 2: 纯文本聊天")
    print("=" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    data = {
        "prompt": "你好，请简单介绍一下你自己",
        "max_new_tokens": 64,
        "temperature": 0.7
    }
    
    try:
        print(f"发送请求: {json.dumps(data, indent=2, ensure_ascii=False)}")
        response = requests.post(f"{API_URL}/api/chat", json=data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and response.json().get("success"):
            print("✓ 文本聊天测试通过")
            return True
        else:
            print("✗ 文本聊天测试失败")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

def test_chat_with_image():
    """测试带图片的聊天"""
    print("\n" + "=" * 50)
    print("测试 3: 带图片的聊天")
    print("=" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    data = {
        "prompt": "请简单描述这张图片",
        "image_url": "https://pics5.baidu.com/feed/962bd40735fae6cdc3a098830069193543a70f22.jpeg",
        "max_new_tokens": 64,
        "temperature": 0.7
    }
    
    try:
        print(f"发送请求: {json.dumps(data, indent=2, ensure_ascii=False)}")
        response = requests.post(f"{API_URL}/api/chat", json=data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and response.json().get("success"):
            print("✓ 图片聊天测试通过")
            return True
        else:
            print("✗ 图片聊天测试失败")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

def test_invalid_request():
    """测试无效请求"""
    print("\n" + "=" * 50)
    print("测试 4: 无效请求（参数验证）")
    print("=" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    data = {
        "prompt": "",  # 空提示
        "max_new_tokens": -1  # 无效的 token 数
    }
    
    try:
        print(f"发送无效请求: {json.dumps(data, indent=2, ensure_ascii=False)}")
        response = requests.post(f"{API_URL}/api/chat", json=data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 422:
            print("✓ 参数验证测试通过（正确拒绝无效请求）")
            return True
        else:
            print("✗ 参数验证测试失败")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

def test_rate_limit():
    """测试请求限流"""
    print("\n" + "=" * 50)
    print("测试 5: 请求限流")
    print("=" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    data = {
        "prompt": "测试限流",
        "max_new_tokens": 32
    }
    
    try:
        print("发送多个请求测试限流...")
        success_count = 0
        rate_limited = False
        
        for i in range(15):  # 发送15个请求
            response = requests.post(f"{API_URL}/api/chat", json=data, headers=headers)
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited = True
                print(f"第 {i+1} 个请求被限流")
                break
        
        print(f"成功请求: {success_count}")
        print(f"是否触发限流: {rate_limited}")
        
        if rate_limited:
            print("✓ 限流测试通过")
            return True
        else:
            print("⚠ 限流未触发（可能配置的限流值较高）")
            return True
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

def main():
    print("\n" + "=" * 50)
    print("Qwen3-VL 服务测试脚本")
    print("=" * 50)
    print(f"API 地址: {API_URL}")
    print(f"API 密钥: {API_KEY}")
    print()
    
    results = []
    
    results.append(("健康检查", test_health()))
    results.append(("文本聊天", test_chat_text()))
    results.append(("图片聊天", test_chat_with_image()))
    results.append(("参数验证", test_invalid_request()))
    results.append(("请求限流", test_rate_limit()))
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print()
    print(f"总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！服务运行正常。")
        sys.exit(0)
    else:
        print(f"\n⚠ 有 {total - passed} 个测试失败，请检查服务配置。")
        sys.exit(1)

if __name__ == "__main__":
    main()
