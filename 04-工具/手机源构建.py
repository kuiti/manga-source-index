#!/usr/bin/env python3
"""构建手机上用的 Venera 源三档目录。

用法:
    python 手机源构建.py \
        --available 02-可用源 \
        --tiers "01-源清单/04-三档分级/三档分级清单.json" \
        --outdir 手机源

输入:
    02-可用源/合并全集/index.json + *.js     已有现成实现的 Venera 源
    02-可用源/Cimoc移植/index.json + *.js
    三档分级清单.json                        目标站点的档位、延迟、质量分

输出（每档自包含：index.json + js + _venera_.js）:
    手机源/一档/  二档/  三档/  其他-未定档/
    手机源/档位映射.csv                      每个源落在哪一档、依据是什么

档位判定：先按源 js 里的 baseUrl 域名匹配，匹配不到再按源名匹配。
已废站点（DNS/TLS 失败）并入三档，理由是这些源本身已实现，可能走镜像域名仍可用。
"""
import argparse
import csv
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 源工具 import fold_name, load, pick_base, norm   # noqa: E402

BUCKETS = {"一档-首用": "一档", "二档-备用": "二档",
           "三档-待复测": "三档", "已废-不建议投入": "三档"}
STD_FIELDS = ("name", "key", "version", "description", "type", "fileName", "url")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--available", required=True, help="02-可用源 目录")
    ap.add_argument("--tiers", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--template", default="_venera_.js",
                    help="类型声明文件名，从 --available 里查找并复制到各档")
    a = ap.parse_args()

    # ---- 1. 目标站点的档位索引 ----
    tiers = load(a.tiers)
    dom2tier, name2tier = {}, {}
    for tk in ("一档-首用", "二档-备用", "三档-待复测", "已废-不建议投入"):
        for r in tiers.get(tk, []):
            if r.get("domain"):
                dom2tier.setdefault(r["domain"], tk)
            for n in r.get("names", []):
                f = fold_name(n)
                if f:
                    name2tier.setdefault(f, tk)
    print(f"档位索引：域名 {len(dom2tier)} · 源名 {len(name2tier)}")

    # ---- 2. 遍历已有可用源 ----
    sources = []
    for sub in ("合并全集", "Cimoc移植"):
        d = os.path.join(a.available, sub)
        for x in load(os.path.join(d, "index.json")):
            fn = x.get("fileName")
            if not fn or not os.path.exists(os.path.join(d, fn)):
                continue
            txt = open(os.path.join(d, fn), encoding="utf-8", errors="ignore").read()
            dom = norm(pick_base(txt))
            sources.append({"_dir": d, "_file": fn, "_domain": dom, "_entry": x})
    print(f"已有可用源：{len(sources)} 个")

    # ---- 3. 分桶 ----
    for s in sources:
        tier = dom2tier.get(s["_domain"])
        basis = "域名" if tier else ""
        if not tier:
            nm = fold_name(s["_entry"].get("name"))
            tier = name2tier.get(nm)
            basis = "源名" if tier else ""
        s["_tier"] = tier or ""
        s["_basis"] = basis
        s["_bucket"] = BUCKETS.get(tier, "其他-未定档")

    # ---- 4. 输出 ----
    buckets = {}
    for s in sources:
        buckets.setdefault(s["_bucket"], []).append(s)

    tpl_src = None
    for sub in ("合并全集", "Cimoc移植"):
        p = os.path.join(a.available, sub, a.template)
        if os.path.exists(p):
            tpl_src = p
            break

    for name in ("一档", "二档", "三档", "其他-未定档"):
        d = os.path.join(a.outdir, name)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)
        items = buckets.get(name, [])
        idx = []
        for s in items:
            shutil.copyfile(os.path.join(s["_dir"], s["_file"]), os.path.join(d, s["_file"]))
            idx.append({k: v for k, v in s["_entry"].items() if k in STD_FIELDS})
        json.dump(idx, open(os.path.join(d, "index.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=4)
        if tpl_src:
            shutil.copyfile(tpl_src, os.path.join(d, a.template))
        print(f"  {name}/  {len(idx)} 源 · {len([f for f in os.listdir(d) if f.endswith('.js') and f != a.template])} js")

    with open(os.path.join(a.outdir, "档位映射.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["分档目录", "来源档位", "匹配依据", "源名", "站点域名", "源文件", "来源目录"])
        for s in sorted(sources, key=lambda x: (x["_bucket"], x["_entry"].get("name", ""))):
            w.writerow([s["_bucket"], s["_tier"] or "未收录", s["_basis"] or "-",
                        s["_entry"].get("name", ""), s["_domain"] or "-", s["_file"],
                        os.path.basename(s["_dir"])])
    print(f"  档位映射.csv  {len(sources)} 行")

    # ---- 5. 校验 ----
    bad = 0
    for name in ("一档", "二档", "三档", "其他-未定档"):
        d = os.path.join(a.outdir, name)
        for x in json.load(open(os.path.join(d, "index.json"), encoding="utf-8")):
            if x.get("fileName") and not os.path.exists(os.path.join(d, x["fileName"])):
                print(f"  ✗ 缺失 {name}/{x['fileName']}")
                bad += 1
    print(f"\n校验：index.json 引用缺失 {bad} 个")


if __name__ == "__main__":
    main()
