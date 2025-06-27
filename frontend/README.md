# 智能搜索助手前端

基于React + TypeScript + Tailwind CSS构建的现代化搜索界面。

## 功能特性

- 🎯 智能关键词搜索
- 🌳 节点树形式展示搜索结果
- 🔄 关键词自动衍生
- 📱 响应式设计
- ⚡ 实时交互

## 技术栈

- React 18
- TypeScript
- Tailwind CSS
- Vite
- Lucide React (图标)

## 开发环境

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

前端将在 http://localhost:3000 启动

### 构建生产版本

```bash
npm run build
```

## 项目结构

```
src/
├── components/          # React组件
│   ├── SearchInterface.tsx  # 搜索界面
│   └── SearchTree.tsx       # 搜索结果树
├── types.ts            # TypeScript类型定义
├── App.tsx             # 主应用组件
├── main.tsx            # 应用入口
└── index.css           # 全局样式
```

## 与后端集成

前端通过代理配置连接到后端API：

- 开发环境：`/api/*` -> `http://localhost:8000/*`
- 确保后端服务在8000端口运行

## 使用说明

1. 在搜索框中输入关键词
2. 点击"开始搜索"按钮
3. 查看搜索结果和生成的相关关键词
4. 点击相关关键词继续衍生搜索
5. 在树状结构中查看完整的搜索历史 