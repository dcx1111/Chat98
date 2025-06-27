import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
import httpx
import os
from typing import List
import jieba.analyse
import json
from openai import OpenAI
from .api_keys import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

# 加载停用词
def load_stopwords():
    """加载停用词库"""
    stopwords = set()
    
    # 1. 使用jieba自带的停用词
    try:
        import jieba.analyse
        # 使用jieba.analyse模块的默认停用词
        try:
            # 获取jieba默认的停用词
            jieba_stopwords = set(jieba.analyse.extract_tags("", topK=0))
            if jieba_stopwords:
                stopwords.update(jieba_stopwords)
        except Exception:
            # 如果获取失败，跳过
            pass
    except ImportError:
        # 如果jieba.analyse模块不存在，跳过
        pass
    
    # 2. 添加一些常见的中文停用词
    common_stopwords = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '什么', '怎么', '为什么', '如何', '哪些'
    }
    stopwords.update(common_stopwords)
    
    return stopwords

def extract_keywords_jieba(text: str, top_k: int = 10) -> List[str]:
    """使用jieba提取关键词（降级方案）"""
    try:
        # 使用jieba的TF-IDF提取关键词
        keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=False)
        # 确保返回的是字符串列表
        if keywords and isinstance(keywords[0], tuple):
            # 如果返回的是带权重的元组，只取关键词部分
            keywords = [kw[0] if isinstance(kw, tuple) else kw for kw in keywords]
        elif keywords and not isinstance(keywords[0], str):
            # 如果返回的不是字符串，转换为字符串
            keywords = [str(kw) for kw in keywords]
        # 确保返回的是字符串列表
        keywords = [str(kw) for kw in keywords]
        
        print(f"jieba提取到关键词: {keywords}")
        return keywords
    except Exception as e:
        print(f"jieba关键词提取失败: {e}")
        return []

def generate_keywords_simple(text: str, count: int = 5) -> List[str]:
    """简单的关键词生成（最终降级方案）"""
    try:
        # 基于文本长度和常见词汇生成简单关键词
        words = jieba.lcut(text)
        # 过滤停用词和短词
        filtered_words = [word for word in words if len(word) > 1 and word not in ['的', '是', '在', '有', '和', '与', '或', '但', '而', '如果', '因为', '所以']]
        
        # 去重并限制数量
        unique_words = list(set(filtered_words))[:count]
        print(f"简单关键词生成: {unique_words}")
        return unique_words
    except Exception as e:
        print(f"简单关键词生成失败: {e}")
        return []

async def generate_keywords_deepseek(text: str, count: int = 5) -> List[str]:
    """使用DeepSeek API生成相关关键词"""
    try:
        print(f"正在调用DeepSeek API生成关键词...")
        print(f"使用OpenAI SDK方式调用DeepSeek API")
        
        # 使用OpenAI SDK方式调用DeepSeek API
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        
        prompt = f"""基于以下文本，生成{count}个相关的搜索关键词。关键词应该：
1. 与原文内容高度相关
2. 适合用于网络搜索
3. 包含核心概念和重要术语
4. 长度适中（2-6个字符）

原文：{text}

请只返回关键词列表，每行一个关键词，不要其他解释："""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的关键词生成助手，能够根据文本内容生成相关的搜索关键词。"},
                {"role": "user", "content": prompt}
            ],
            stream=False,
            temperature=0.7,
            max_tokens=200
        )
        
        print(f"DeepSeek API调用成功")
        content = response.choices[0].message.content
        print(f"DeepSeek API返回内容: {content}")
        
        # 解析返回的关键词
        if content is None:
            print("DeepSeek API返回内容为空")
            return []
        
        keywords = [line.strip() for line in content.split('\n') if line.strip()]
        print(f"DeepSeek生成关键词: {keywords}")
        return keywords[:count]
        
    except Exception as e:
        print(f"DeepSeek关键词生成失败: {e}")
        print(f"错误类型: {type(e)}")
        raise e

