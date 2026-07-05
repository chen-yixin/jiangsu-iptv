# AGENTS

## 项目运行

```bash
uv sync
uv run python generate_iptv.py
```

输出文件：`js-cucc.m3u`、`js-ctcc.m3u`（`js-cmcc.m3u` 暂不可用，见下方说明）

---

## 当前项目状态

### 运营商支持

| 运营商 | ISP Code | 状态 | 数据源 |
|--------|----------|------|--------|
| 联通 | JS_CUCC | ✅ | gitv.tv API |
| 电信 | JS_CTCC | ✅ | gitv.tv API |
| 移动 | JS_CMCC | ❌ | gitv API playUrl 返回 405，待切换 mobaibox |

### 移动调研

详见 `MOBAIBOX_RESEARCH.md`。移动的替代源是 `ott.mobaibox.com`（江苏移动内网），需在移动网络下探测其 API。

---

## API 参考

### 1. CHANNEL_LIST_URL — 频道列表 + EPG

```
GET http://live.epg.gitv.tv/tagNewestEpgList/{isp}/1/100/0.json
```

**参数：** `{isp}` = `JS_CUCC` | `JS_CTCC` | `JS_CMCC`

**用途：** 获取频道列表、当前节目 EPG、流地址解析入口（playUrl）。这是主数据源，一次请求获取所有需要的信息。

**返回结构：**

```json
{
  "code": "A000000",
  "data": [
    {
      // ---- 频道标识 ----
      "chnName": "CCTV-1",          // 频道名（含质量后缀，需 normalize_channel_name）
      "chnAlias": "CCTV-1",         // 别名
      "chnCode": "G_CCTV-1-CQ",     // 频道编码（用于 tvg-id）
      "chnunCode": "cctv1",         // 统一频道编码（用于去重）
      "chnNum": 1,                  // 频道号
      "chnTypeId": 1,               // 频道类型：1=CCTV, 2=卫视/其他, 3=南京, 5=江苏本地
      "chnOrder": 27,               // 排序权重

      // ---- 清晰度 ----
      "chnDefinition": 200,         // 200=高清, 100=标清

      // ---- 流媒体 ----
      "playUrl": "http://...m3u8?p=GITV&area=JS_CUCC",    // 流地址解析入口（GET后返回JSON）
      "backPlayUrl": "http://...history.m3u8?...",        // 回看/时移地址
      "isShift": 1,                 // 是否支持时移

      // ---- EPG（当前节目） ----
      "title": "金石探文明",         // 当前节目名
      "startTime": 1783252860000,   // 节目开始时间（epoch 毫秒）
      "endTime": 1783260000000,     // 节目结束时间（epoch 毫秒）
      "tag": "综艺",                // 分类标签
      "tags": "综艺",               // 多标签（逗号分隔）
      "packageName": "金石探文明",   // 节目包名
      "packageCode": "6957...",     // 节目包编码
      "packageCover": "http://...", // 节目海报横版
      "packageCoverH": "http://...",// 节目海报竖版
      "epgStatus": 1,              // EPG状态：1=有效

      // ---- 状态/标志 ----
      "showLive": 1,               // 是否显示直播
      "playConfirm": 1,            // 是否需确认播放
      "isBroadcastChn": 0,         // 是否为广播频道
      "restrictLv": "",            // 内容分级限制
      "purchaseOwn": 0,            // 是否付费频道

      // ---- 台标/角标 ----
      "superscriptType": 1,         // 角标类型
      "superscriptPic": "http://...hd.png",  // 角标图片（如"高清"角标）

      // ---- 海报 ----
      "epgPoster": "http://...live.jpg",     // EPG海报
      "backPoster": "http://...images?",     // 回看海报

      // ---- 其他 ----
      "onlineCount": 0,            // 在线观看人数
      "defHis": 0,                 // 默认回看时长
      "tlReviewChn": 1,            // 是否支持回看
      "backJump": 1,               // 回看跳转
      "pOrder": 1680,              // 播放排序
      "fkOrder": 9999              // 备用排序
    }
  ]
}
```

**playUrl 解析（resolve_stream_url）：**

GET playUrl → 返回 JSON，从中提取真实流地址：

```json
// JS_CUCC / JS_CTCC 响应格式（data[0].url）：
{
  "code": "A000000",
  "data": [{
    "cdn": "fenghuo",
    "cid": "G_CCTV-1-CQ",
    "url": "http://122.96.52.98:8006/JS_CUCC/G_CCTV-1-CQ.m3u8?...",
    "isMulticast": 0,
    "playType": "live",
    "duration": 5000,
    "needAuth": 1
  }]
}

// 备选格式（u 字段）：
// { "u": "http://..." }
```

> **JS_CMCC 的 playUrl 使用 `live.dispatcher.gitv.tv` 域名，返回 405，无法解析。**
> JS_CUCC 用 `jscucc-livod.dispatcher.gitv.tv`，JS_CTCC 用 `jsctcc-livod.dispatcher.gitv.tv`。

---

### 2. CHANNEL_INFO_URL — 频道元信息 + 台标（备用）

```
GET http://live.epg.gitv.tv/chnInfos/{isp}/0.json
```

