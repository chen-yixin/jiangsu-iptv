#!/usr/bin/env python3
"""江苏IPTV直播源m3u8生成器"""

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


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


def main():
    pass


if __name__ == "__main__":
    main()
