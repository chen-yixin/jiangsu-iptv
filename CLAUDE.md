# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

本仓库用于存储和管理 IPTV 相关资源：收集网络上的 IPTV 源、EPG 数据、台标，并基于这些资源生成自用的 M3U 播放列表。历史提交记录已作废，不做参考。

## 资源来源

| 类型 | 来源 |
|------|------|
| IPTV 源 | <https://github.com/xisohi/CHINA-IPTV> |
| EPG / 台标 | <https://github.com/fanmingming/live> |
| 老张 EPG | XML: `http://epg.51zmt.top:8000/e.xml`，网站: <https://epg.51zmt.top:8001/> |

## 目录结构约定

```
.
├── sources/              # 从网络收集的 IPTV 源（原始数据）
│   ├── china-iptv/       #   来自 xisohi/CHINA-IPTV
│   └── ...               #   其他收集到的源
├── archive/              # 历史存档的 IPTV 源
│   ├── jiangsu-unicom-gitv/   # 江苏联通 GITV 源
│   └── jiangsu-mobile-mobai/  # 江苏移动 MOBAI 源
├── epg/                  # EPG 相关资源（来自 fanmingming/live）
├── logos/                # 台标资源（来自 fanmingming/live）
├── output/               # 生成的输出文件（M3U 等）
└── scripts/              # 生成脚本（Python）
```

## 工作流

1. **收集**：将网络 IPTV 源保存到 `sources/` 目录
2. **存档**：历史源放入 `archive/` 保留
3. **处理**：运行 `scripts/` 中的 Python 脚本，以收集到的源为基础，替换台标等内容
4. **输出**：生成自用的 M3U 播放列表到 `output/`

## 技术栈

- **Python**：用于 IPTV 源解析、M3U 生成、台标替换等数据处理脚本
- **M3U**：播放列表格式，UTF-8 编码
