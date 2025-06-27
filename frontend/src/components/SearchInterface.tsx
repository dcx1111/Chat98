import React, { useState } from 'react'
import { Search, Loader2 } from 'lucide-react'

interface SearchInterfaceProps {
  onSearch: (keyword: string) => void
  isLoading: boolean
}

const SearchInterface: React.FC<SearchInterfaceProps> = ({ onSearch, isLoading }) => {
  const [keyword, setKeyword] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (keyword.trim() && !isLoading) {
      onSearch(keyword.trim())
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          搜索关键词
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="输入搜索关键词..."
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

        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-medium text-blue-900 mb-2">使用说明</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• 输入关键词进行智能搜索</li>
            <li>• 系统会自动生成相关关键词</li>
            <li>• 点击衍生关键词继续搜索</li>
            <li>• 点击"具体查看"查看完整搜索结果</li>
            <li>• 点击"换一批"重新搜索相同关键词</li>
            <li>• 每层显示上一层的衍生结果</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default SearchInterface 