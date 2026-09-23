#!/usr/bin/env python3
"""一键重建整条源清单流水线。

用法:
    python 全量重建.py                       # 含连通性检测（需联网）
    python 全量重建.py --skip-network        # 跳过联网步骤，用已有检测结果重新分档

流程:
    1. 重建清单.py         raw 提取结果 → 去重主表 + 全量评分表 + 中文优先清单
    2. 连通性检测.py ×2    两轮探测（第二轮的档位作为当前生效版本）
    3. 三档分级.py ×2      首轮存档 + 当前版本
    4. 延迟对照 + 工作清单  两轮稳定性、可直接执行的工作清单
    5. 开源仓库构建.py      开源漫画源清单/ 三大类全部数据
    6. 手机源构建.py        手机源/ 四档自包含目录
"""
import argparse
import csv
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
R = os.path.abspath(os.path.join(HERE, ".."))

RAW = os.path.join(R, "01-源清单/06-原始提取/原始索引与中间结果")
M = os.path.join(R, "01-源清单")
CONN = os.path.join(M, "05-连通性检测")
TIER = os.path.join(M, "04-三档分级")
ZH = os.path.join(M, "03-中文优先/中文优先清单.json")
TIERS_JSON = os.path.join(TIER, "三档分级清单.json")


def run(script, *args):
    cmd = [PY, os.path.join(HERE, script), *args]
    print(f"\n$ {script} {' '.join(args)}", flush=True)
    r = subprocess.run(cmd, cwd=R)
    if r.returncode != 0:
        raise SystemExit(f"✗ {script} 退出码 {r.returncode}")


def delay_compare():
    """两轮延迟对照 + 工作清单。"""
    r1 = {x["domain"]: x for x in json.load(open(os.path.join(CONN, "connectivity_首轮.json"),
                                                 encoding="utf-8"))}
    r2 = {x["domain"]: x for x in json.load(open(os.path.join(CONN, "connectivity_二轮.json"),
                                                 encoding="utf-8"))}
    meta = {x["domain"]: x for x in json.load(open(ZH, encoding="utf-8"))}

    rows, work = [], []
    for d in sorted(set(r1) & set(r2)):
        a, b = r1[d], r2[d]
        ala, alb = bool(a["alive"]), bool(b["alive"])
        if ala and alb:
            la, lb = a["latency_ms"], b["latency_ms"]
            avg, diff = (la + lb) // 2, abs(la - lb)
            spot = ("延迟波动大" if diff > 800 else
                    "稳定快" if avg < 400 else "稳定中" if avg < 1200 else "稳定慢")
        else:
            la = lb = avg = diff = 0
            spot = "不稳定" if (ala or alb) else "两轮都不通"
        rows.append({"domain": d, "lat1": a["latency_ms"], "lat2": b["latency_ms"],
                     "avg": avg, "diff": diff, "alive1": int(ala), "alive2": int(alb),
                     "stability": spot, "score": meta.get(d, {}).get("score", 0),
                     "tier": meta.get(d, {}).get("tier", ""),
                     "effort": meta.get(d, {}).get("effort", "")})
        if ala and alb:
            state = "now_ok"
        elif not ala and not alb and (a["error"].startswith("HTTP 5") or a["error"] == "timeout"
                                      or b["error"].startswith("HTTP 5") or b["error"] == "timeout"):
            state = "retest_proxy"
        else:
            state = "dead"
        m = meta.get(d, {})
        work.append({"domain": d, "state": state, "tier": m.get("tier", ""),
                     "score": m.get("score", 0), "effort": m.get("effort", ""),
                     "official": m.get("official", ""), "nsfw": int(bool(m.get("nsfw"))),
                     "ecosystems": "|".join(m.get("ecosystems", [])),
                     "http_status": b["status"], "latency_ms": b["latency_ms"],
                     "error": b["error"]})

    order = {"now_ok": 0, "retest_proxy": 1, "dead": 2}
    work.sort(key=lambda x: (order[x["state"]], -x["score"]))
    rows.sort(key=lambda x: (x["stability"], x["avg"] or 999999))

    with open(os.path.join(CONN, "两轮延迟对照.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(CONN, "工作清单.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(work[0].keys()))
        w.writeheader()
        w.writerows(work)

    from collections import Counter
    print("\n=== 两轮稳定性 ===")
    for k, n in Counter(x["stability"] for x in rows).most_common():
        print(f"  {n:>4}  {k}")
    print("=== 工作清单 ===")
    for k, n in Counter(x["state"] for x in work).most_common():
        print(f"  {n:>4}  {k}")
    print("已输出 两轮延迟对照.csv 与 工作清单.csv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-network", action="store_true", help="跳过连通性检测，用已有结果")
    a = ap.parse_args()

    print("=" * 60, "\n[1/6] 重建清单")
    run("重建清单.py", "--raw", RAW, "--venera", os.path.join(R, "02-可用源"),
        "--outdir", M)

    if a.skip_network:
        print("\n[2/6] 跳过连通性检测（--skip-network）")
    else:
        print("=" * 60, "\n[2/6] 连通性检测 · 首轮")
        run("连通性检测.py", "--input", ZH, "--tag", "首轮", "--workers", "30",
            "--outdir", CONN)
        print("=" * 60, "\n[3/6] 连通性检测 · 二轮")
        run("连通性检测.py", "--input", ZH, "--tag", "二轮", "--workers", "30",
            "--outdir", CONN)

    print("=" * 60, "\n[4/6] 三档分级")
    run("三档分级.py", "--sources", ZH,
        "--connectivity", os.path.join(CONN, "connectivity_二轮.json"),
        "--outdir", TIER, "--prefix", "三档分级清单")
    run("三档分级.py", "--sources", ZH,
        "--connectivity", os.path.join(CONN, "connectivity_首轮.json"),
        "--outdir", TIER, "--prefix", "三档分级清单-首轮")

    print("=" * 60, "\n[5/6] 延迟对照")
    delay_compare()

    print("=" * 60, "\n[6/6] 开源仓库 + 手机源")
    run("开源仓库构建.py", "--outdir", os.path.join(R, "开源漫画源清单"),
        "--raw", RAW, "--master", M, "--tiers", TIERS_JSON)
    run("手机源构建.py", "--available", os.path.join(R, "02-可用源"),
        "--tiers", TIERS_JSON, "--outdir", os.path.join(R, "手机源"))

    print("\n" + "=" * 60)
    print("全流水线完成")


if __name__ == "__main__":
    main()
