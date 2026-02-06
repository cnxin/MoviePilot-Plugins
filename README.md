# NotionMediaSync - MoviePilot Notion 媒体同步插件

媒体整理完成后自动将媒体信息同步到 Notion 数据库。

## 功能特性

- 监听 MoviePilot 的 `TransferComplete` 事件，媒体整理完成后自动同步
- 支持电影、剧集等多种媒体类型
- 自动获取 TMDB 媒体信息（标题、年份、评分、简介、封面等）
- 支持重复检测，避免重复录入
- 支持更新已存在的条目
- 兼容 Notion API 2025-09-03（data_sources API）
- 自动过滤数据库中不存在的字段

## 安装方法

在 MoviePilot 中添加插件仓库地址：

```
https://github.com/cnxin/MoviePilot-Plugins
```

然后在插件市场中搜索并安装 **Notion媒体同步** 插件。

## 配置说明

### 1. 创建 Notion Integration

1. 访问 [Notion Integrations](https://www.notion.so/my-integrations)
2. 点击 **New integration** 创建新的集成
3. 填写名称，选择关联的工作区
4. 创建后复制 **Internal Integration Token**

### 2. 创建 Notion 数据库

在 Notion 中创建一个数据库，建议包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 标题 | Title | 媒体标题（必需） |
| 原始标题 | Text | 原始语言标题 |
| 类型 | Select | 电影/剧集/动画/其他 |
| 年份 | Number | 发行年份 |
| 季数 | Number | 剧集季数 |
| 集数 | Text | 总集数 |
| 评分 | Number | TMDB 评分 |
| 封面 | Files | 海报图片 |
| 简介 | Text | 媒体简介 |
| 数据源 | Select | TMDB/Bangumi |

### 3. 连接数据库到 Integration

1. 打开 Notion 数据库页面
2. 点击右上角 **...** → **Add connections**
3. 选择你创建的 Integration

### 4. 获取数据库 ID

数据库 ID 可以从 URL 中获取：
```
https://www.notion.so/your-workspace/DATABASE_ID?v=xxx
```

或者从完整链接中提取 32 位字符的 ID。

### 5. 配置插件

在 MoviePilot 插件配置页面填入：
- **Notion Token**: Integration Token
- **数据库 ID**: Notion 数据库 ID
- **启用插件**: 开启

## 更新日志

### v1.0.1
- 修复 Notion API 2025-09-03 兼容性问题，支持 data_sources API
- 自动过滤数据库中不存在的字段
- 动态查找标题字段名称

### v1.0.0
- 首个版本，支持媒体整理完成后自动同步到 Notion

## 作者

cnxin

## 许可证

MIT License
