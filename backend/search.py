import httpx
from typing import List, Dict, Any
import socket
from api_keys import BAIDU_API_KEY

# 百度千帆AI搜索API配置
BAIDU_SEARCH_URL = "https://qianfan.baidubce.com/v2/ai_search/chat/completions"

def test_network_connectivity():
    """测试网络连接"""
    try:
        # 测试DNS解析
        host = "qianfan.baidubce.com"
        ip = socket.gethostbyname(host)
        print(f"DNS解析成功: {host} -> {ip}")
        return True
    except socket.gaierror as e:
        print(f"DNS解析失败: {e}")
        return False
    except Exception as e:
        print(f"网络连接测试失败: {e}")
        return False

async def baidu_search(query: str, count: int = 5) -> List[Dict[str, Any]]:
    """使用百度千帆AI搜索API进行网页搜索"""
    # 首先测试网络连接
    if not test_network_connectivity():
        print("网络连接测试失败，跳过API调用")
        return []
    
    headers = {
        "Authorization": f"Bearer {BAIDU_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 根据官方接口示例，构建正确的请求体
    json_data = {
        "messages": [
            {
                "content": query,
                "role": "user"
            }
        ]
        # 去除search_filter，允许搜索全网内容
    }
    
    try:
        print(f"正在调用百度搜索API，关键词: {query}")
        print(f"请求URL: {BAIDU_SEARCH_URL}")
        print(f"请求头: {headers}")
        print(f"请求体: {json_data}")
        
        # 增加连接超时和重试机制
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            resp = await client.post(BAIDU_SEARCH_URL, headers=headers, json=json_data)
            print(f"百度API响应状态码: {resp.status_code}")
            
            if resp.status_code != 200:
                print(f"百度API调用失败，状态码: {resp.status_code}")
                print(f"响应内容: {resp.text}")
                if resp.status_code == 400:
                    print("百度API请求参数错误")
                elif resp.status_code == 401:
                    print("百度API Key无效或权限不足")
                elif resp.status_code == 403:
                    print("百度API余额不足或超出限制")
                elif resp.status_code == 404:
                    print("百度API地址不存在")
                elif resp.status_code == 500:
                    print("百度API服务端执行错误")
                elif resp.status_code == 501:
                    print("百度API调用模型服务超时")
                elif resp.status_code == 502:
                    print("百度API模型流式输出超时")
                return []
            
            data = resp.json()
            print(f"百度API返回数据: {data}")
            
            # 解析搜索结果
            results = []
            if "search_info" in data and "search_results" in data["search_info"]:
                for item in data["search_info"]["search_results"]:
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "url": item.get("url", "")
                    })
            elif "references" in data:
                # 备用解析方式
                for item in data.get("references", []):
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("content", ""),
                        "url": item.get("url", "")
                    })
            
            print(f"解析到 {len(results)} 个搜索结果")
            return results
    except httpx.ConnectTimeout:
        print("百度搜索API连接超时")
        return []
    except httpx.ConnectError as e:
        print(f"百度搜索API连接错误: {e}")
        print(f"连接错误详情: {type(e).__name__}")
        return []
    except httpx.RequestError as e:
        print(f"百度搜索API请求错误: {e}")
        print(f"错误类型: {type(e)}")
        return []
    except Exception as e:
        print(f"百度搜索API调用失败: {e}")
        print(f"错误类型: {type(e)}")
        return []