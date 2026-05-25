#!/usr/bin/env python3
"""江苏IPTV直播源m3u8生成器"""

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

ISP_CONFIGS = [
    ("JS_CUCC", "联通", "iptv_js_unicom.m3u"),
    ("JS_CMCC", "移动", "iptv_js_mobile.m3u"),
    ("JS_CTCC", "电信", "iptv_js_telecom.m3u"),
]

API_URL_TEMPLATE = "http://live.epg.gitv.tv/tagNewestEpgList/{isp}/1/100/0.json"


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
    return re.sub(r"-?(?:高清|超清|8M)", "", chn_name).strip("- ")


def format_extinf(channel: dict) -> str:
    chn_name = channel.get("chnName", "")
    group = get_group(chn_name)
    tvg_name = clean_tvg_name(chn_name)
    chn_num_raw = channel.get("chnNum")
    chn_num = str(chn_num_raw) if chn_num_raw is not None else ""
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


def main():
    pass


if __name__ == "__main__":
    main()