async def generate_keywords_deepseek_httpx(text: str, count: int = 5) -> List[str]:
    """使用httpx调用DeepSeek API（备用方案）"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""基于以下文本，生成{count}个相关的搜索关键词。关键词应该：
1. 与原文内容高度相关
2. 适合用于网络搜索
3. 包含核心概念和重要术语
4. 长度适中（2-6个字符）

原文：{text}

请只返回关键词列表，每行一个关键词，不要其他解释："""

    json_data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    try:
        print(f"正在调用DeepSeek API生成关键词（httpx方式）...")
        print(f"请求URL: {DEEPSEEK_BASE_URL}/v1/chat/completions")
        print(f"请求头: {headers}")
        print(f"请求体: {json_data}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{DEEPSEEK_BASE_URL}/v1/chat/completions", headers=headers, json=json_data)
            print(f"DeepSeek API响应状态码: {resp.status_code}")
            
            if resp.status_code != 200:
                print(f"DeepSeek API调用失败，状态码: {resp.status_code}")
                print(f"响应内容: {resp.text}")
                if resp.status_code == 401:
                    print("DeepSeek API Key无效")
                elif resp.status_code == 402:
                    print("DeepSeek API需要付费或余额不足")
                elif resp.status_code == 429:
                    print("DeepSeek API请求频率超限")
                raise Exception(f"DeepSeek API调用失败: {resp.status_code}")
            
            data = resp.json()
            print(f"DeepSeek API返回数据: {data}")
            
            content = data["choices"][0]["message"]["content"]
            # 解析返回的关键词
            keywords = [line.strip() for line in content.split('\n') if line.strip()]
            print(f"DeepSeek生成关键词: {keywords}")
            return keywords[:count]
            
    except httpx.ConnectTimeout:
        print("DeepSeek API连接超时")
        raise Exception("DeepSeek API连接超时")
    except httpx.RequestError as e:
        print(f"DeepSeek API请求错误: {e}")
        raise Exception(f"DeepSeek API请求错误: {e}")
    except Exception as e:
        print(f"DeepSeek关键词生成失败: {e}")
        raise e

async def generate_keywords(text: str, count: int = 5) -> List[str]:
    """生成关键词的主函数，包含多层降级"""
    try:
        # 首先尝试使用OpenAI SDK方式调用DeepSeek API
        keywords = await generate_keywords_deepseek(text, count)
        if keywords:
            return keywords
    except Exception as e:
        print(f"OpenAI SDK方式DeepSeek关键词生成失败: {e}")
        
        try:
            # 降级到httpx方式调用DeepSeek API
            keywords = await generate_keywords_deepseek_httpx(text, count)
            if keywords:
                return keywords
        except Exception as e2:
            print(f"httpx方式DeepSeek关键词生成也失败: {e2}")
    
    try:
        # 降级到jieba关键词提取
        keywords = extract_keywords_jieba(text, count)
        if keywords:
            return keywords
    except Exception as e:
        print(f"jieba关键词提取失败: {e}")
    
    try:
        # 最终降级到简单关键词生成
        keywords = generate_keywords_simple(text, count)
        return keywords
    except Exception as e:
        print(f"所有关键词生成方法都失败了: {e}")
        return []

def extract_keywords_tfidf(origin_keyword: str, texts: list, top_k: int = 5):
    """使用TF-IDF提取关键词（保留原有函数）"""
    try:
        # 合并所有文本
        combined_text = " ".join(texts)
        
        # 使用jieba的TF-IDF提取关键词
        keywords = jieba.analyse.extract_tags(combined_text, topK=top_k*2, withWeight=False)
        
        # 过滤掉与原始关键词过于相似的关键词
        filtered_keywords = []
        for keyword in keywords:
            if keyword != origin_keyword and len(keyword) > 1:
                filtered_keywords.append(keyword)
        
        return filtered_keywords[:top_k]
    except Exception as e:
        print(f"TF-IDF关键词提取失败: {e}")
        return []

# 保持向后兼容
def extract_keywords(origin_keyword: str, texts: list, top_k: int = 5):
    """保持原有接口，但内部使用改进的方法"""
    return extract_keywords_tfidf(origin_keyword, texts, top_k)