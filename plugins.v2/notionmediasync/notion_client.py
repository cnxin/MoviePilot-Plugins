"""Notion API 客户端

适配 MoviePilot 插件使用
"""

from typing import Dict, List, Optional

from notion_client import Client

from app.log import logger


class NotionClient:
    """Notion API 客户端封装"""

    def __init__(self, token: str, database_id: str):
        """
        初始化 Notion 客户端

        Args:
            token: Notion Integration Token
            database_id: Notion 数据库 ID
        """
        self.client = Client(auth=token)
        self.database_id = database_id
        logger.info(f"Notion 客户端初始化完成，数据库 ID: {database_id[:8]}...")

    def create_page(self, properties: Dict) -> Optional[str]:
        """
        创建页面

        Args:
            properties: 页面属性字典

        Returns:
            页面 ID，失败返回 None
        """
        try:
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )

            page_id = response['id']
            logger.info(f"Notion 页面创建成功: {page_id}")
            return page_id

        except Exception as e:
            logger.error(f"创建 Notion 页面失败: {str(e)}")
            return None

    def update_page(self, page_id: str, properties: Dict) -> bool:
        """
        更新页面

        Args:
            page_id: 页面 ID
            properties: 要更新的属性

        Returns:
            True 如果成功，否则 False
        """
        try:
            self.client.pages.update(
                page_id=page_id,
                properties=properties
            )

            logger.info(f"Notion 页面更新成功: {page_id}")
            return True

        except Exception as e:
            logger.error(f"更新 Notion 页面失败: {page_id}, 错误: {str(e)}")
            return False

    def query_database(self, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        查询数据库

        Args:
            filter_dict: 过滤条件（可选）

        Returns:
            结果列表
        """
        try:
            query_params = {"database_id": self.database_id}

            if filter_dict:
                query_params["filter"] = filter_dict

            response = self.client.databases.query(**query_params)

            logger.info(f"Notion 数据库查询完成，找到 {len(response['results'])} 条记录")
            return response['results']

        except Exception as e:
            logger.error(f"查询 Notion 数据库失败: {str(e)}")
            return []

    def check_duplicate(self, title: str) -> Optional[str]:
        """
        检查是否存在重复条目

        Args:
            title: 标题

        Returns:
            如果存在，返回页面 ID，否则返回 None
        """
        try:
            filter_dict = {
                "property": "标题",
                "title": {
                    "equals": title
                }
            }

            results = self.query_database(filter_dict)

            if results:
                page_id = results[0]['id']
                logger.info(f"找到重复条目: {title}, ID: {page_id}")
                return page_id

            return None

        except Exception as e:
            logger.error(f"检查重复条目失败: {title}, 错误: {str(e)}")
            return None

    @staticmethod
    def build_properties(media_data: Dict) -> Dict:
        """
        构建 Notion 属性字典

        Args:
            media_data: 媒体数据

        Returns:
            Notion 属性字典
        """
        properties = {}

        # 标题（必需）
        title = media_data.get('title') or media_data.get('name', '')
        if title:
            properties['标题'] = {
                'title': [{'text': {'content': title}}]
            }

        # 原始标题
        original_title = media_data.get('original_title') or media_data.get('original_name', '')
        if original_title:
            properties['原始标题'] = {
                'rich_text': [{'text': {'content': original_title}}]
            }

        # 类型
        media_type = media_data.get('media_type') or media_data.get('type', '')
        if media_type:
            type_mapping = {
                'movie': '电影',
                'tv': '剧集',
                'tv_series': '剧集',
                'anime': '动画',
                '电影': '电影',
                '电视剧': '剧集'
            }
            type_name = type_mapping.get(str(media_type).lower(), '其他')
            properties['类型'] = {'select': {'name': type_name}}

        # 年份
        year = media_data.get('year') or media_data.get('first_air_date', '')[:4] if media_data.get('first_air_date') else None
        if year:
            try:
                properties['年份'] = {'number': int(year)}
            except (ValueError, TypeError):
                pass

        # 季数
        season = media_data.get('season') or media_data.get('season_number')
        if season:
            try:
                properties['季数'] = {'number': int(season)}
            except (ValueError, TypeError):
                pass

        # 集数
        episodes = media_data.get('total_episodes') or media_data.get('number_of_episodes')
        if episodes:
            properties['集数'] = {
                'rich_text': [{'text': {'content': str(episodes)}}]
            }

        # 评分
        rating = media_data.get('vote_average') or media_data.get('rating')
        if rating:
            try:
                properties['评分'] = {'number': float(rating)}
            except (ValueError, TypeError):
                pass

        # 封面URL
        poster = media_data.get('poster_path') or media_data.get('poster') or media_data.get('cover_url')
        if poster:
            # 如果是相对路径，补全 TMDB 图片地址
            if poster.startswith('/'):
                poster = f"https://image.tmdb.org/t/p/w500{poster}"
            properties['封面'] = {
                'files': [{'name': '封面', 'external': {'url': poster}}]
            }

        # 简介
        overview = media_data.get('overview') or media_data.get('summary', '')
        if overview:
            # Notion 富文本有长度限制，截断到 2000 字符
            if len(overview) > 2000:
                overview = overview[:1997] + '...'
            properties['简介'] = {
                'rich_text': [{'text': {'content': overview}}]
            }

        # TMDB ID
        tmdb_id = media_data.get('tmdb_id') or media_data.get('id')
        if tmdb_id:
            properties['TMDB ID'] = {
                'rich_text': [{'text': {'content': str(tmdb_id)}}]
            }

        # 数据源
        source = media_data.get('source', 'TMDB')
        if source:
            properties['数据源'] = {'select': {'name': source}}

        return properties
