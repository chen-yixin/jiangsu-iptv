# IPTV m3u8 生成器 实现计划

> **给执行者：** 推荐使用 superpowers:subagent-driven-development 或 superpowers:executing-plans 按任务逐步执行。步骤使用 checkbox (`- [ ]`) 语法跟踪进度。

**目标：** 从 GITV EPG API 拉取江苏联通/移动/电信的 IPTV 直播源，为每个运营商生成包含完整节目信息的 m3u8 播放列表。

**架构：** 单脚本 `generate_iptv.py`，使用 `concurrent.futures` 并发解析流地址。通过 `uv` 管理依赖。

**技术栈：** Python 3, requests, concurrent.futures.ThreadPoolExecutor

---

### 文件清单

| 文件 | 操作 | 职责 |
|------|------|------|
| `pyproject.toml` | 创建 | uv 项目配置，仅 requests 依赖 |
| `generate_iptv.py` | 创建 | 全部逻辑：拉取、解析、去重、并发、分组、输出 |

---

### Task 1: 初始化 uv 项目

**文件：**
- 创建: `pyproject.toml`
- 创建: `generate_iptv.py`（空壳，含 shebang 和入口点）

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[project]
name = "jiangsu-iptv"
version = "1.0.0"
description = "江苏IPTV直播源m3u8生成器"
requires-python = ">=3.10"
dependencies = [
    "requests>=2.31",
]

[tool.uv]
dev-dependencies = []
```

- [ ] **Step 2: 创建 generate_iptv.py 骨架**

```python
#!/usr/bin/env python3
"""江苏IPTV直播源m3u8生成器"""

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def main():
    pass


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 初始化 uv 并安装依赖**

```powershell
uv sync
```

预期：安装 `requests` 并创建 `.venv/` 目录。

- [ ] **Step 4: 验证脚本可以被 uv run 执行**

```powershell
uv run python generate_iptv.py
```

预期：无报错退出（main 为空）。

- [ ] **Step 5: 提交**

```powershell
git add pyproject.toml generate_iptv.py
git commit -m "Init uv project with basic script skeleton"
```

---

### Task 2: 实现频道分组与 m3u8 格式化函数

**文件：**
- 修改: `generate_iptv.py`（添加 `get_group()` 和 `format_channel()` 函数）

- [ ] **Step 1: 添加频道分组函数**

在 `main()` 上方添加：

```python
def get_group(chn_name: str) -> str:
    if any(k in chn_name for k in ["CCTV", "CGTN"]):
        return "CCTV"
    if "南京" in chn_name:
        return "南京"
    if "江苏" in chn_name:
        return "江苏"
    if "卫视" in chn_name:
        return "卫视"
    if any(k in chn_name for k in ["CETV", "教育"]):
        return "教育"
    return "其他"


def clean_tvg_name(chn_name: str) -> str:
    return re.sub(r"高清|超清|-8M|-", "", chn_name).strip()
```

- [ ] **Step 2: 添加 m3u8 行格式化函数**

```python
def format_extinf(channel: dict, real_url: str) -> str:
    chn_name = channel.get("chnName", "")
    group = get_group(chn_name)
    tvg_name = clean_tvg_name(chn_name)
    chn_num = channel.get("chnNum") or ""
    title = channel.get("title", "")

    display_name = chn_name
    if title:
        display_name = f"{chn_name} {title}"

    extinf = (
        f'#EXTINF:-1 group-title="{group}"'
        f' tvg-name="{tvg_name}"'
        f' tvg-chno="{chn_num}",'
        f'{display_name}'
    )
    return extinf
```

- [ ] **Step 3: 提交**

```powershell
git add generate_iptv.py
git commit -m "Add channel grouping and m3u8 formatting functions"
```

---

### Task 3: 实现 EPG 数据拉取与画质去重

**文件：**
- 修改: `generate_iptv.py`（添加 `fetch_epg()` 和 `dedup_channels()` 函数）

- [ ] **Step 1: 定义 ISP 配置**

在 `main()` 上方添加：

```python
ISP_CONFIGS = [
    ("JS_CUCC", "联通", "iptv_js_unicom.m3u"),
    ("JS_CMCC", "移动", "iptv_js_mobile.m3u"),
    ("JS_CTCC", "电信", "iptv_js_telecom.m3u"),
]

API_URL_TEMPLATE = "http://live.epg.gitv.tv/tagNewestEpgList/{isp}/1/100/0.json"
```

- [ ] **Step 2: 添加 EPG 数据拉取函数**

