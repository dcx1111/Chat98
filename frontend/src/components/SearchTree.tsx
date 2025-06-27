import React, { useState } from 'react'
import { ChevronRight, ExternalLink, Clock, Tag, Search, Eye, RefreshCw, Globe, MessageSquare } from 'lucide-react'
import { SearchNode } from '../types'
import SearchResultDetail from './SearchResultDetail'

interface SearchTreeProps {
  nodes: SearchNode[]
  onExpandNode: (nodeId: string, keyword: string) => void
  onViewResults: (nodeId: string) => void
  onRefreshSearch: (nodeId: string, keyword: string) => void
  isLoading: boolean
  onCollectItem: (item: any) => void
}

const SearchTree: React.FC<SearchTreeProps> = ({ nodes, onExpandNode, onViewResults, onRefreshSearch, isLoading, onCollectItem }) => {
  const [detailNode, setDetailNode] = useState<SearchNode | null>(null)

  // 将树状结构转换为层级结构
  const buildLevels = (nodes: SearchNode[]): Array<{level: number, items: Array<{node: SearchNode, parentId?: string, keyword: string}>}> => {
    const levels: Array<{level: number, items: Array<{node: SearchNode, parentId?: string, keyword: string}>}> = []
    
    const processNode = (node: SearchNode, level: number, parentId?: string) => {
      // 添加主节点到当前层级
      if (!levels[level]) {
        levels[level] = { level, items: [] }
      }
      levels[level].items.push({ node, parentId, keyword: node.keyword })
      
      // 处理子节点
      node.children.forEach(child => {
        processNode(child, level + 1, node.id)
      })
    }
    
    nodes.forEach(node => processNode(node, 0))
    return levels
  }

  const levels = buildLevels(nodes)

  const handleViewResults = (node: SearchNode) => {
    if (node.isExpanded) {
      // 如果已经展开，则收起
      onViewResults(node.id)
    } else {
      // 如果未展开，则显示详情弹窗
      setDetailNode(node)
    }
  }

  const renderLevel = (level: {level: number, items: Array<{node: SearchNode, parentId?: string, keyword: string}>}) => {
    return (
      <div key={level.level} className="mb-6">
        <div className="flex items-center mb-3">
          <div className="text-sm font-medium text-gray-700 bg-gray-100 px-3 py-1 rounded-full">
            第 {level.level + 1} 层
          </div>
          <div className="ml-2 text-xs text-gray-500">
            {level.items.length} 个关键词
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {level.items.map((item, index) => (
            <div key={`${item.node.id}-${index}`} className="relative">
              {/* 连接线 */}
              {item.parentId && (
                <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 w-px h-2 bg-gray-300"></div>
              )}
              
              {/* 关键词节点 */}
              <div className="bg-white rounded-lg border-2 border-blue-200 p-4 shadow-sm hover:shadow-md transition-shadow">
                {/* 关键词标题 */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-gray-900 truncate">
                      {item.keyword}
                    </h3>
                    <div className="flex items-center mt-1">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        item.node.searchSource === 'baidu' 
                          ? 'bg-blue-100 text-blue-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {item.node.searchSource === 'baidu' ? (
                          <>
                            <Globe className="w-3 h-3 mr-1" />
                            百度搜索
                          </>
                        ) : (
                          <>
                            <MessageSquare className="w-3 h-3 mr-1" />
                            CC98论坛
                          </>
                        )}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center text-xs text-gray-500">
                    <Clock className="w-3 h-3 mr-1" />
                    {new Date(item.node.timestamp).toLocaleTimeString()}
                  </div>
                </div>

                {/* 搜索结果预览 */}
                {item.node.searchResults.length > 0 && (
                  <div className="mb-3">
                    <div className="flex items-center text-xs font-medium text-gray-700 mb-2">
                      <Search className="w-3 h-3 mr-1" />
                      搜索结果 ({item.node.searchResults.length})
                    </div>
                    <div className="space-y-1">
                      {item.node.searchResults.slice(0, 2).map((result, resultIndex) => (
                        <div key={resultIndex} className="bg-gray-50 rounded p-2">
                          <div className="flex items-start justify-between">
                            <div className="flex-1 min-w-0">
                              <h4 className="font-medium text-gray-900 text-xs mb-1 truncate">
                                {result.title}
                              </h4>
                              <p className="text-gray-600 text-xs line-clamp-2">
                                {result.snippet}
                              </p>
                            </div>
                            <a
                              href={result.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="ml-2 text-blue-600 hover:text-blue-700 flex-shrink-0"
                            >
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 操作按钮 */}
                <div className="flex items-center justify-between mb-3">
                  {/* 具体查看按钮 */}
                  {item.node.hasSearched && item.node.searchResults.length > 0 && (
                    <button
                      onClick={() => handleViewResults(item.node)}
                      className="flex items-center px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs hover:bg-blue-200 transition-colors"
                    >
                      <Eye className="w-3 h-3 mr-1" />
                      具体查看
                    </button>
                  )}
                  
                  {/* 换一批按钮 */}
                  <button
                    onClick={() => onRefreshSearch(item.node.id, item.keyword)}
                    disabled={item.node.isLoading || isLoading}
                    className="flex items-center px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs hover:bg-green-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <RefreshCw className={`w-3 h-3 mr-1 ${item.node.isLoading ? 'animate-spin' : ''}`} />
                    换一批
                  </button>
                </div>

                {/* 衍生关键词 */}
                {item.node.generatedKeywords.length > 0 && (
                  <div>
                    <div className="flex items-center text-xs font-medium text-gray-700 mb-2">
                      <Tag className="w-3 h-3 mr-1" />
                      衍生关键词
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {item.node.generatedKeywords.map((keyword, keywordIndex) => (
                        <button
                          key={keywordIndex}
                          onClick={() => onExpandNode(item.node.id, keyword)}
                          disabled={isLoading}
                          className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs hover:bg-green-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          title={`点击搜索: ${keyword}`}
                        >
                          {keyword}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* 展开指示器 */}
                {item.node.children.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-gray-100">
                    <div className="flex items-center text-xs text-gray-500">
                      <ChevronRight className="w-3 h-3 mr-1" />
                      已展开 {item.node.children.length} 个子节点
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (nodes.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>暂无搜索结果</p>
        <p className="text-sm mt-1">输入关键词开始搜索</p>
      </div>
    )
  }

  return (
    <>
      <div className="space-y-6">
        {levels.map(level => renderLevel(level))}
      </div>

      {/* 搜索结果详情弹窗 */}
      {detailNode && (
        <SearchResultDetail
          results={detailNode.searchResults}
          keyword={detailNode.keyword}
          nodeId={detailNode.id}
          onClose={() => setDetailNode(null)}
          onCollectItem={onCollectItem}
        />
      )}
    </>
  )
}

export default SearchTree 