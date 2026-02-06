"""Notion API 客户端

适配 MoviePilot 插件使用
支持 Notion API 2025-09-03 (data_sources API)
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
        self._db_properties: Optional[Dict] = None
        self._data_source_id: Optional[str] = None
        logger.info(f"Notion 客户端初始化完成，数据库 ID: {database_id[:8]}...")

    def _get_database_properties(self) -> Dict:
        """
        获取数据库的属性定义，用于验证字段是否存在
        支持 Notion API 2025-09-03 的 data_sources API
        """
        if self._db_properties is None:
            try:
                # 首先获取数据库信息
                db_info = self.client.databases.retrieve(database_id=self.database_id)

                # 尝试直接从 databases.retrieve 获取属性
                self._db_properties = db_info.get('properties', {})

                # 如果 properties 为空，尝试从 data_sources 获取
                if not self._db_properties and db_info.get('data_sources'):
                    self._data_source_id = db_info['data_sources'][0]['id']
                    logger.info(f"使用 data_source_id: {self._data_source_id[:8]}...")

                    if hasattr(self.client, 'data_sources'):
                        try:
                            ds_info = self.client.data_sources.retrieve(
                                data_source_id=self._data_source_id
                            )
                            self._db_properties = ds_info.get('properties', {})
                        except Exception as e:
                            logger.warning(f"data_sources.retrieve 失败: {str(e)}")

                # 打印数据库中的所有字段名和类型
                if self._db_properties:
                    logger.info(f"数据库字段列表 (共 {len(self._db_properties)} 个):")
                    for prop_name, prop_info in self._db_properties.items():
                        logger.debug(f"  - {prop_name}: {prop_info.get('type')}")
                else:
                    logger.warning("未能获取数据库字段，请检查 Integration 权限")

            except Exception as e:
                logger.error(f"获取数据库属性失败: {str(e)}")
                self._db_properties = {}

        return self._db_properties

    def _filter_properties(self, properties: Dict) -> Dict:
        """
        过滤掉数据库中不存在的属性
        """
        db_props = self._get_database_properties()
        filtered = {}
        for key, value in properties.items():
            if key in db_props:
                filtered[key] = value
            else:
                logger.warning(f"跳过不存在的属性: {key}")
        return filtered

    def create_page(self, properties: Dict) -> Optional[str]:
        """
        创建页面

        Args:
            properties: 页面属性字典

        Returns:
            页面 ID，失败返回 None
        """
        try:
            # 过滤掉不存在的属性
            filtered_props = self._filter_properties(properties)

            if not filtered_props:
                logger.error("没有有效的属性可以创建页面")
                return None

            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=filtered_props
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
            # 过滤掉不存在的属性
            filtered_props = self._filter_properties(properties)

            self.client.pages.update(
                page_id=page_id,
                properties=filtered_props
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
            # 确保已获取数据库属性（这会设置 _data_source_id）
            self._get_database_properties()

            # 优先使用 data_sources API (Notion API 2025-09-03)
            if self._data_source_id and hasattr(self.client, 'data_sources'):
                query_params = {"data_source_id": self._data_source_id}
                if filter_dict:
                    query_params["filter"] = filter_dict

                try:
                    response = self.client.data_sources.query(**query_params)
                    logger.info(f"Notion 数据库查询完成，找到 {len(response['results'])} 条记录")
                    return response['results']
                except Exception as e:
                    logger.warning(f"data_sources.query 失败: {str(e)}，尝试旧版 API")

            # 回退到旧版 databases API
            query_params = {"database_id": self.database_id}
            if filter_dict:
                query_params["filter"] = filter_dict

            if hasattr(self.client.databases, 'query'):
                response = self.client.databases.query(**query_params)
            else:
                # 如果没有 query 方法，返回空列表
                logger.warning("Notion API 不支持 databases.query")
                return []

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
            # 获取数据库属性，找到标题字段的名称
            db_props = self._get_database_properties()
            title_field = None

            # 查找 title 类型的字段
            for prop_name, prop_info in db_props.items():
                if prop_info.get('type') == 'title':
                    title_field = prop_name
                    break

            if not title_field:
                logger.warning("数据库中没有找到标题字段")
                return None

            filter_dict = {
                "property": title_field,
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
    def build_properties(media_data: Dict, db_properties: Optional[Dict] = None) -> Dict:
        """
        构建 Notion 属性字典

        Args:
            media_data: 媒体数据
            db_properties: 数据库属性定义（可选，用于验证）

        Returns:
            Notion 属性字典
        """
        properties = {}

        # 标题（必需）
        if media_data.get('title'):
            properties['标题'] = {
                'title': [{'text': {'content': media_data['title']}}]
            }

        # 原始标题
        if media_data.get('original_title'):
            properties['原始标题'] = {
                'rich_text': [{'text': {'content': media_data['original_title']}}]
            }

        # 类型
        media_type = media_data.get('media_type') or media_data.get('type')
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
        if media_data.get('year'):
            try:
                properties['年份'] = {'number': int(media_data['year'])}
            except (ValueError, TypeError):
                pass

        # 季数
        if media_data.get('season'):
            try:
                properties['季数'] = {'number': int(media_data['season'])}
            except (ValueError, TypeError):
                pass

        # 集数（总集数）- 支持 number 和 rich_text 两种类型
        episodes = media_data.get('total_episodes') or media_data.get('number_of_episodes')
        if episodes:
            # 转换为字符串以支持 rich_text 类型
            properties['集数'] = {
                'rich_text': [{'text': {'content': str(episodes)}}]
            }

        # 分辨率
        if media_data.get('resolution'):
            properties['分辨率'] = {'select': {'name': media_data['resolution']}}

        # 视频编码
        if media_data.get('video_codec'):
            properties['视频编码'] = {
                'rich_text': [{'text': {'content': media_data['video_codec']}}]
            }

        # 音频格式
        audio_info = media_data.get('audio_codec', '')
        if media_data.get('audio_channels'):
            audio_info += f" {media_data['audio_channels']}"
        if audio_info:
            properties['音频格式'] = {
                'rich_text': [{'text': {'content': audio_info}}]
            }

        # 来源（视频来源：BluRay/WEB-DL/HDTV）
        video_source = media_data.get('source')
        # 如果 source 是 API 数据源（tmdb/bangumi），则不作为视频来源
        if video_source and video_source not in ['tmdb', 'bangumi', 'TMDB', 'Bangumi']:
            properties['来源'] = {'select': {'name': video_source}}

        # 发布组
        if media_data.get('release_group'):
            properties['发布组'] = {
                'rich_text': [{'text': {'content': media_data['release_group']}}]
            }

        # 评分
        if media_data.get('rating') or media_data.get('vote_average'):
            rating = media_data.get('rating') or media_data.get('vote_average')
            try:
                properties['评分'] = {'number': float(rating)}
            except (ValueError, TypeError):
                pass

        # 封面URL
        poster = media_data.get('poster_path') or media_data.get('cover_url') or media_data.get('poster')
        if poster:
            # 如果是相对路径，补全 TMDB 图片地址
            if poster.startswith('/'):
                poster = f"https://image.tmdb.org/t/p/w500{poster}"
            properties['封面'] = {
                'files': [{'name': '封面', 'external': {'url': poster}}]
            }

        # 简介
        summary = media_data.get('overview') or media_data.get('summary')
        if summary:
            # Notion 富文本有长度限制，截断到 2000 字符
            if len(summary) > 2000:
                summary = summary[:1997] + '...'
            properties['简介'] = {
                'rich_text': [{'text': {'content': summary}}]
            }

        # 数据源（使用 api_source 字段，避免与视频来源冲突）
        api_source = media_data.get('api_source') or media_data.get('source')
        if api_source:
            source_mapping = {
                'tmdb': 'TMDB',
                'bangumi': 'Bangumi',
                'TMDB': 'TMDB',
                'Bangumi': 'Bangumi'
            }
            source_name = source_mapping.get(api_source)
            if source_name:
                properties['数据源'] = {'select': {'name': source_name}}

        return properties
