#!/usr/bin/env python3
"""按可用性与延迟把源分成三档。

用法:
    python 三档分级.py \
        --sources 01-源清单/03-中文优先/中文优先清单.json \
        --connectivity 01-源清单/05-连通性检测/connectivity_二轮.json \
        --outdir 01-源清单/04-三档分级 --prefix 三档分级清单

分档规则（先定档，档内按延迟升序，同延迟再按质量分降序）:
    一档-首用     HTTP 200 可达，且（官方正版 或 跨生态收录 或 质量分 >= 46）
    二档-备用     HTTP 200 可达，但为单生态小站
    三档-待复测   其余：反爬 403/503、超时、代理网关错误、HTTP 4xx
    已废-不建议投入  DNS 解析失败或 TLS 握手失败

速度标签: <400ms 快 · 400-1200ms 中 · >1200ms 慢
"""
import argparse
import csv
import json
import os

BAND = lambda ms: "" if not ms else ("快" if ms < 400 else ("中" if ms < 1200 else "慢"))


def subclass(conn):
    """把连接结果归到子类。"""
    if not conn:
        return "Z-未检测"
    st, al, err = conn.get("status", 0), conn.get("alive", 0), conn.get("error", "")
    if al and st == 200:
        return "B-正常可达"
    if al and st in (403, 503):
        return "A-反爬拦截(活着)"
    if al:
        return f"A-活着(HTTP {st})"
    if err.startswith("HTTP 5"):
        return "C-代理/网关错误(待复测)"
    if err == "timeout":
        return "C-超时(待复测)"
    if err.startswith("HTTP 4"):
        return "D-HTTP错误(可能改版)"
    if "dns" in err.lower() or err == "dns_fail":
        return "F-DNS失败(已废)"
    if err.lower().startswith("tls") or "SSL" in err or "EOF" in err:
        return "F-TLS失败(已废)"
    return "E-其他失败"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True, help="中文优先清单.json")
    ap.add_argument("--connectivity", required=True, help="连通性检测输出的 json")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--prefix", default="三档分级清单")
    a = ap.parse_args()

    src = json.load(open(a.sources, encoding="utf-8-sig"))
    conn = {r["domain"]: r for r in json.load(open(a.connectivity, encoding="utf-8-sig"))}
    os.makedirs(a.outdir, exist_ok=True)

    tiers = {"一档-首用": [], "二档-备用": [], "三档-待复测": []}
    dead = []
    for x in src:
        d = x.get("domain", "")
        if "." not in d:
            continue
        c = conn.get(d, {})
        sub = subclass(c)
        lat = c.get("latency_ms", 0)
        row = {
            "domain": d, "subclass": sub, "latency_ms": lat, "speed": BAND(lat),
            "http_status": c.get("status", 0), "score": x.get("score", 0),
            "quality_tier": x.get("tier", ""), "effort": x.get("effort", ""),
            "official": x.get("official", ""), "nsfw": x.get("nsfw", False),
            "eco_count": x.get("eco_count", 0), "ecosystems": x.get("ecosystems", []),
            "names": x.get("names", []),
        }
        if sub.startswith("F-"):
            dead.append(row)
        elif sub == "B-正常可达":
            high = bool(x.get("official")) or x.get("eco_count", 0) > 1 or x.get("score", 0) >= 46
            tiers["一档-首用" if high else "二档-备用"].append(row)
        else:
            tiers["三档-待复测"].append(row)

    for k in tiers:
        tiers[k].sort(key=lambda r: (r["subclass"], r["latency_ms"] or 999999, -r["score"]))

    print("=== 分档结果 ===")
    for k in tiers:
        v = tiers[k]
        lat = sorted(r["latency_ms"] for r in v if r["latency_ms"])
        med = lat[len(lat) // 2] if lat else 0
        print(f"  {k}: {len(v):>3} 个   中位延迟 {med}ms")
        from collections import Counter
        for s, n in Counter(r["subclass"] for r in v).most_common():
            print(f"        {n:>3}  {s}")
    print(f"  已废-不建议投入: {len(dead)} 个")

    print(f"\n=== 一档 {len(tiers['一档-首用'])} 个（按延迟升序）===")
    for i, r in enumerate(tiers["一档-首用"], 1):
        star = f" ★{r['official']}" if r["official"] else ""
        print(f" {i:>2} {r['latency_ms']:>6}ms {r['speed']}  {r['domain']:<30} "
              f"{r['effort']:<8}{star}")

    jout = {k: v for k, v in tiers.items()}
    jout["已废-不建议投入"] = dead
    json.dump(jout, open(os.path.join(a.outdir, a.prefix + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    with open(os.path.join(a.outdir, a.prefix + ".csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["档位", "档内排名", "子类", "域名", "延迟ms", "速度", "HTTP", "质量分",
                    "质量层", "工作量", "官方", "NSFW", "生态数", "生态", "源名"])
        for k in list(tiers) + ["已废-不建议投入"]:
            rows = tiers[k] if k in tiers else dead
            for i, r in enumerate(rows, 1):
                w.writerow([k, i, r["subclass"], r["domain"], r["latency_ms"], r["speed"],
                            r["http_status"], r["score"], r["quality_tier"], r["effort"],
                            r["official"], int(bool(r["nsfw"])), r["eco_count"],
                            "|".join(r["ecosystems"]), "|".join(r["names"])[:180]])
    print(f"\n已输出 {a.outdir}/{a.prefix}.json 与 .csv")


if __name__ == "__main__":
    main()
