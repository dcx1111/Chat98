import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
import httpx
import os
from typing import List
import jieba.analyse
import json
from openai import OpenAI
from api_keys import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

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
        
        prompt = f"""基于以下关键词或主题，生成{count}个发散但相关的搜索关键词。

要求：
1. 关键词应该与主题高度相关，但不要局限于简单的同义词
2. 考虑主题的各个方面、相关概念、影响因素、应用场景等
3. 关键词应该具有搜索价值，能够找到相关内容
4. 长度适中（2-8个字符）
5. 避免过于宽泛或过于具体的词汇

示例：
- 如果主题是"保研"，可以生成：导师、均绩、挂科、科研、竞赛、夏令营、推免、面试等
- 如果主题是"微积分"，可以生成：导数、积分、极限、微分方程、数学分析、高等数学等
- 如果主题是"人工智能"，可以生成：机器学习、深度学习、神经网络、算法、数据科学等

主题：{text}

请只返回关键词列表，每行一个关键词，不要其他解释："""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的关键词生成助手，能够根据主题生成发散但相关的搜索关键词。你善于从不同角度思考主题，生成有价值的搜索词。"},
                {"role": "user", "content": prompt}
            ],
            stream=False,
            temperature=0.8,  # 提高温度以获得更多样化的结果
            max_tokens=300
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
    
    prompt = f"""基于以下关键词或主题，生成{count}个发散但相关的搜索关键词。

要求：
1. 关键词应该与主题高度相关，但不要局限于简单的同义词
2. 考虑主题的各个方面、相关概念、影响因素、应用场景等
3. 关键词应该具有搜索价值，能够找到相关内容
4. 长度适中（2-8个字符）
5. 避免过于宽泛或过于具体的词汇

示例：
- 如果主题是"保研"，可以生成：导师、均绩、挂科、科研、竞赛、夏令营、推免、面试等
- 如果主题是"微积分"，可以生成：导数、积分、极限、微分方程、数学分析、高等数学等
- 如果主题是"人工智能"，可以生成：机器学习、深度学习、神经网络、算法、数据科学等

主题：{text}

请只返回关键词列表，每行一个关键词，不要其他解释："""

    json_data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.8,  # 提高温度以获得更多样化的结果
        "max_tokens": 300
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
    """提取关键词的主函数"""
    return extract_keywords_tfidf(origin_keyword, texts, top_k)

async def generate_summary_deepseek(content: str, max_length: int = 200) -> str:
    """使用DeepSeek API生成内容概括"""
    try:
        print(f"正在调用DeepSeek API生成概括...")
        
        # 使用OpenAI SDK方式调用DeepSeek API
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        
        prompt = f"""请对以下内容进行概括，要求：
1. 概括要简洁明了，突出重点
2. 保持原文的核心信息和主要观点
3. 概括长度控制在{max_length}字以内
4. 使用客观的语言，避免主观评价

原文内容：
{content}

请直接返回概括内容，不要添加其他解释："""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的内容概括助手，能够准确、简洁地概括文本内容。"},
                {"role": "user", "content": prompt}
            ],
            stream=False,
            temperature=0.3,
            max_tokens=500
        )
        
        print(f"DeepSeek API调用成功")
        summary = response.choices[0].message.content
        print(f"DeepSeek API返回概括: {summary}")
        
        return summary.strip() if summary else "概括生成失败"
        
    except Exception as e:
        print(f"DeepSeek概括生成失败: {e}")
        print(f"错误类型: {type(e)}")
        # 降级到简单概括
        return generate_summary_simple(content, max_length)

def generate_summary_simple(content: str, max_length: int = 200) -> str:
    """简单的概括功能（降级方案）"""
    try:
        # 简单的概括逻辑：取前几句话
        sentences = content.split('。')
        summary = ""
        for sentence in sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + "。"
            else:
                break
        
        if not summary:
            # 如果句子太长，直接截取
            summary = content[:max_length] + "..."
        
        print(f"简单概括生成: {summary}")
        return summary
        
    except Exception as e:
        print(f"简单概括生成失败: {e}")
        return "概括生成失败"