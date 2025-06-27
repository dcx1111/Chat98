import React, { useState } from 'react'
import SearchInterface from './components/SearchInterface'
import SearchTree from './components/SearchTree'
import { SearchNode } from './types'

function App() {
  const [searchTree, setSearchTree] = useState<SearchNode[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = async (keyword: string) => {
    setIsLoading(true)
    try {
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          keyword,
          max_results: 5,
          generate_keywords_count: 5
        })
      })

      const data = await response.json()

      if (data.success) {
        const newNode: SearchNode = {
          id: Date.now().toString(),
          keyword,
          searchResults: data.search_results,
          generatedKeywords: data.generated_keywords,
          children: [],
          timestamp: new Date().toISOString(),
          isExpanded: false,
          hasSearched: true,
          isLoading: false
        }

        setSearchTree(prev => [...prev, newNode])
      } else {
        alert(`搜索失败: ${data.message}`)
      }
    } catch (error) {
      console.error('搜索请求失败:', error)
      alert('搜索请求失败，请检查网络连接')
    } finally {
      setIsLoading(false)
    }
  }

  const handleExpandNode = async (nodeId: string, keyword: string) => {
    setIsLoading(true)
    try {
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          keyword,
          max_results: 3,
          generate_keywords_count: 3
        })
      })

      const data = await response.json()
      
      if (data.success) {
        const childNode: SearchNode = {
          id: Date.now().toString(),
          keyword,
          searchResults: data.search_results,
          generatedKeywords: data.generated_keywords,
          children: [],
          timestamp: new Date().toISOString(),
          isExpanded: false,
          hasSearched: true,
          isLoading: false
        }
        
        setSearchTree(prev => {
          const updateNode = (nodes: SearchNode[]): SearchNode[] => {
            return nodes.map(node => {
              if (node.id === nodeId) {
                return { ...node, children: [...node.children, childNode] }
              }
              return { ...node, children: updateNode(node.children) }
            })
          }
          return updateNode(prev)
        })
      }
    } catch (error) {
      console.error('扩展节点失败:', error)
      alert('扩展节点失败，请重试')
    } finally {
      setIsLoading(false)
    }
  }

  const handleViewResults = (nodeId: string) => {
    setSearchTree(prev => {
      const updateNode = (nodes: SearchNode[]): SearchNode[] => {
        return nodes.map(node => {
          if (node.id === nodeId) {
            return { ...node, isExpanded: !node.isExpanded }
          }
          return { ...node, children: updateNode(node.children) }
        })
      }
      return updateNode(prev)
    })
  }

  const handleRefreshSearch = async (nodeId: string, keyword: string) => {
    // 设置节点为加载状态
    setSearchTree(prev => {
      const updateNode = (nodes: SearchNode[]): SearchNode[] => {
        return nodes.map(node => {
          if (node.id === nodeId) {
            return { ...node, isLoading: true }
          }
          return { ...node, children: updateNode(node.children) }
        })
      }
      return updateNode(prev)
    })

    try {
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          keyword,
          max_results: 5,
          generate_keywords_count: 5
        })
      })

      const data = await response.json()
      
      if (data.success) {
        setSearchTree(prev => {
          const updateNode = (nodes: SearchNode[]): SearchNode[] => {
            return nodes.map(node => {
              if (node.id === nodeId) {
                return { 
                  ...node, 
                  searchResults: data.search_results,
                  generatedKeywords: data.generated_keywords,
                  timestamp: new Date().toISOString(),
                  isLoading: false
                }
              }
              return { ...node, children: updateNode(node.children) }
            })
          }
          return updateNode(prev)
        })
      } else {
        alert(`重新搜索失败: ${data.message}`)
        // 重置加载状态
        setSearchTree(prev => {
          const updateNode = (nodes: SearchNode[]): SearchNode[] => {
            return nodes.map(node => {
              if (node.id === nodeId) {
                return { ...node, isLoading: false }
              }
              return { ...node, children: updateNode(node.children) }
            })
          }
          return updateNode(prev)
        })
      }
    } catch (error) {
      console.error('重新搜索失败:', error)
      alert('重新搜索失败，请重试')
      // 重置加载状态
      setSearchTree(prev => {
        const updateNode = (nodes: SearchNode[]): SearchNode[] => {
          return nodes.map(node => {
            if (node.id === nodeId) {
              return { ...node, isLoading: false }
            }
            return { ...node, children: updateNode(node.children) }
          })
        }
        return updateNode(prev)
      })
    }
  }

  const clearTree = () => {
    setSearchTree([])
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            智能搜索助手
          </h1>
          <p className="text-gray-600">
            基于AI的智能搜索和关键词衍生系统
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 搜索界面 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <SearchInterface 
              onSearch={handleSearch} 
              isLoading={isLoading}
            />
          </div>

          {/* 搜索结果展示 */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                搜索结果树
              </h2>
              {searchTree.length > 0 && (
                <button
                  onClick={clearTree}
                  className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                >
                  清空
                </button>
              )}
            </div>
            
            <SearchTree 
              nodes={searchTree} 
              onExpandNode={handleExpandNode}
              onViewResults={handleViewResults}
              onRefreshSearch={handleRefreshSearch}
              isLoading={isLoading}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App 