```python
def fetch_epg(isp: str) -> dict | None:
    url = API_URL_TEMPLATE.format(isp=isp)
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == "A000000":
            return data
        print(f"[{isp}] API返回异常: code={data.get('code')}, message={data.get('message')}")
        return None
    except requests.RequestException as e:
        print(f"[{isp}] 网络请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"[{isp}] JSON解析失败: {e}")
        return None
```

- [ ] **Step 3: 添加画质去重函数**

```python
def dedup_channels(channels: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for ch in channels:
        code = ch.get("chnunCode", "")
        if not code:
            continue
        existing = seen.get(code)
        if existing is None or ch.get("chnDefinition", 0) > existing.get("chnDefinition", 0):
            seen[code] = ch
    result = list(seen.values())
    result.sort(key=lambda x: x.get("chnNum") or 9999)
    return result
```

- [ ] **Step 4: 提交**

```powershell
git add generate_iptv.py
git commit -m "Add EPG fetching and quality dedup functions"
```

---

### Task 4: 实现并发流地址解析与 m3u8 生成

**文件：**
- 修改: `generate_iptv.py`（添加 `resolve_stream_url()`、`process_isp()` 函数，完善 `main()`）

- [ ] **Step 1: 添加单频道流地址解析函数**

```python
def resolve_stream_url(channel: dict) -> tuple[dict, str | None]:
    chn_name = channel.get("chnName", "Unknown")
    play_url = channel.get("playUrl", "")
    if not play_url:
        print(f"  [{chn_name}] 缺少playUrl，跳过")
        return channel, None
    try:
        resp = requests.get(play_url, timeout=15)
        resp.raise_for_status()
        real = resp.json().get("u", "")
        if real:
            return channel, real
        print(f"  [{chn_name}] playUrl响应中无'u'字段")
        return channel, None
    except requests.RequestException as e:
        print(f"  [{chn_name}] 流地址解析失败: {e}")
        return channel, None
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  [{chn_name}] playUrl响应解析失败: {e}")
        return channel, None
```

- [ ] **Step 2: 添加单个 ISP 处理函数**

```python
def process_isp(code: str, name: str, output: str):
    print(f"\n{'='*50}")
    print(f"处理 {name} ({code}) ...")
    print(f"{'='*50}")

    data = fetch_epg(code)
    if data is None:
        print(f"[{name}] 无法获取EPG数据，跳过")
        return

    channels = data.get("data", [])
    print(f"[{name}] 共 {len(channels)} 个频道条目")

    channels = dedup_channels(channels)
    print(f"[{name}] 去重后 {len(channels)} 个频道")

    lines = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(resolve_stream_url, ch): ch for ch in channels}
        for future in as_completed(futures):
            ch, real_url = future.result()
            if real_url:
                extinf = format_extinf(ch, real_url)
                lines.append(extinf)
                lines.append(real_url)
                print(f"  [OK] {ch.get('chnName')}")

    m3u8 = "#EXTM3U\n" + "\n".join(lines) + "\n"
    with open(output, "w", encoding="utf-8") as f:
        f.write(m3u8)
    print(f"[{name}] 已写入 {len(lines) // 2} 个频道 -> {output}")
```

- [ ] **Step 3: 完善 main() 入口函数**

```python
def main():
    for code, name, output in ISP_CONFIGS:
        process_isp(code, name, output)
    print("\n全部完成。")
```

- [ ] **Step 4: 提交**

```powershell
git add generate_iptv.py
git commit -m "Add concurrent stream resolution and main workflow"
```

---

### Task 5: 执行验证

- [ ] **Step 1: 运行脚本生成 m3u8 文件**

```powershell
uv run python generate_iptv.py
```

- [ ] **Step 2: 检查输出文件**

```powershell
Get-ChildItem iptv_js_*.m3u | Select-Object Name, Length
```

预期：三个 m3u8 文件，大小 > 0。

- [ ] **Step 3: 抽查 m3u8 内容格式**

```powershell
Get-Content iptv_js_unicom.m3u -Head 20
```

预期：`#EXTM3U` 头 + 连续的 `#EXTINF` 行与 URL 行成对出现，含分组信息和节目名。

- [ ] **Step 4: 统计各分组频道数**

```powershell
Select-String -Path iptv_js_unicom.m3u -Pattern 'group-title=' | ForEach-Object { if ($_ -match 'group-title="([^"]+)"') { $matches[1] } } | Group-Object | Select-Object Count, Name
```

预期：CCTV、江苏、南京、卫视、教育、其他 分组均有频道。

- [ ] **Step 5: 提交（如有 .gitignore 需要添加）**

确认 `.gitignore` 包含 `.venv/` 和 m3u8 输出文件后，无额外的提交。
