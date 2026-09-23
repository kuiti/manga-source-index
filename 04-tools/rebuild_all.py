#!/usr/bin/env python3
"""Rebuild the whole source-index pipeline in one command.

用法 / Usage:
    python rebuild_all.py                    # full run, including connectivity probes (network)
    python rebuild_all.py --skip-network     # skip probing, re-tier from existing results

流程 / Pipeline:
    1. rebuild_index.py        raw extracts → master table + scored table + Chinese list
    2. check_connectivity.py   two probe rounds (round 2 is the effective one)
    3. build_tiers.py          tier assignment (round 1 archived as *-首轮)
    4. two-round comparison + actionable worklist
    5. build_repo.py           this repository's English data tree
    6. build_phone_sources.py  on-device Venera source tree, split by tier

默认路径对应本项目的本地布局（目录名为中文，因为本地数据以中文源为主）。
每个路径都可用命令行参数覆盖，便于移植到别的目录结构。
"""
import argparse
import csv
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def run(script, *args):
    cmd = [PY, os.path.join(HERE, script), *args]
    print(f"\n$ {script} {' '.join(args)}", flush=True)
    r = subprocess.run(cmd, cwd=os.path.dirname(HERE))
    if r.returncode != 0:
        raise SystemExit(f"x {script} exited with {r.returncode}")


def delay_compare(conn, zh_path):
    """Two-round latency comparison + actionable worklist."""
    r1 = {x["domain"]: x for x in json.load(open(os.path.join(conn, "connectivity_首轮.json"),
                                                 encoding="utf-8"))}
    r2 = {x["domain"]: x for x in json.load(open(os.path.join(conn, "connectivity_二轮.json"),
                                                 encoding="utf-8"))}
    meta = {x["domain"]: x for x in json.load(open(zh_path, encoding="utf-8"))}

    rows, work = [], []
    for d in sorted(set(r1) & set(r2)):
        a, b = r1[d], r2[d]
        ala, alb = bool(a["alive"]), bool(b["alive"])
        if ala and alb:
            la, lb = a["latency_ms"], b["latency_ms"]
            avg, diff = (la + lb) // 2, abs(la - lb)
            spot = ("unstable-latency" if diff > 800 else
                    "stable-fast" if avg < 400 else
                    "stable-mid" if avg < 1200 else "stable-slow")
        else:
            la = lb = avg = diff = 0
            spot = "flapping" if (ala or alb) else "both-fail"
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
    with open(os.path.join(conn, "两轮延迟对照.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    with open(os.path.join(conn, "工作清单.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(work[0].keys()))
        w.writeheader(); w.writerows(work)

    from collections import Counter
    print("\n=== two-round stability ===")
    for k, n in Counter(x["stability"] for x in rows).most_common():
        print(f"  {n:>4}  {k}")
    print("=== worklist ===")
    for k, n in Counter(x["state"] for x in work).most_common():
        print(f"  {n:>4}  {k}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-network", action="store_true")
    ap.add_argument("--raw", default="01-源清单/06-原始提取/原始索引与中间结果")
    ap.add_argument("--master", default="01-源清单")
    ap.add_argument("--available", default="02-可用源")
    ap.add_argument("--repo", default="开源漫画源清单")
    ap.add_argument("--phone", default="手机源")
    a = ap.parse_args()

    M = a.master
    CONN = os.path.join(M, "05-连通性检测")
    TIER = os.path.join(M, "04-三档分级")
    ZH = os.path.join(M, "03-中文优先/中文优先清单.json")
    TIERS_JSON = os.path.join(TIER, "三档分级清单.json")

    print("=" * 60, "\n[1/6] rebuild index")
    run("rebuild_index.py", "--raw", a.raw, "--venera", a.available, "--outdir", M)

    if a.skip_network:
        print("\n[2/6] skip connectivity (--skip-network)")
    else:
        print("=" * 60, "\n[2/6] connectivity · round 1")
        run("check_connectivity.py", "--input", ZH, "--tag", "首轮", "--workers", "30",
            "--outdir", CONN)
        print("=" * 60, "\n[3/6] connectivity · round 2")
        run("check_connectivity.py", "--input", ZH, "--tag", "二轮", "--workers", "30",
            "--outdir", CONN)

    print("=" * 60, "\n[4/6] tiering")
    run("build_tiers.py", "--sources", ZH,
        "--connectivity", os.path.join(CONN, "connectivity_二轮.json"),
        "--outdir", TIER, "--prefix", "三档分级清单")
    run("build_tiers.py", "--sources", ZH,
        "--connectivity", os.path.join(CONN, "connectivity_首轮.json"),
        "--outdir", TIER, "--prefix", "三档分级清单-首轮")

    print("=" * 60, "\n[5/6] latency comparison")
    delay_compare(CONN, ZH)

    print("=" * 60, "\n[6/6] repo tree + phone tree")
    run("build_repo.py", "--outdir", a.repo, "--raw", a.raw, "--master", M,
        "--tiers", TIERS_JSON)
    run("build_phone_sources.py", "--available", a.available, "--tiers", TIERS_JSON,
        "--outdir", a.phone)

    print("\n" + "=" * 60)
    print("pipeline finished")


if __name__ == "__main__":
    main()
