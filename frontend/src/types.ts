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
}

export interface SearchRequest {
  keyword: string
  max_results: number
  generate_keywords_count: number
}

export interface SearchResponse {
  original_keyword: string
  search_results: SearchResult[]
  generated_keywords: string[]
  success: boolean
  message: string
} 