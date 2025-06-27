import requests
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import quote
from cc98_config import CC98_CONFIG

class CC98Search:
    def __init__(self):
        self.web_name = CC98_CONFIG["api_base_url"]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
        }
        # 这里需要配置CC98的认证信息
        self.access_token = None
        
    def refresh_auth(self):
        """刷新CC98认证"""
        login_url = CC98_CONFIG["auth_url"]
        payload = {
            "client_id": CC98_CONFIG["client_id"],
            "client_secret": CC98_CONFIG["client_secret"],
            "grant_type": "password",
            "username": CC98_CONFIG["username"],
            "password": CC98_CONFIG["password"],
            "scope": "cc98-api openid offline_access"
        }
        
        try:
            response = requests.post(login_url, data=payload)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                self.headers['Authorization'] = f"Bearer {self.access_token}"
                print("CC98认证刷新成功")
                return True
            else:
                print(f"CC98认证失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"CC98认证异常: {e}")
            return False

    def get_url_json(self, web_url: str, retry: int = 1) -> Any:
        """获取URL的JSON响应"""
        try:
            resp = requests.get(web_url, headers=self.headers)
            resp.encoding = 'utf-8'
            html = resp.text
            
            if html == "topic_not_exists":
                return "topic_not_exists"
            elif html == "topic_is_deleted":
                return "topic_is_deleted"
            elif html == "":
                return "empty_response"
            else:
                try:
                    return json.loads(html)
                except json.decoder.JSONDecodeError:
                    print("CC98 API认证错误")
                    if retry > 0 and self.refresh_auth():
                        return self.get_url_json(web_url, retry - 1)
                    else:
                        raise Exception(f"CC98 API请求失败: {web_url}")
        except Exception as e:
            print(f"CC98 API请求异常: {e}")
            return None

    def extract_topic(self, topic_info: Dict, main_post: Dict) -> Dict[str, Any]:
        """提取主题信息"""
        topic_save = ['id', 'boardId', 'title', 'time', 'userName', 'userId', 'isAnonymous', 'hitCount', 'bestState', 'favoriteCount']
        post_save = ['content', 'likeCount', 'dislikeCount', 'awards']
        
        topic_data = {}
        for key in topic_save:
            topic_data[key] = topic_info.get(key, '')
        for key in post_save:
            topic_data[key] = main_post.get(key, '')
            
        topic_data['awardsCount'] = len(topic_data.pop('awards', []))
        topic_data['bestState'] = topic_data['bestState'] == 1
        
        # 转换时间格式
        try:
            dt = datetime.fromisoformat(topic_data['time'].replace('Z', '+00:00'))
            topic_data['time'] = int(dt.timestamp())
        except:
            topic_data['time'] = 0
            
        return topic_data

    def spider_topic(self, topic_id: int) -> Optional[Dict[str, Any]]:
        """爬取单个主题"""
        topic_url = f"{self.web_name}/Topic/{topic_id}?sf_request_type=fetch"
        topic_info = self.get_url_json(topic_url)
        
        if isinstance(topic_info, str) or topic_info is None:
            return None
            
        reply_num = topic_info.get("replyCount", 0)
        for reply_page in range(0, reply_num // 10 + 1):
            url = f"{self.web_name}/Topic/{topic_id}/post?from={reply_page * 10}&size=10&sf_request_type=fetch"
            reply_list = self.get_url_json(url)
            
            if reply_list and len(reply_list) > 0:
                return self.extract_topic(topic_info, reply_list[0])
        
        return None

    async def search_cc98(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """CC98搜索主函数"""
        try:
            print(f"开始CC98搜索，关键词: {query}")
            
            # 检查认证配置
            if not CC98_CONFIG["username"] or not CC98_CONFIG["password"]:
                print("CC98认证信息未配置，无法进行CC98搜索")
                return []
            
            # 尝试认证
            if not self.access_token:
                print("CC98未认证，尝试刷新认证...")
                if not self.refresh_auth():
                    print("CC98认证失败，无法进行搜索")
                    return []
            
            # URL编码搜索词
            search_word = quote(query)
            search_url = f"{self.web_name}/topic/search?keyword={search_word}&size={count}&from=0"
            print(f"CC98搜索URL: {search_url}")
            
            resp = requests.get(search_url, headers=self.headers)
            resp.encoding = 'utf-8'
            
            if not resp.text:
                print("CC98搜索响应为空，尝试重新认证...")
                if self.refresh_auth():
                    resp = requests.get(search_url, headers=self.headers)
                else:
                    print("CC98重新认证失败")
                    return []

            if resp.status_code != 200:
                print(f"CC98搜索失败: {resp.status_code}")
                print(f"响应内容: {resp.text}")
                return []
                
            res_js = resp.json()
            print(f"CC98搜索返回 {len(res_js)} 个主题")
            topic_list = []
            
            for i in range(min(len(res_js), count)):
                print(f"处理第 {i+1} 个主题: {res_js[i]['id']}")
                topic = self.spider_topic(res_js[i]['id'])
                if topic:
                    # 转换为统一的搜索结果格式
                    result = {
                        "title": topic['title'],
                        "snippet": topic['content'][:200] + "..." if len(topic['content']) > 200 else topic['content'],
                        "url": f"https://www.cc98.org/topic/{topic['id']}",
                        "source": "cc98",
                        "author": topic['userName'],
                        "time": topic['time'],
                        "likeCount": topic['likeCount'],
                        "hitCount": topic['hitCount']
                    }
                    topic_list.append(result)
                    print(f"成功处理主题: {topic['title']}")
                else:
                    print(f"主题 {res_js[i]['id']} 处理失败")
            
            print(f"CC98搜索完成，共获取 {len(topic_list)} 个结果")
            return topic_list
            
        except Exception as e:
            print(f"CC98搜索异常: {e}")
            import traceback
            traceback.print_exc()
            return []

# 创建全局CC98搜索实例
cc98_searcher = CC98Search() 