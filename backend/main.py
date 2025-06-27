from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import httpx
import json
import os
from search import baidu_search
from keywords import generate_keywords, generate_summary_deepseek
from cc98_search import cc98_searcher

app = FastAPI(title="智能搜索助手", description="基于百度搜索和AI关键词生成的智能搜索系统")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    keyword: str
    max_results: int = 5
    generate_keywords_count: int = 5
    search_source: str = "baidu"

class SearchResponse(BaseModel):
    original_keyword: str
    search_results: List[Dict[str, Any]]
    generated_keywords: List[str]
    success: bool
    message: str

class SummarizeRequest(BaseModel):
    content: str
    max_length: int = 200

class SummarizeResponse(BaseModel):
    original_content: str
    summary: str
    success: bool
    message: str

class ContentItem(BaseModel):
    title: str
    content: str

class IntegrateRequest(BaseModel):
    contents: List[ContentItem]
    keyword: str

class TreeNode(BaseModel):
    keyword: str
    results: List[ContentItem]

class TreeIntegrationRequest(BaseModel):
    nodes: List[TreeNode]
    main_keyword: str

@app.get("/")
async def root():
    return {"message": "智能搜索助手API", "version": "1.0"}

@app.post("/search")
async def search_keyword(request: SearchRequest):
    """搜索关键词并生成相关关键词"""
    try:
        print(f"收到搜索请求，关键词: {request.keyword}, 搜索源: {request.search_source}")
        print(f"搜索源类型: {type(request.search_source)}")
        print(f"搜索源值: '{request.search_source}'")
        print(f"搜索源是否等于'cc98': {request.search_source == 'cc98'}")
        
        search_results = []
        
        # 根据搜索源选择不同的搜索方法
        if request.search_source == 'cc98':
            print("使用CC98搜索...")
            # 使用CC98搜索
            search_results = await cc98_searcher.search_cc98(request.keyword, request.max_results)
            
            # 如果CC98搜索失败，降级到百度搜索
            if not search_results:
                print("CC98搜索失败，降级到百度搜索...")
                search_results = await baidu_search(request.keyword, request.max_results)
        else:
            print("使用百度搜索...")
            # 默认使用百度搜索
            search_results = await baidu_search(request.keyword, request.max_results)
        
        if not search_results:
            return SearchResponse(
                original_keyword=request.keyword,
                search_results=[],
                generated_keywords=[],
                success=False,
                message="搜索失败，未获取到结果"
            )
        
        print(f"搜索完成，获取到 {len(search_results)} 个结果")
        
        # 生成相关关键词
        generated_keywords = await generate_keywords(request.keyword, request.generate_keywords_count)
        
        return SearchResponse(
            original_keyword=request.keyword,
            search_results=search_results,
            generated_keywords=generated_keywords,
            success=True,
            message="搜索完成"
        )
        
    except Exception as e:
        print(f"搜索过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return SearchResponse(
            original_keyword=request.keyword,
            search_results=[],
            generated_keywords=[],
            success=False,
            message=f"搜索失败: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "message": "服务正常运行"}

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_content(request: SummarizeRequest):
    """使用DeepSeek API进行内容概括"""
    try:
        # 使用DeepSeek API进行内容概括
        summary = await generate_summary_deepseek(request.content, request.max_length)
        
        return SummarizeResponse(
            original_content=request.content,
            summary=summary,
            success=True,
            message="概括完成"
        )
    except Exception as e:
        print(f"概括过程中发生错误: {e}")
        return SummarizeResponse(
            original_content=request.content,
            summary="",
            success=False,
            message=f"概括失败: {str(e)}"
        )

@app.post("/integrate")
async def integrate_contents(request: IntegrateRequest):
    """使用DeepSeek API整合多篇内容"""
    try:
        # 构建整合提示词
        content_text = ""
        for i, item in enumerate(request.contents, 1):
            content_text += f"内容{i}：{item.title}\n{item.content}\n\n"
        
        prompt = f"""请整合以下关于"{request.keyword}"的多篇内容，生成一个连贯、全面的总结：

{content_text}

请按照以下要求进行整合：
1. 提取各篇内容的核心观点和重要信息
2. 消除重复内容，保持逻辑清晰
3. 按照主题相关性组织内容
4. 生成一个结构化的总结，包含主要观点和关键信息
5. 保持客观中立的语调
6. 总结长度控制在500-800字之间

请直接输出整合后的内容，不要添加额外的说明文字。"""

        # 使用DeepSeek API进行内容整合
        integration = await generate_summary_deepseek(prompt, 800)
        
        return {
            "success": True,
            "integration": integration
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.post("/integrate-tree")
async def integrate_tree_contents(request: TreeIntegrationRequest):
    """使用DeepSeek API整合整棵搜索树的内容"""
    try:
        # 构建整合提示词
        content_text = ""
        for i, node in enumerate(request.nodes, 1):
            content_text += f"=== 节点{i}：{node.keyword} ===\n"
            for j, result in enumerate(node.results, 1):
                content_text += f"结果{j}：{result.title}\n{result.content}\n\n"
        
        prompt = f"""请整合以下关于"{request.main_keyword}"的整棵搜索树内容，生成一个全面、系统的总结：

{content_text}

请按照以下要求进行整合：
1. 分析各个搜索节点的主题关联性和层次结构
2. 提取每个节点的核心观点和重要信息
3. 识别不同节点间的联系和差异
4. 按照逻辑层次组织内容，形成完整的知识体系
5. 消除重复信息，突出关键观点
6. 生成一个结构化的综合总结，包含：
   - 主要主题和子主题
   - 核心观点和关键信息
   - 不同角度的分析
   - 整体结论和见解
7. 保持客观中立的语调
8. 总结长度控制在800-1200字之间

请直接输出整合后的内容，不要添加额外的说明文字。"""

        # 使用DeepSeek API进行内容整合
        integration = await generate_summary_deepseek(prompt, 1200)
        
        return {
            "success": True,
            "integration": integration
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 