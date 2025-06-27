from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
from .search import baidu_search
from .keywords import generate_keywords

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

class SearchResponse(BaseModel):
    original_keyword: str
    search_results: List[Dict[str, Any]]
    generated_keywords: List[str]
    success: bool
    message: str

@app.get("/")
async def root():
    return {"message": "智能搜索助手API", "version": "1.0"}

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """执行搜索并生成相关关键词"""
    try:
        print(f"收到搜索请求: {request.keyword}")
        
        # 执行搜索
        search_results = await baidu_search(request.keyword, request.max_results)
        
        # 生成相关关键词
        generated_keywords = []
        if search_results:
            # 使用搜索结果生成关键词
            result_text = " ".join([result.get('title', '') + " " + result.get('snippet', '') for result in search_results])
            generated_keywords = await generate_keywords(result_text, request.generate_keywords_count)
        else:
            # 如果搜索失败，直接基于原关键词生成
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 