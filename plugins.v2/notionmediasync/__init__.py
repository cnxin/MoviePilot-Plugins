"""Notion 媒体同步插件

媒体整理完成后自动录入 Notion 数据库
"""

import datetime
from typing import Any, List, Dict, Tuple, Optional

from app import schemas
from app.core.config import settings
from app.core.event import eventmanager, Event
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import EventType

from .notion_client import NotionClient


class NotionMediaSync(_PluginBase):
    # 插件名称
    plugin_name = "Notion媒体同步"
    # 插件描述
    plugin_desc = "媒体整理完成后自动录入Notion数据库。"
    # 插件图标
    plugin_icon = "https://www.notion.so/images/favicon.ico"
    # 插件版本
    plugin_version = "1.0.0"
    # 插件作者
    plugin_author = "media-library-manager"
    # 作者主页
    author_url = "https://github.com/jxxghp/MoviePilot-Plugins"
    # 插件配置项ID前缀
    plugin_config_prefix = "notionmediasync_"
    # 加载顺序
    plugin_order = 30
    # 可使用的用户级别
    auth_level = 1

    # 私有变量
    _notion_client: Optional[NotionClient] = None

    # 配置属性
    _enabled: bool = False
    _notify: bool = False
    _notion_token: str = ""
    _database_id: str = ""
    _skip_existing: bool = True
    _media_types: List[str] = []

    def init_plugin(self, config: dict = None):
        """
        初始化插件
        """
        if config:
            self._enabled = config.get("enabled", False)
            self._notify = config.get("notify", False)
            self._notion_token = config.get("notion_token", "")
            self._database_id = config.get("database_id", "")
            self._skip_existing = config.get("skip_existing", True)
            self._media_types = config.get("media_types", [])

        # 初始化 Notion 客户端
        if self._enabled and self._notion_token and self._database_id:
            try:
                self._notion_client = NotionClient(
                    token=self._notion_token,
                    database_id=self._database_id
                )
                logger.info("Notion媒体同步插件初始化成功")
            except Exception as e:
                logger.error(f"Notion客户端初始化失败: {str(e)}")
                self._notion_client = None

    def get_state(self) -> bool:
        """
        获取插件状态
        """
        return self._enabled and self._notion_client is not None

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """
        定义远程控制命令
        """
        return [{
            "cmd": "/notion_sync",
            "event": EventType.PluginAction,
            "desc": "手动同步到Notion",
            "category": "工具",
            "data": {
                "action": "notion_sync"
            }
        }]

    def get_api(self) -> List[Dict[str, Any]]:
        """
        获取插件API
        """
        return [
            {
                "path": "/delete_history",
                "endpoint": self.delete_history,
                "methods": ["GET"],
                "summary": "删除Notion同步历史记录"
            },
            {
                "path": "/test_connection",
                "endpoint": self.test_connection,
                "methods": ["GET"],
                "summary": "测试Notion连接"
            }
        ]

    def get_service(self) -> List[Dict[str, Any]]:
        """
        注册插件公共服务
        """
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面
        """
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'notify',
                                            'label': '发送通知',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 4
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'skip_existing',
                                            'label': '跳过已存在',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'notion_token',
                                            'label': 'Notion Integration Token',
                                            'placeholder': 'secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                                            'type': 'password'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'database_id',
                                            'label': 'Notion 数据库 ID',
                                            'placeholder': '32位数据库ID，从数据库链接中获取'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VSelect',
                                        'props': {
                                            'model': 'media_types',
                                            'label': '媒体类型过滤',
                                            'multiple': True,
                                            'chips': True,
                                            'items': [
                                                {'title': '电影', 'value': 'movie'},
                                                {'title': '电视剧', 'value': 'tv'},
                                            ],
                                            'placeholder': '留空则同步所有类型'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'text': '使用说明：\n'
                                                    '1. 在 Notion 创建 Integration 并获取 Token\n'
                                                    '2. 将 Integration 连接到目标数据库\n'
                                                    '3. 数据库需包含以下属性：标题(title)、原始标题(rich_text)、'
                                                    '类型(select)、年份(number)、评分(number)、封面(files)、简介(rich_text)、'
                                                    'TMDB ID(rich_text)、数据源(select)\n'
                                                    '4. 可选属性：季数(number)、集数(rich_text)'
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": False,
            "notify": True,
            "notion_token": "",
            "database_id": "",
            "skip_existing": True,
            "media_types": []
        }

    def get_page(self) -> List[dict]:
        """
        拼装插件详情页面
        """
        # 查询同步历史
        historys = self.get_data('history')
        if not historys:
            return [
                {
                    'component': 'div',
                    'text': '暂无同步记录',
                    'props': {
                        'class': 'text-center',
                    }
                }
            ]

        # 数据按时间降序排序
        historys = sorted(historys, key=lambda x: x.get('time', ''), reverse=True)

        # 拼装页面
        contents = []
        for history in historys:
            title = history.get("title", "未知")
            poster = history.get("poster", "")
            mtype = history.get("type", "未知")
            time_str = history.get("time", "")
            status = history.get("status", "unknown")
            page_id = history.get("page_id", "")

            status_text = {
                "success": "成功",
                "skipped": "跳过",
                "failed": "失败"
            }.get(status, status)

            status_color = {
                "success": "success",
                "skipped": "warning",
                "failed": "error"
            }.get(status, "default")

            contents.append(
                {
                    'component': 'VCard',
                    'content': [
                        {
                            "component": "VDialogCloseBtn",
                            "props": {
                                'innerClass': 'absolute top-0 right-0',
                            },
                            'events': {
                                'click': {
                                    'api': 'plugin/NotionMediaSync/delete_history',
                                    'method': 'get',
                                    'params': {
                                        'page_id': page_id or title,
                                        'apikey': settings.API_TOKEN
                                    }
                                }
                            },
                        },
                        {
                            'component': 'div',
                            'props': {
                                'class': 'd-flex justify-space-start flex-nowrap flex-row',
                            },
                            'content': [
                                {
                                    'component': 'div',
                                    'content': [
                                        {
                                            'component': 'VImg',
                                            'props': {
                                                'src': poster,
                                                'height': 120,
                                                'width': 80,
                                                'aspect-ratio': '2/3',
                                                'class': 'object-cover shadow ring-gray-500',
                                                'cover': True
                                            }
                                        }
                                    ]
                                },
                                {
                                    'component': 'div',
                                    'content': [
                                        {
                                            'component': 'VCardTitle',
                                            'props': {
                                                'class': 'ps-1 pe-5 break-words whitespace-break-spaces'
                                            },
                                            'text': title
                                        },
                                        {
                                            'component': 'VCardText',
                                            'props': {
                                                'class': 'pa-0 px-2'
                                            },
                                            'text': f'类型：{mtype}'
                                        },
                                        {
                                            'component': 'VCardText',
                                            'props': {
                                                'class': 'pa-0 px-2'
                                            },
                                            'text': f'时间：{time_str}'
                                        },
                                        {
                                            'component': 'VChip',
                                            'props': {
                                                'color': status_color,
                                                'size': 'small',
                                                'class': 'ms-2 mt-1'
                                            },
                                            'text': status_text
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            )

        return [
            {
                'component': 'div',
                'props': {
                    'class': 'grid gap-3 grid-info-card',
                },
                'content': contents
            }
        ]

    def delete_history(self, page_id: str, apikey: str):
        """
        删除同步历史记录
        """
        if apikey != settings.API_TOKEN:
            return schemas.Response(success=False, message="API密钥错误")

        historys = self.get_data('history')
        if not historys:
            return schemas.Response(success=False, message="未找到历史记录")

        # 删除指定记录
        historys = [h for h in historys if h.get("page_id") != page_id and h.get("title") != page_id]
        self.save_data('history', historys)
        return schemas.Response(success=True, message="删除成功")

    def test_connection(self, apikey: str):
        """
        测试 Notion 连接
        """
        if apikey != settings.API_TOKEN:
            return schemas.Response(success=False, message="API密钥错误")

        if not self._notion_client:
            return schemas.Response(success=False, message="Notion客户端未初始化")

        try:
            # 尝试查询数据库
            results = self._notion_client.query_database()
            return schemas.Response(success=True, message=f"连接成功，数据库中有 {len(results)} 条记录")
        except Exception as e:
            return schemas.Response(success=False, message=f"连接失败: {str(e)}")

    def stop_service(self):
        """
        退出插件
        """
        pass

    @eventmanager.register(EventType.TransferComplete)
    def on_transfer_complete(self, event: Event):
        """
        整理完成后触发
        """
        if not self._enabled or not self._notion_client:
            return

        event_data = event.event_data
        if not event_data:
            return

        # 获取媒体信息
        mediainfo = event_data.get("mediainfo")
        transferinfo = event_data.get("transferinfo")

        if not mediainfo:
            logger.warning("TransferComplete 事件缺少 mediainfo")
            return

        # 媒体类型过滤
        media_type = str(mediainfo.type.value).lower() if hasattr(mediainfo, 'type') else ''
        if self._media_types and media_type not in self._media_types:
            logger.info(f"跳过媒体类型 {media_type}: {mediainfo.title}")
            return

        # 构建媒体数据
        media_data = self._build_media_data(mediainfo, transferinfo)
        title = media_data.get('title', '未知')

        logger.info(f"开始同步到 Notion: {title}")

        # 检查重复
        if self._skip_existing:
            existing = self._notion_client.check_duplicate(title)
            if existing:
                logger.info(f"跳过已存在条目: {title}")
                self._save_history(media_data, None, "skipped")
                return

        # 构建 Notion 属性
        properties = NotionClient.build_properties(media_data)

        # 创建 Notion 页面
        page_id = self._notion_client.create_page(properties)

        if page_id:
            logger.info(f"Notion 同步成功: {title} -> {page_id}")
            self._save_history(media_data, page_id, "success")

            # 发送通知
            if self._notify:
                self.post_message(
                    mtype=None,
                    title="Notion媒体同步",
                    text=f"已同步: {title}",
                    image=media_data.get('poster')
                )
        else:
            logger.error(f"Notion 同步失败: {title}")
            self._save_history(media_data, None, "failed")

    @eventmanager.register(EventType.PluginAction)
    def on_plugin_action(self, event: Event):
        """
        响应远程命令
        """
        if not event:
            return

        event_data = event.event_data
        if not event_data or event_data.get("action") != "notion_sync":
            return

        logger.info("收到 Notion 同步命令")
        self.post_message(
            channel=event_data.get("channel"),
            title="Notion媒体同步",
            text="手动同步功能暂未实现，请等待媒体整理完成后自动同步",
            userid=event_data.get("user")
        )

    def _build_media_data(self, mediainfo, transferinfo) -> Dict:
        """
        从 MoviePilot 媒体信息构建数据字典
        """
        data = {}

        if mediainfo:
            data['title'] = mediainfo.title
            data['original_title'] = getattr(mediainfo, 'original_title', '')
            data['year'] = mediainfo.year
            data['type'] = mediainfo.type.value if hasattr(mediainfo, 'type') else ''
            data['media_type'] = data['type']
            data['tmdb_id'] = mediainfo.tmdb_id
            data['vote_average'] = getattr(mediainfo, 'vote_average', None)
            data['overview'] = getattr(mediainfo, 'overview', '')
            data['poster'] = mediainfo.get_poster_image() if hasattr(mediainfo, 'get_poster_image') else ''
            data['number_of_episodes'] = getattr(mediainfo, 'number_of_episodes', None)
            data['number_of_seasons'] = getattr(mediainfo, 'number_of_seasons', None)
            data['source'] = 'TMDB'

        if transferinfo:
            # 可以从 transferinfo 获取更多信息
            pass

        return data

    def _save_history(self, media_data: Dict, page_id: Optional[str], status: str):
        """
        保存同步历史
        """
        history: List[dict] = self.get_data('history') or []

        history.append({
            "title": media_data.get('title', '未知'),
            "type": media_data.get('type', ''),
            "year": media_data.get('year', ''),
            "poster": media_data.get('poster', ''),
            "tmdb_id": media_data.get('tmdb_id', ''),
            "page_id": page_id or '',
            "status": status,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # 只保留最近 100 条记录
        if len(history) > 100:
            history = history[-100:]

        self.save_data('history', history)
