#!/usr/bin/env python3
"""将 FinVault data.csv 转为按对话分组的 JSON（messages 列表，user/bot 交替）。"""

from __future__ import annotations

import argparse
import csv
import json
from collections import OrderedDict
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path("/Users/guoxing.lan/projects/datasets/Finance/FinVault/data.csv")


def csv_to_conversations(
    input_path: Path,
) -> list[dict[str, Any]]:
    """按 ID 分组，同一 ID 下按文件行顺序追加 user → bot 消息。"""
    groups: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    domains: dict[str, str] = {}

    with input_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conv_id = (row.get("ID") or "").strip()
            if not conv_id:
                continue
            user_text = (row.get("User") or "").strip()
            bot_text = (row.get("BOT") or "").strip()

            if conv_id not in groups:
                groups[conv_id] = []
                domains[conv_id] = (row.get("Domain") or "").strip()
            groups[conv_id].append({"role": "user", "content": user_text})
            groups[conv_id].append({"role": "bot", "content": bot_text})

    return [
        {"id": cid, "domain": domains[cid], "messages": msgs}
        for cid, msgs in groups.items()
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"输入 CSV 路径（默认: {DEFAULT_INPUT}）",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="输出 JSON 路径（默认与 CSV 同目录下的 finvault_messages.json）",
    )
    args = parser.parse_args()

    out_path = args.output
    if out_path is None:
        out_path = args.input.parent / "finvault_messages.json"

    data = csv_to_conversations(args.input)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"写入 {len(data)} 条对话 -> {out_path}")


if __name__ == "__main__":
    main()
