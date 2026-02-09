# NotionMediaSync - MoviePilot Notion 媒体同步插件

[![Version](https://img.shields.io/badge/version-2.3.0-blue.svg)](https://github.com/cnxin/MoviePilot-Plugins)
[![MoviePilot](https://img.shields.io/badge/MoviePilot-Plugin-green.svg)](https://github.com/jxxghp/MoviePilot)

媒体整理完成后自动录入 Notion 数据库，支持技术信息同步、动画独立分类和属性自动创建。

## 功能特性

### v2.3.0 新增功能

- **重复记录修复**: 使用线程锁+持久化存储，彻底解决多文件同步时创建重复记录的问题
- **集数修复**: 使用当前季的实际集数，而非全剧集总数
- **清空同步记录**: 新增 API 端点，支持清空同步去重记录

### v2.0.0 功能

- **技术信息同步**: 自动提取并同步分辨率、视频编码、音频格式、来源、发布组、季数、集数等技术信息
- **动画独立分类**: 根据 TMDB 类型自动识别动画，细分为「动画电影」和「动画剧集」
- **属性自动创建**: 插件初始化时自动检测并创建缺失的 Notion 数据库属性

### 基础功能

- 监听 MoviePilot 的 `TransferComplete` 事件，媒体整理完成后自动同步
- 支持电影、剧集等多种媒体类型
- 自动获取 TMDB 媒体信息（标题、年份、评分、简介、封面等）
- 支持重复检测，避免重复录入
- 同步历史记录查看和管理
- 同步完成通知推送

## 安装方法

在 MoviePilot 中添加插件仓库地址：

```
https://github.com/cnxin/MoviePilot-Plugins
```

然后在插件市场中搜索并安装 **Notion媒体同步** 插件。

## 快速开始

1. 在 Notion 创建 Integration 并获取 Token
2. 创建数据库并将 Integration 连接到数据库
3. 在 MoviePilot 插件设置中配置 Token 和数据库 ID
4. 启用插件，开始自动同步

详细配置请参考 [使用手册](./plugins.v2/notionmediasync/MANUAL.md)

## 数据库属性

### 必需属性

| 属性名 | 类型 | 说明 |
|--------|------|------|
| 标题 | title | 媒体标题 |

### 推荐属性

| 属性名 | 类型 | 说明 |
|--------|------|------|
| 原始标题 | rich_text | 原始语言标题 |
| 类型 | select | 电影/剧集/动画电影/动画剧集 |
| 年份 | number | 发行年份 |
| 评分 | number | TMDB 评分 |
| 封面 | files | 海报图片 |
| 简介 | rich_text | 媒体简介 |
| 数据源 | select | TMDB/Bangumi |

### 技术信息属性 (v2.0 新增，自动创建)

| 属性名 | 类型 | 说明 |
|--------|------|------|
| 分辨率 | select | 1080p/2160p/720p 等 |
| 视频编码 | rich_text | H265/x264/HEVC 等 |
| 音频格式 | rich_text | AAC/DTS/TrueHD 等 |
| 来源 | select | WEB-DL/BluRay/HDTV 等 |
| 发布组 | rich_text | 制作组/字幕组 |
| 季数 | number | 电视剧季数 |
| 集数 | rich_text | 集数信息 |

## 类型分类

插件会根据 TMDB 的 `genre_ids` 自动判断媒体类型：

| 条件 | 类型 |
|------|------|
| genre_ids 包含 16 (Animation) + 电影 | 动画电影 |
| genre_ids 包含 16 (Animation) + 电视剧 | 动画剧集 |
| 普通电影 | 电影 |
| 普通电视剧 | 剧集 |

## 更新日志

### v2.3.0

- 修复: 多文件同步时创建重复记录的问题（使用线程锁+持久化存储）
- 修复: 集数显示错误，使用当前季的实际集数
- 新增: 清空同步记录 API 端点 `/clear_synced_keys`

### v2.2.0

- 修复: 集数显示全剧集总数而非当前季集数的问题

### v2.1.0

- 新增: 持久化去重存储，防止重复同步

### v2.0.0

- 新增: 技术信息字段同步 (分辨率、编码、来源等)
- 新增: 动画独立分类 (动画电影/动画剧集)
- 新增: Notion 数据库属性自动创建
- 优化: 更新配置表单使用说明

### v1.0.1

- 修复: Notion API 2025-09-03 兼容性问题，支持 data_sources API
- 优化: 自动过滤数据库中不存在的字段
- 优化: 动态查找标题字段名称

### v1.0.0

- 初始版本
- 基础媒体信息同步
- 重复检测和跳过
- 同步历史记录

## 作者

cnxin

## 许可证

MIT License

## 致谢

- [MoviePilot](https://github.com/jxxghp/MoviePilot) - 媒体管理平台
- [notion-sdk-py](https://github.com/ramnes/notion-sdk-py) - Notion Python SDK
