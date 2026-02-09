# Notion 媒体同步插件

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/jxxghp/MoviePilot-Plugins)
[![MoviePilot](https://img.shields.io/badge/MoviePilot-Plugin-green.svg)](https://github.com/jxxghp/MoviePilot)

媒体整理完成后自动录入 Notion 数据库，支持技术信息同步、动画独立分类和属性自动创建。

## 功能特性

### v2.0.0 新增功能

- **技术信息同步**: 自动提取并同步分辨率、视频编码、音频格式、来源、发布组、季数、集数等技术信息
- **动画独立分类**: 根据 TMDB 类型自动识别动画，细分为「动画电影」和「动画剧集」
- **属性自动创建**: 插件初始化时自动检测并创建缺失的 Notion 数据库属性

### 基础功能

- 媒体整理完成后自动同步到 Notion 数据库
- 支持电影和电视剧类型过滤
- 支持跳过已存在条目（去重）
- 同步历史记录查看和管理
- 同步完成通知推送

## 安装要求

- MoviePilot v2.x
- Python 依赖: `notion-client`

## 快速开始

1. 在 Notion 创建 Integration 并获取 Token
2. 创建数据库并将 Integration 连接到数据库
3. 在 MoviePilot 插件设置中配置 Token 和数据库 ID
4. 启用插件，开始自动同步

详细配置请参考 [使用手册](./MANUAL.md)

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

### v2.0.0

- 新增: 技术信息字段同步 (分辨率、编码、来源等)
- 新增: 动画独立分类 (动画电影/动画剧集)
- 新增: Notion 数据库属性自动创建
- 优化: 更新配置表单使用说明

### v1.0.0

- 初始版本
- 基础媒体信息同步
- 重复检测和跳过
- 同步历史记录

## 许可证

MIT License

## 致谢

- [MoviePilot](https://github.com/jxxghp/MoviePilot) - 媒体管理平台
- [notion-sdk-py](https://github.com/ramnes/notion-sdk-py) - Notion Python SDK
