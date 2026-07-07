# 江苏 IPTV 直播源

从 GITV EPG API 拉取江苏联通/移动/电信的 IPTV 直播源，生成 m3u8 播放列表。

## 使用

```bash
uv sync
uv run python generate_iptv.py
```

生成的文件：

| 文件 | 运营商 |
|------|--------|
| `js-cucc.m3u` | 联通 |
| `js-cmcc.m3u` | 移动 |
| `js-ctcc.m3u` | 电信 |

## 频道分组

CCTV / 江苏 / 南京 / 卫视 / 教育 / 其他

## 参考

- [lesca/jiangsu-iptv](https://github.com/lesca/jiangsu-iptv) — 原始参考脚本（仅联通）

## 资源收集

| 资源 | 说明 | 链接 |
|---|---|---|
| CHINA-IPTV | 国内 IPTV 直播源汇总 | [xisohi/CHINA-IPTV](https://github.com/xisohi/CHINA-IPTV) |
| fanmingming/live | EPG、台标、频道分类 | [fanmingming/live](https://github.com/fanmingming/live) |
| 老张 EPG | 电子节目单 XML 接口 | [epg.51zmt.top](https://epg.51zmt.top:8001/) |

## 目录结构

```
IPTV-Source/
├── docs/                   # 文档
│   └── resources.md        # 资源收集记录
├── sources/                # IPTV 源文件
│   ├── collected/          # 网络收集的 IPTV 源
│   └── archive/            # 历史存档
│       ├── jiangsu-unicom-gitv/
│       └── jiangsu-mobile-mobai/
├── generate_iptv.py        # IPTV 源生成脚本
└── README.md
```
