import React, { useState } from 'react'
import { Search, Loader2, Bookmark, Layers, Globe, MessageSquare } from 'lucide-react'
import { CollectedItem, SearchSource } from '../types'

interface SearchInterfaceProps {
  onSearch: (keyword: string, searchSource: SearchSource) => void
  isLoading: boolean
  collectedItems: CollectedItem[]
  onIntegrateCollections: () => void
  integrationLoading: boolean
  integrationResult: string
}

const SearchInterface: React.FC<SearchInterfaceProps> = ({ 
  onSearch, 
  isLoading, 
  collectedItems,
  onIntegrateCollections,
  integrationLoading,
  integrationResult
}) => {
  const [keyword, setKeyword] = useState('')
  const [searchSource, setSearchSource] = useState<SearchSource>('baidu')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (keyword.trim() && !isLoading) {
      onSearch(keyword.trim(), searchSource)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          搜索关键词
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 搜索源选择 */}
          <div className="flex space-x-2">
            <button
              type="button"
              onClick={() => setSearchSource('baidu')}
              className={`flex-1 flex items-center justify-center px-4 py-2 rounded-lg border-2 transition-colors ${
                searchSource === 'baidu'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-300 bg-white text-gray-600 hover:border-gray-400'
              }`}
            >
              <Globe className="w-4 h-4 mr-2" />
              百度搜索
            </button>
            <button
              type="button"
              onClick={() => setSearchSource('cc98')}
              className={`flex-1 flex items-center justify-center px-4 py-2 rounded-lg border-2 transition-colors ${
                searchSource === 'cc98'
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : 'border-gray-300 bg-white text-gray-600 hover:border-gray-400'
              }`}
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              CC98论坛
            </button>
          </div>

          <div className="relative">
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder={`在${searchSource === 'baidu' ? '百度' : 'CC98'}中搜索...`}
              className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all text-gray-900 bg-white"
              disabled={isLoading}
            />
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          </div>

          <button
            type="submit"
            disabled={!keyword.trim() || isLoading}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>搜索中...</span>
              </>
            ) : (
              <>
                <Search className="w-5 h-5" />
                <span>开始搜索</span>
              </>
            )}
          </button>
        </form>

        {/* 收藏集合区域 */}
        <div className="mt-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center">
              <Bookmark className="w-5 h-5 text-yellow-600 mr-2" />
              <h3 className="font-medium text-yellow-900">收藏集合</h3>
              <span className="ml-2 text-sm text-yellow-700 bg-yellow-100 px-2 py-1 rounded-full">
                {collectedItems.length} 项
              </span>
            </div>
            <button
              onClick={onIntegrateCollections}
              disabled={collectedItems.length === 0 || integrationLoading}
              className="flex items-center px-3 py-1 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
            >
              {integrationLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                  集合中...
                </>
              ) : (
                <>
                  <Layers className="w-4 h-4 mr-1" />
                  集合
                </>
              )}
            </button>
          </div>

          {/* 收藏项目预览 */}
          {collectedItems.length > 0 && (
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {collectedItems.slice(0, 3).map((item) => (
                <div key={item.id} className="bg-white rounded p-2 border border-yellow-100">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-gray-900 truncate">
                        {item.title}
                      </p>
                      <p className="text-xs text-gray-500">
                        来自: {item.nodeKeyword}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
              {collectedItems.length > 3 && (
                <p className="text-xs text-yellow-600 text-center">
                  还有 {collectedItems.length - 3} 项收藏...
                </p>
              )}
            </div>
          )}

          {/* 集合结果显示 */}
          {integrationResult && (
            <div className="mt-3 bg-white rounded-lg p-3 border border-yellow-100">
              <div className="flex items-center mb-2">
                <Layers className="w-4 h-4 text-yellow-600 mr-2" />
                <span className="text-sm font-medium text-yellow-800">集合结果</span>
              </div>
              <div className="bg-gray-50 rounded p-2">
                <p className="text-xs text-gray-800 leading-relaxed whitespace-pre-line">
                  {integrationResult}
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-medium text-blue-900 mb-2">使用说明</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• 选择搜索源：百度搜索或CC98论坛</li>
            <li>• 输入关键词进行智能搜索</li>
            <li>• 系统会自动生成相关关键词</li>
            <li>• 点击衍生关键词继续搜索</li>
            <li>• 点击"具体查看"查看完整搜索结果</li>
            <li>• 在搜索结果中点击"收藏"按钮收藏内容</li>
            <li>• 点击"集合"按钮整合所有收藏内容</li>
            <li>• 点击"换一批"重新搜索相同关键词</li>
            <li>• 每层显示上一层的衍生结果</li>
            <li>• <span className="font-medium">注意：CC98搜索需要配置认证信息</span></li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default SearchInterface 