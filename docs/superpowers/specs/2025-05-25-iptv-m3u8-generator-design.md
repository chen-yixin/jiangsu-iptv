# IPTV m3u8 生成器设计

## 概述

从 GITV EPG API 拉取江苏省三大运营商（联通、移动、电信）的 IPTV 直播源，为每个运营商生成独立的 m3u8 播放列表文件，包含完整的节目信息。

## 文件结构

```
pyproject.toml          # uv 项目配置，仅依赖 requests
generate_iptv.py        # 单脚本，所有逻辑集中在一个文件中
iptv_js_unicom.m3u      # 输出：联通 (JS_CUCC)
iptv_js_mobile.m3u      # 输出：移动 (JS_CMCC)
iptv_js_telecom.m3u     # 输出：电信 (JS_CTCC)
```

## 依赖

- `requests` — HTTP 客户端
- 通过 `uv` 管理（pyproject.toml）

## API 端点

| 运营商 | API 地址 | 输出文件 |
|--------|---------|----------|
| 联通 | `http://live.epg.gitv.tv/tagNewestEpgList/JS_CUCC/1/100/0.json` | `iptv_js_unicom.m3u` |
| 移动 | `http://live.epg.gitv.tv/tagNewestEpgList/JS_CMCC/1/100/0.json` | `iptv_js_mobile.m3u` |
| 电信 | `http://live.epg.gitv.tv/tagNewestEpgList/JS_CTCC/1/100/0.json` | `iptv_js_telecom.m3u` |

## 脚本流程

对每个运营商依次执行：

1. **拉取 EPG 数据**：GET 请求 tagNewestEpgList JSON 接口
2. **解析频道列表**：从 `response['data']` 中提取所有频道条目
3. **去重画质变体**：对每个唯一的 `chnunCode`，仅保留 `chnDefinition` 值最高的条目
4. **解析真实流地址**：并发请求每个频道的 `playUrl`，从响应的 JSON 字段 `u` 中提取真实流媒体地址
5. **频道分组**：根据 `chnName` 关键词匹配分配分组
6. **生成 m3u8**：生成 `#EXTM3U` 头 + 每个频道的 `#EXTINF` 行
7. **写入文件**：保存到对应运营商的输出文件

## 频道分组

按 `chnName` 关键词匹配（按优先级顺序检查，首次命中即确定分组）：

| 优先级 | 分组 | 匹配关键词 |
|--------|------|-----------|
| 1 | CCTV | `CCTV`、`CGTN` |
| 2 | 南京 | `南京` |
| 3 | 江苏 | `江苏` |
| 4 | 卫视 | `卫视` |
| 5 | 教育 | `CETV`、`教育` |
| 6 | 其他 | 兜底 |

相比参考脚本移除的分组：少儿（少儿频道合并到"其他"分组）。

## m3u8 格式

```
#EXTM3U
#EXTINF:-1 group-title="CCTV" tvg-name="CCTV-1" tvg-chno="1",CCTV-1 今日说法(第20250525期)
http://解析后的真实流地址/playlist.m3u8?...
```

- `group-title`：关键词匹配分配的分组名
- `tvg-name`：清洗后的频道名（去除 `高清`、`超清`、`-8M`、`-` 后缀）
- `tvg-chno`：频道的逻辑频道号（来自 `chnNum` 字段）
- 显示名（逗号后）：`{chnName} {title}`，同时展示频道名和当前节目名
- 时长：`-1`（直播流，时长未知）
- 流地址：从二级 playUrl 请求解析出的真实播放地址

## 并发处理

使用 `concurrent.futures.ThreadPoolExecutor`，15 个工作线程并发解析所有频道的真实流地址。预计 70~120 个频道在 5~10 秒内完成解析，而不是逐条请求的 60 秒以上。

## 画质去重

JS_CUCC 会返回同一频道不同画质的重复条目（SD/HD/4K），这些条目的 `chnNum` 为 null。对于每个唯一的 `chnunCode`，仅保留 `chnDefinition` 值最高的条目。JS_CMCC 和 JS_CTCC 极少或没有重复条目，因此此逻辑主要影响 JS_CUCC。

## 错误处理

- 网络错误：打印警告，跳过失败频道，继续处理
- 无效 JSON 响应：打印错误，跳过该运营商
- 缺少预期字段：使用空字符串 / `None` 回退
