# 智能搜索助手

一个基于AI的智能搜索和关键词衍生系统，集成了百度搜索API和DeepSeek关键词生成API。

## 功能特性

- 🔍 **智能搜索**: 基于百度搜索API获取搜索结果
- 🤖 **AI关键词生成**: 使用DeepSeek API生成相关关键词
- 🌳 **树状展示**: 层级化展示搜索历史和关键词衍生
- 📊 **结果管理**: 每个节点存储搜索结果，支持查看和重新搜索
- 🎯 **具体查看**: 点击查看完整的搜索结果详情
- 🔄 **换一批**: 重新搜索相同关键词获取新结果
- 📱 **响应式设计**: 支持桌面和移动设备

## 技术栈

### 后端
- **FastAPI**: 高性能Python Web框架
- **百度搜索API**: 获取搜索结果
- **DeepSeek API**: AI关键词生成
- **jieba**: 中文分词和关键词提取（降级方案）
- **httpx**: 异步HTTP客户端

### 前端
- **React**: 用户界面框架
- **TypeScript**: 类型安全的JavaScript
- **Tailwind CSS**: 实用优先的CSS框架
- **Lucide React**: 图标库

## 项目结构

```
Hackathon/
├── backend/                 # 后端代码
│   ├── __init__.py
│   ├── main.py             # FastAPI主应用
│   ├── search.py           # 百度搜索API
│   └── keywords.py         # 关键词生成
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # React组件
│   │   │   ├── SearchInterface.tsx
│   │   │   ├── SearchTree.tsx
│   │   │   └── SearchResultDetail.tsx
│   │   ├── types.ts        # TypeScript类型定义
│   │   ├── App.tsx         # 主应用组件
│   │   └── main.tsx        # 应用入口
│   ├── package.json
│   └── vite.config.ts
├── requirements.txt        # Python依赖
└── README.md
```

## 安装和运行

### 后端设置

1. 进入后端目录：
```bash
cd backend
```

2. 安装Python依赖：
```bash
pip install -r ../requirements.txt
```

3. 启动后端服务：
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端设置

1. 进入前端目录：
```bash
cd frontend
```

2. 安装Node.js依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

4. 在浏览器中访问：`http://localhost:5173`

## 使用说明

1. **搜索关键词**: 在搜索框中输入关键词，点击"开始搜索"
2. **查看结果**: 系统会显示搜索结果和生成的衍生关键词
3. **具体查看**: 点击"具体查看"按钮查看完整的搜索结果
4. **换一批**: 点击"换一批"按钮重新搜索相同关键词
5. **衍生搜索**: 点击衍生关键词继续搜索，形成搜索树
6. **清空历史**: 点击"清空"按钮清除所有搜索历史

## API接口

### 搜索接口
- **POST** `/search`
- 请求体：
```json
{
  "keyword": "搜索关键词",
  "max_results": 5,
  "generate_keywords_count": 5
}
```

### 健康检查
- **GET** `/health`
- 返回服务状态信息

## 配置说明

### API密钥配置
在 `backend/keywords.py` 中配置DeepSeek API密钥：
```python
DEEPSEEK_API_KEY = "your-api-key-here"
```

### 百度搜索配置
在 `backend/search.py` 中配置百度搜索API参数。

## 开发说明

### 添加新功能
1. 后端：在 `backend/` 目录下添加新的Python模块
2. 前端：在 `frontend/src/components/` 目录下添加新的React组件
3. 类型定义：在 `frontend/src/types.ts` 中定义新的TypeScript接口

### 错误处理
- 后端使用多层降级机制，确保服务的稳定性
- 前端提供友好的错误提示和加载状态

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请提交 Issue 或联系项目维护者。 