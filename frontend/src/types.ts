export interface SearchResult {
  title: string
  snippet: string
  url: string
}

export interface SearchNode {
  id: string
  keyword: string
  searchResults: SearchResult[]
  generatedKeywords: string[]
  children: SearchNode[]
  timestamp: string
  isExpanded: boolean
  hasSearched: boolean
  isLoading: boolean
  searchSource: string
}

export interface SearchRequest {
  keyword: string
  max_results: number
  generate_keywords_count: number
  search_source: string
}

export interface SearchResponse {
  original_keyword: string
  search_results: SearchResult[]
  generated_keywords: string[]
  success: boolean
  message: string
}

export interface TreeIntegrationRequest {
  nodes: Array<{
    keyword: string
    results: SearchResult[]
  }>
  main_keyword: string
}

export interface CollectedItem {
  id: string
  nodeId: string
  nodeKeyword: string
  title: string
  content: string
  url: string
  timestamp: string
}

export type SearchSource = 'baidu' | 'cc98' 