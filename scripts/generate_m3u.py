import json
from pathlib import Path

INPUT = Path("jstr4web.json")
OUTPUT = Path("channels.m3u")


def load_channels():
    with INPUT.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("channels", "data", "items"):
            if isinstance(data.get(key), list):
                return data[key]

    raise ValueError("Unsupported JSON structure")


def has_drm(channel):
    # Format 1:
    # "keyId": "...",
    # "key": "..."

    key_id = channel.get("keyId")
    key = channel.get("key")

    if key_id and key:
        if str(key_id).lower() != "null" and str(key).lower() != "null":
            return True

    # Format 2:
    # "keys": [{"keyId":"...", "key":"..."}]

    keys = channel.get("keys")

    if isinstance(keys, list):
        for item in keys:
            if not isinstance(item, dict):
                continue

            kid = item.get("keyId")
            k = item.get("key")

            if kid and k:
                if str(kid).lower() != "null" and str(k).lower() != "null":
                    return True

    return False


def clean(value):
    if value is None:
        return ""
    return str(value).replace('"', "'").replace("\n", " ").strip()


def generate():
    channels = load_channels()

    lines = [
        "#EXTM3U",
        "# Generated automatically from jstr4web.json",
        ""
    ]

    total = 0
    drm_count = 0
    clear_count = 0

    for channel in channels:
        if not isinstance(channel, dict):
            continue

        name = clean(channel.get("name", "Unknown Channel"))
        channel_id = clean(channel.get("id", ""))
        category = clean(channel.get("category", "Live TV"))
        url = clean(channel.get("url", ""))
        logo = clean(channel.get("logo", ""))

        if not url:
            continue

        drm = has_drm(channel)

        if drm:
            drm_count += 1
            drm_ref = f"channel-{channel_id}" if channel_id else f"channel-{total + 1}"
        else:
            clear_count += 1
            drm_ref = ""

        lines.append(
            f'#EXTINF:-1 tvg-id="{channel_id}" '
            f'tvg-name="{name}" '
            f'tvg-logo="{logo}" '
            f'group-title="{category}",{name}'
        )

        lines.append(url)

        if drm:
            lines.append(f"#DRM-REF: {drm_ref}")

        lines.append("")

        total += 1

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"Channels generated : {total}")
    print(f"DRM channels       : {drm_count}")
    print(f"Non-DRM channels   : {clear_count}")
    print(f"Output             : {OUTPUT}")


if __name__ == "__main__":
    generate()
