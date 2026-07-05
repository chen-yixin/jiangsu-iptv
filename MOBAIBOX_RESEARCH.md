# mobaibox.com API 调研任务

## 背景

本项目 `generate_iptv.py` 通过 gitv.tv 的 API 自动生成江苏 IPTV M3U 播放列表。

### 当前支持的运营商

| 运营商 | ISP Code | 状态 |
|--------|----------|------|
| 联通 | JS_CUCC | ✅ 正常 |
| 电信 | JS_CTCC | ✅ 正常 |
| 移动 | JS_CMCC | ❌ gitv API 的 playUrl 返回 405，流不可用 |

### 移动的替代源

移动有一个可用的 M3U 文件来自 **`ott.mobaibox.com`**（第三方 OTT 平台）：
- 文件：`js-cmcc-2.m3u`
- 格式：`http://ott.mobaibox.com/PLTV/3/224/{数字ID}/index.m3u8`
- 频道数：106 个（央视频道 37 + 卫视频道 35 + NEWTV 19 + 江苏地方 10 + 少儿 5）
- 频道 ID 范围：`3221225923` ~ `3221228689`

## 任务目标

探测 `ott.mobaibox.com` 是否有类似 gitv.tv `CHANNEL_LIST_URL` 的频道列表 API，实现移动 M3U 的**自动化生成**（替代手动维护 M3U 文件）。

## 当前已知信息

### gitv.tv API（联通/电信在用）

```python
# 频道列表（含当前节目 EPG、playUrl）
CHANNEL_LIST_URL = "http://live.epg.gitv.tv/tagNewestEpgList/{isp}/1/100/0.json"
# 频道信息（台标等）
CHANNEL_INFO_URL = "http://live.epg.gitv.tv/chnInfos/{isp}/0.json"
```

### mobaibox URL 模式

```
http://ott.mobaibox.com/PLTV/3/224/{channel_id}/index.m3u8
```

- `PLTV` — OTT 平台标识
- `3` — 服务器/平台 ID
- `224` — 区域码（可能对应江苏移动）
- `channel_id` — 数字频道 ID（如 `3221227467`）

### mobaibox 已知额外频道

搜索发现 js-cmcc-2.m3u 中**未收录**但 mobaibox 上存在的频道：

| 频道 | Channel ID |
|------|-----------|
| 奥林匹克4K（CCTV-16 4K） | 3221228127 |
| 金鹰纪实 | 3221228110 |
| 劲爆体育 | 3221227023 |

这说明 M3U 是手动整理的，**不是**从 API 自动生成的，可能存在更多未收录频道。

## 待执行探测（需在江苏移动网络下运行）

### 1. 基础连通性验证

```bash
# 确认能访问 mobaibox.com
curl -sL --max-time 10 -o /dev/null -w "HTTP:%{http_code}\n" http://ott.mobaibox.com/
```

### 2. 常见 IPTV API 路径探测

华为/中兴 OTT 平台常见的频道列表接口路径：

```bash
# EPG 相关
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/EPG/jsp/getChannelList.jsp"
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/epg/api/channel"
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/epg/getChannelList"
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/epg/getEpgList"

# Portal/API 相关
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/api/getChannelList"
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/api/getChannels"
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/api/channels"
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/api/iptv"
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/portal/jsp/getChannelList.jsp"

# IPTV 标准接口
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/iptv/jsp/getChannelList.jsp"
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/iptv/getChannelList"

# JSON 接口
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/json/channelList.json"
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/channelList.json"
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/channels.json"

# PLTV 目录列举
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/PLTV/"
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/PLTV/3/"
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/PLTV/3/224/"
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/PLTV/3/224/playlist.m3u8"
curl -sL --max-time 10 -w "\n→ HTTP:%{http_code}\n" "http://ott.mobaibox.com/PLTV/3/224/playlist.m3u"
```

### 3. 相邻 ID 探测

验证是否能通过遍历 ID 发现新频道：

