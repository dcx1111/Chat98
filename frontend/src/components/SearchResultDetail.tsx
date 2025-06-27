import React, { useState } from 'react'
import { ExternalLink, X, FileText, Loader2, Bookmark, BookmarkPlus } from 'lucide-react'
import { SearchResult, CollectedItem } from '../types'

interface SearchResultDetailProps {
  results: SearchResult[]
  keyword: string
  nodeId: string
  onClose: () => void
  onCollectItem: (item: CollectedItem) => void
}

interface SummaryState {
  [key: number]: {
    summary: string
    loading: boolean
    error: string
  }
}

interface CollectionState {
  [key: number]: boolean
}

const SearchResultDetail: React.FC<SearchResultDetailProps> = ({ 
  results, 
  keyword, 
  nodeId,
  onClose, 
  onCollectItem 
}) => {
  const [summaries, setSummaries] = useState<SummaryState>({})
  const [collections, setCollections] = useState<CollectionState>({})

  const generateSummary = async (index: number, content: string) => {
    // 如果已经有概括了，直接返回
    if (summaries[index]?.summary) {
      return
    }

    // 设置加载状态
    setSummaries(prev => ({
      ...prev,
      [index]: { summary: '', loading: true, error: '' }
    }))

    try {
      const response = await fetch('http://localhost:8000/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: content,
          max_length: 150
        })
      })

      const data = await response.json()

      if (data.success) {
        setSummaries(prev => ({
          ...prev,
          [index]: { summary: data.summary, loading: false, error: '' }
        }))
      } else {
        setSummaries(prev => ({
          ...prev,
          [index]: { summary: '', loading: false, error: data.message }
        }))
      }
    } catch (error) {
      setSummaries(prev => ({
        ...prev,
        [index]: { summary: '', loading: false, error: '网络错误，请稍后重试' }
      }))
    }
  }

  const toggleCollection = (index: number, result: SearchResult) => {
    const isCollected = collections[index]
    
    if (isCollected) {
      // 取消收藏
      setCollections(prev => ({
        ...prev,
        [index]: false
      }))
    } else {
      // 添加收藏
      const collectedItem: CollectedItem = {
        id: `${nodeId}-${index}`,
        nodeId: nodeId,
        nodeKeyword: keyword,
        title: result.title,
        content: result.snippet,
        url: result.url,
        timestamp: new Date().toISOString()
      }
      
      onCollectItem(collectedItem)
      setCollections(prev => ({
        ...prev,
        [index]: true
      }))
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
        {/* 头部 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            搜索结果详情 - "{keyword}"
          </h2>
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        {/* 内容 */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {results.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>暂无搜索结果</p>
            </div>
          ) : (
            <div className="space-y-4">
              {results.map((result, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 mb-2 line-clamp-2">
                        {result.title}
                      </h3>
                      <p className="text-gray-600 text-sm leading-relaxed">
                        {result.snippet}
                      </p>
                      
                      {/* 概括区域 */}
                      <div className="mt-3">
                        {summaries[index]?.summary && (
                          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-2">
                            <div className="flex items-center mb-1">
                              <FileText className="w-4 h-4 text-blue-600 mr-2" />
                              <span className="text-sm font-medium text-blue-800">内容概括</span>
                            </div>
                            <p className="text-sm text-blue-700 leading-relaxed">
                              {summaries[index].summary}
                            </p>
                          </div>
                        )}
                        
                        {summaries[index]?.error && (
                          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-2">
                            <p className="text-sm text-red-600">
                              概括失败: {summaries[index].error}
                            </p>
                          </div>
                        )}
                        
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => generateSummary(index, `${result.title} ${result.snippet}`)}
                            disabled={summaries[index]?.loading}
                            className="inline-flex items-center px-3 py-1 text-xs bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          >
                            {summaries[index]?.loading ? (
                              <>
                                <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                                概括中...
                              </>
                            ) : (
                              <>
                                <FileText className="w-3 h-3 mr-1" />
                                概括
                              </>
                            )}
                          </button>
                          
                          {/* 收藏按钮 */}
                          <button
                            onClick={() => toggleCollection(index, result)}
                            className={`inline-flex items-center px-3 py-1 text-xs rounded-md transition-colors ${
                              collections[index]
                                ? 'bg-yellow-600 text-white hover:bg-yellow-700'
                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                            }`}
                          >
                            {collections[index] ? (
                              <>
                                <BookmarkPlus className="w-3 h-3 mr-1" />
                                已收藏
                              </>
                            ) : (
                              <>
                                <Bookmark className="w-3 h-3 mr-1" />
                                收藏
                              </>
                            )}
                          </button>
                        </div>
                      </div>
                      
                      <div className="mt-2 text-xs text-gray-500">
                        结果 #{index + 1}
                      </div>
                    </div>
                    
                    <a
                      href={result.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-4 p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-full transition-colors flex-shrink-0"
                      title="在新标签页中打开"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 底部 */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">
              共找到 {results.length} 个搜索结果
            </span>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SearchResultDetail 