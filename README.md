# IPTV-Source

收集、整理网络 IPTV 资源，生成自用 M3U 播放列表。

## 资源来源

- **IPTV 源**：[xisohi/CHINA-IPTV](https://github.com/xisohi/CHINA-IPTV)
- **EPG / 台标**：[fanmingming/live](https://github.com/fanmingming/live)
- **老张 EPG**：[http://epg.51zmt.top:8000/e.xml](http://epg.51zmt.top:8000/e.xml)（[网站](https://epg.51zmt.top:8001/)）

## 目录结构

```
├── sources/              # 收集的 IPTV 源（原始数据）
├── archive/              # 历史存档
│   ├── jiangsu-unicom-gitv/   # 江苏联通 GITV 源
│   └── jiangsu-mobile-mobai/  # 江苏移动 MOBAI 源
├── epg/                  # EPG 资源
├── logos/                # 台标资源
├── output/               # 生成的 M3U 文件
├── scripts/              # 生成脚本
└── RESOURCES.md          # 资源详细记录
```

## 工作流

1. 从网络收集 IPTV 源，放入 `sources/`
2. 运行 `scripts/` 中的脚本，替换台标、整理格式
3. 生成的 M3U 输出到 `output/`

## 历史存档

- 江苏联通 GITV 源 → `archive/jiangsu-unicom-gitv/`
- 江苏移动 MOBAI 源 → `archive/jiangsu-mobile-mobai/`
