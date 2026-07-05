#!/usr/bin/env python3
"""江苏IPTV直播源m3u8生成器"""

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

ISP_CONFIGS = [
    ("JS_CUCC", "联通", "js-cucc.m3u"),
    # 以下运营商M3U源暂不可用，预留待以后恢复
    # ("JS_CMCC", "移动", "js-cmcc.m3u"),
    # ("JS_CTCC", "电信", "js-ctcc.m3u"),
]

CHANNEL_LIST_URL = "http://live.epg.gitv.tv/tagNewestEpgList/{isp}/1/100/0.json"
CHANNEL_INFO_URL = "http://live.epg.gitv.tv/chnInfos/{isp}/0.json"


def get_group(chn_name: str, chn_type_id: int | None = None) -> str:
    if chn_type_id is not None:
        if chn_type_id == 1:
            return "CCTV"
        if chn_type_id == 3:
            return "南京"
        if chn_type_id == 5:
            return "江苏本地"
        if chn_type_id == 2:
            if "卫视" in chn_name:
                return "卫视"
            if any(k in chn_name for k in ["CETV", "教育"]):
                return "教育"
            if "江苏" in chn_name:
                return "江苏本地"
            return "其他"

    if any(k in chn_name for k in ["CCTV", "CGTN"]):
        return "CCTV"
    if "南京" in chn_name:
        return "南京"
    if "江苏" in chn_name:
        return "江苏本地"
    if "卫视" in chn_name:
        return "卫视"
    if any(k in chn_name for k in ["CETV", "教育"]):
        return "教育"
    return "其他"


def normalize_channel_name(chn_name: str) -> str:
    """将频道名标准化为与EPG display-name一致的格式"""
    # 去除质量后缀（高清、超清、8M等）
    name = re.sub(r"-?(?:高清|超清|8M)", "", chn_name).strip("- ")

    # CCTV: "CCTV-1" -> "CCTV1"（与EPG对齐，去掉横杠）
    name = re.sub(r"CCTV-(\d+)", r"CCTV\1", name)

    # CETV -> 中国教育台
    cetv_map = {
        "CETV-1": "中国教育1台",
        "CETV-2": "中国教育2台",
        "CETV-3": "中国教育3台",
        "CETV-4": "中国教育4台",
    }
    if name in cetv_map:
        return cetv_map[name]

    # 海南卫视 -> 旅游卫视（EPG使用旧名称）
    if name == "海南卫视":
        return "旅游卫视"

    return name


def format_extinf(channel: dict, logo_url: str = "") -> str:
    chn_name = channel.get("chnName", "")
    chn_type_id = channel.get("chnTypeId")
    group = get_group(chn_name, chn_type_id)
    display_name = normalize_channel_name(chn_name)
    tvg_id = channel.get("chnCode", "")

    extinf = (
        f'#EXTINF:-1 group-title="{group}"'
        f' tvg-name="{display_name}"'
        f' tvg-id="{tvg_id}"'
        f' tvg-logo="{logo_url}",'
        f'{display_name}'
    )
    return extinf


def fetch_epg(isp: str) -> dict | None:
    url = CHANNEL_LIST_URL.format(isp=isp)
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


def fetch_chninfos(isp: str) -> dict[str, str] | None:
    url = CHANNEL_INFO_URL.format(isp=isp)
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == "A000000":
            logo_map = {}
            for item in data.get("data", []):
                chn_code = item.get("chnCode", "")
                if not chn_code:
                    continue
                logo = item.get("chnIcon") or ""
                if logo:
                    logo_map[chn_code] = logo
            return logo_map
        print(f"[{isp}] chnInfos API返回异常: code={data.get('code')}, message={data.get('message')}")
        return None
    except requests.RequestException as e:
        print(f"[{isp}] chnInfos网络请求失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"[{isp}] chnInfos JSON解析失败: {e}")
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
    return result


def resolve_stream_url(channel: dict) -> tuple[dict, str | None]:
    chn_name = channel.get("chnName", "Unknown")
    play_url = channel.get("playUrl", "")
    if not play_url:
        print(f"  [{chn_name}] 缺少playUrl，跳过")
        return channel, None
    try:
        resp = requests.get(play_url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        real = data.get("u", "")
        if real:
            return channel, real
        if isinstance(data.get("data"), list) and len(data["data"]) > 0:
            real = data["data"][0].get("url", "")
            if real:
                return channel, real
        print(f"  [{chn_name}] playUrl响应中无法提取流地址，使用原始地址")
        return channel, play_url
    except requests.RequestException as e:
        print(f"  [{chn_name}] 流地址解析失败: {e}，使用原始地址")
        return channel, play_url
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        print(f"  [{chn_name}] playUrl响应解析失败: {e}，使用原始地址")
        return channel, play_url


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

    logo_map = fetch_chninfos(code)
    if logo_map:
        print(f"[{name}] 获取到 {len(logo_map)} 个台标信息")
    else:
        print(f"[{name}] 未获取到台标信息，将使用空logo")
        logo_map = {}

    channels = dedup_channels(channels)
    print(f"[{name}] 去重后 {len(channels)} 个频道")

    results = {}
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(resolve_stream_url, ch): i for i, ch in enumerate(channels)}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                ch, real_url = future.result()
            except Exception as e:
                ch = channels[idx]
                print(f"  [ERR] {ch.get('chnName', 'Unknown')} 处理异常: {e}")
                continue
            if real_url:
                logo_url = logo_map.get(ch.get("chnCode", ""), "")
                results[idx] = (format_extinf(ch, logo_url), real_url)
                print(f"  [OK] {ch.get('chnName')}")

    lines = []
    for idx in sorted(results):
        extinf, real_url = results[idx]
        lines.append(extinf)
        lines.append(real_url)

    m3u8 = "#EXTM3U\n" + "\n".join(lines) + "\n"
    with open(output, "w", encoding="utf-8") as f:
        f.write(m3u8)
    print(f"[{name}] 已写入 {len(lines) // 2} 个频道 -> {output}")


def main():
    for code, name, output in ISP_CONFIGS:
        process_isp(code, name, output)
    print("\n全部完成。")


if __name__ == "__main__":
    main()