```bash
# 测试已知间隙和边界附近的 ID
for id in \
    3221225920 3221225921 3221225922 \
    3221227018 3221227023 3221227028 \
    3221227467 3221227468 3221227469 \
    3221228110 3221228127 \
    3221228433 3221228435 3221228436 \
    3221228686 3221228689 3221228690 3221228691 \
    3221229000; do
    STATUS=$(curl -sL --max-time 8 -o /dev/null -w '%{http_code}' \
        "http://ott.mobaibox.com/PLTV/3/224/$id/index.m3u8")
    SIZE=$(curl -sL --max-time 8 -o /dev/null -w '%{size_download}' \
        "http://ott.mobaibox.com/PLTV/3/224/$id/index.m3u8")
    if [ "$STATUS" != "000" ] && [ "$SIZE" -gt 100 ]; then
        echo "✅ ID $id: HTTP $STATUS, ${SIZE} bytes — 有效频道"
    else
        echo "❌ ID $id: HTTP $STATUS"
    fi
done
```

### 4. 如果以上都失败 — 全量扫描

如果没有任何 API 返回频道列表，考虑对已知 ID 范围进行全量扫描：

```bash
# 扫描 3221225000 ~ 3221230000 范围（约5000个ID）
# 注意：适当限速避免被封
for id in $(seq 3221225000 3221230000); do
    STATUS=$(curl -sL --max-time 5 -o /dev/null -w '%{http_code}' \
        "http://ott.mobaibox.com/PLTV/3/224/$id/index.m3u8")
    if [ "$STATUS" = "200" ]; then
        echo "$id"
    fi
    sleep 0.05  # 限速，每秒约20个请求
done > discovered_ids.txt
```

## 集成方案（找到 API 后）

### 情况 A：找到频道列表 API

参考现有 `generate_iptv.py` 模式，新增 mobaibox 数据源：

```python
# 新增 ISP 配置
ISP_CONFIGS = [
    ("JS_CUCC", "联通", "js-cucc.m3u"),     # gitv API
    ("JS_CTCC", "电信", "js-ctcc.m3u"),     # gitv API
    ("JS_CMCC", "移动", "js-cmcc.m3u"),     # mobaibox API（新）
]

# 新增 mobaibox 的 URL 常量
MOBAIBOX_CHANNEL_LIST_URL = "http://ott.mobaibox.com/..."  # 待填入
MOBAIBOX_STREAM_URL_TEMPLATE = "http://ott.mobaibox.com/PLTV/3/224/{channel_id}/index.m3u8"
```

### 情况 B：只能通过 ID 扫描

定期扫描 ID 范围，发现有效频道后生成 M3U（自动化程度较低但可用）。

### 情况 C：完全无 API

只能手动维护 M3U 文件，类似当前的 `js-cmcc-2.m3u`。

## 项目文件结构

```
generate_iptv.py       # 主生成脚本
js-cucc.m3u            # 联通 M3U（自动生成）
js-ctcc.m3u            # 电信 M3U（自动生成）
js-cmcc-2.m3u          # 移动 M3U（手动维护，来自 mobaibox）
js-cmcc.m3u            # （待产出）移动 M3U 自动生成
MOBAIBOX_RESEARCH.md   # 本文档
```

## 相关代码关键函数

`generate_iptv.py` 中的核心流程（作为参考）：

1. `fetch_epg(isp)` — 请求 CHANNEL_LIST_URL，获取频道列表 + 当前节目
2. `fetch_chninfos(isp)` — 请求 CHANNEL_INFO_URL，获取台标
3. `resolve_stream_url(channel)` — GET playUrl → 解析 JSON → 提取真实流地址
4. `normalize_channel_name(chn_name)` — 频道名对齐 EPG display-name
5. `process_isp(code, name, output)` — 主流程：获取数据 → 去重 → 解析流 → 写 M3U

---

> 🤖 此文档由 Claude Code 生成，供江苏移动网络环境下的 Agent 继续调研。
> 项目仓库：`D:\github.com\chen-yixin\jiangsu-iptv`
