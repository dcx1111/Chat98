import React from 'react'
import { ExternalLink, X } from 'lucide-react'
import { SearchResult } from '../types'

interface SearchResultDetailProps {
  results: SearchResult[]
  keyword: string
  onClose: () => void
}

const SearchResultDetail: React.FC<SearchResultDetailProps> = ({ results, keyword, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
        {/* 头部 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            搜索结果详情 - "{keyword}"
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
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