> **当前未使用。** 台标已改用 fanmingming/live 源（`LOGO_URL_TEMPLATE`）。
> 以下文档供后续需要时参考。

**返回结构（~183 个频道）：**

```json
{
  "code": "A000000",
  "all": 183,
  "num": 12,
  "data": [
    {
      // ---- 频道标识 ----
      "chnCode": "G_JSTY",          // 频道编码（与 CHANNEL_LIST_URL 的 chnCode 对应）
      "chnName": "江苏体育休闲",      // 频道名

      // ---- 清晰度 ----
      "chnDefinition": "100",        // "100"=标清, "200"=高清

      // ---- 台标/图标（多尺寸多用途）----
      "chnIcon": "http://live.pic.gitv.tv/...png",      // 主台标（小尺寸，width×height）
      "newIcon": "http://live.pic.gitv.tv/...png",      // "新"角标台标
      "bigChnIcon": "http://live.pic.gitv.tv/...png",   // 大尺寸台标（部分频道为空）
      "guideIcon": "http://live.pic.gitv.tv/...png",    // EPG节目导视中的台标（部分为null）
      "playIcon": "",                                    // 播放状态图标（通常为空）

      // ---- 台标尺寸（像素）----
      "width": 143,
      "height": 24,
      "bigIconWidth": null,
      "bigIconHeight": null,
      "guidWidth": null,                                // guideIcon 宽度
      "guideHeight": null,                              // guideIcon 高度
      "playIconWidth": null,
      "playIconHeight": null,

      // ---- 状态标志 ----
      "showLive": "1",               // 是否显示直播："1"=显示
      "chn_status": "1",            // 频道状态："1"=启用
      "nodeChn_status": "1",        // 节点频道状态
      "nuChnStatus": 1,             // 另一个状态字段（int类型）
      "forbidReplay": "1",          // 是否禁止回看："0"=允许, "1"=禁止

      // ---- 分类标签 ----
      "subTags": [                   // 子标签列表
        {"tagId": 0, "tagType": 0, "subTagId": 2}   // subTagId: 2=卫视, 3=本地
      ],
      "oSubTags": [],               // 另一套标签（通常为空）

      // ---- 关联频道 ----
      "chns": []                    // 关联频道列表（通常为空）
    }
  ]
}
```

**字段用途分析：**

| 类别 | 字段 | 当前使用 | 潜在用途 |
|------|------|:------:|----------|
| 标识 | `chnCode` | — | 可替代 tvg-id |
| 标识 | `chnName` | — | 备用频道名 |
| 台标 | `chnIcon` | 曾用作 tvg-logo | 备用台标源 |
| 台标 | `bigChnIcon` | — | 高清台标源 |
| 台标 | `guideIcon` | — | EPG 匹配用台标 |
| 清晰度 | `chnDefinition` | — | 标清/高清分类 |
| 状态 | `forbidReplay` | — | 标注是否支持回看 |
| 状态 | `showLive` / `chn_status` | — | 过滤已下线频道 |
| 分类 | `subTags[].subTagId` | — | 辅助频道分组 |

**与 CHANNEL_LIST_URL 的关联点：** 两个 API 通过 `chnCode` 关联。CHANNEL_LIST_URL 提供流地址和 EPG，CHANNEL_INFO_URL 提供台标和分类元数据。

**之前的使用方式（已移除）：**

```python
CHANNEL_INFO_URL = "http://live.epg.gitv.tv/chnInfos/{isp}/0.json"

def fetch_chninfos(isp):
    # GET CHANNEL_INFO_URL → 构建 {chnCode: chnIcon} 映射
    # process_isp 中通过 logo_map.get(ch.get("chnCode"), "") 获取台标
```

**为何移除：** 每个 ISP 需要额外一次 HTTP 请求获取台标，而 fanmingming/live 源可以直接从频道名拼出 URL，零额外请求且与移动 M3U 保持统一。

**何时恢复：** 如果 fanmingming 源不可用，或需要高清台标（`bigChnIcon`）、EPG 台标（`guideIcon`），或需要通过 `forbidReplay`/`chn_status` 过滤频道。

---

### 3. LOGO_URL_TEMPLATE — 当前台标源

```
https://ghproxy.cc/https://raw.githubusercontent.com/fanmingming/live/main/tv/{name}.png
```

`{name}` = `normalize_channel_name()` 的输出（如 `CCTV1`、`广东卫视`）。

与 `js-cmcc-2.m3u`（mobaibox 源）使用相同的台标来源。

---

## 频道名标准化规则

`normalize_channel_name()` 的转换：

| 规则 | 示例 |
|------|------|
| 去质量后缀 | `CCTV-1高清` → `CCTV-1`、`江苏卫视高清` → `江苏卫视`、`湖北卫视超清-8M` → `湖北卫视` |
| CCTV 去横杠 | `CCTV-1` → `CCTV1` |
| CETV 映射 | `CETV-1` → `中国教育1台` |
| 旧名兼容 | `海南卫视` → `旅游卫视` |

目标：与 EPG 源 `http://epg.51zmt.top:8000/e.xml` 的 `display-name` 对齐。
