#!/usr/bin/env python3
"""构建开源源库目录树：按生态细分的三大类数据。

用法:
    python 开源仓库构建.py \
        --outdir 开源漫画源清单 \
        --raw "01-源清单/06-原始提取/原始索引与中间结果" \
        --master "01-源清单" \
        --tiers "01-源清单/04-三档分级/三档分级清单.json"

输出:
    01-所有生态-所有源/   00-去重总表.*  +  按生态 *.csv
    02-所有生态-中文源/   00-去重总表.*  +  按生态 *.csv
    03-所有生态-三档源/   <档位>/00-本档完整清单.csv + <档位>/按生态/*.csv
                          前两档精选.csv|.json

只重建数据目录，README 与 04-工具 不动。
"""
import argparse
import csv
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 源工具 import fold_name, load, norm   # noqa: E402

ECO_ORDER = ["01-Mihon系", "02-Aidoku", "03-Kotatsu", "04-阅读Legado",
             "05-Venera", "06-Cimoc", "07-MangaReader"]
ECO_LABEL = {
    "01-Mihon系": "Mihon系（Mihon/Tachiyomi/Suwayomi/Komikku/Neko）",
    "02-Aidoku": "Aidoku（iOS）", "03-Kotatsu": "Kotatsu", "04-阅读Legado": "阅读 Legado",
    "05-Venera": "Venera", "06-Cimoc": "Cimoc", "07-MangaReader": "MangaReader",
}
# 生态短名（用于从「收录生态」字符串反查）
ECO_SHORT = {"01-Mihon系": "mihon", "02-Aidoku": "aidoku", "03-Kotatsu": "kotatsu",
             "04-阅读Legado": "legado", "05-Venera": "venera", "06-Cimoc": "cimoc",
             "07-MangaReader": "mangareader"}
ZH_ECO = {"04-阅读Legado", "05-Venera", "06-Cimoc", "07-MangaReader"}   # 天然中文向
ECO_FIELDS = ["生态", "源名", "站点域名", "语言", "NSFW", "标识/包名"]
TIER_FIELDS = ["档内排名", "站点域名", "子类", "延迟ms", "速度", "HTTP", "质量分", "质量层",
               "适配工作量", "官方正版", "NSFW", "收录生态数", "收录生态", "各生态源名"]

MR = {"bzm": "baozimhcn.com", "copy": "mangacopy.com", "dmzj": "idmzj.com",
      "happy": "happymh.com", "jmc": "18comic.vip", "kl": "klmanga.net",
      "mbz": "mangabz.com", "mhdb": "manhuadb.com", "mhg": "mhgui.com",
      "mhgm": "manhuagui.com", "mhm": "maofly.com", "nh": "nhentai.net",
      "pica": "picacomic.com", "rm5": "rouman5.com"}


def collect_by_eco(raw):
    """按生态收集源记录，保留各自的唯一标识。"""
    eco = {k: [] for k in ECO_ORDER}
    for x in load(os.path.join(raw, "Mihon系-提取结果.json")):
        eco["01-Mihon系"].append({"name": x.get("name", ""), "domain": norm(x.get("homeUrl")),
                                  "lang": x.get("lang", ""), "nsfw": x.get("nsfw", ""),
                                  "key": x.get("ext", "")})
    for x in load(os.path.join(raw, "Aidoku-提取结果.json")):
        eco["02-Aidoku"].append({"name": x.get("name", ""), "domain": norm(x.get("domain")),
                                 "lang": x.get("key", "").split(".")[0], "nsfw": "",
                                 "key": x.get("key", "")})
    for x in load(os.path.join(raw, "Kotatsu-提取结果.json")):
        eco["03-Kotatsu"].append({"name": x.get("name", ""), "domain": "",
                                  "lang": x.get("lang", ""), "nsfw": "",
                                  "key": x.get("file", "")})
    for x in load(os.path.join(raw, "阅读书源-漫画分组.json")):
        eco["04-阅读Legado"].append({"name": x.get("name", ""), "domain": norm(x.get("url")),
                                     "lang": "zh", "nsfw": "", "key": x.get("group", "")})
    for x in load(os.path.join(raw, "本地生态-提取结果.json")):
        k = "05-Venera" if x.get("ecosystem") == "venera" else "06-Cimoc"
        eco[k].append({"name": x.get("name", ""),
                       "domain": norm(x.get("baseUrl") or x.get("domain")),
                       "lang": "zh", "nsfw": "",
                       "key": x.get("key", "") or x.get("repo", "")})
    for k, v in MR.items():
        eco["07-MangaReader"].append({"name": k, "domain": norm(v), "lang": "zh",
                                      "nsfw": "", "key": k})
    for k in eco:
        for x in eco[k]:
            x["is_zh"] = int(k in ZH_ECO or x["lang"] in ("zh", "zh-hans", "zh-hant", "zh-cn",
                                                          "zh-tw", "zh-hk")
                              or bool(re.search(r"[\u4e00-\u9fff]", x["name"] or "")))
    return eco


def wcsv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--master", required=True)
    ap.add_argument("--tiers", required=True)
    a = ap.parse_args()

    eco = collect_by_eco(a.raw)
    tiers = load(a.tiers)

    # 不删目录：所有文件名都是确定性的（每个生态都写一份，空就是空表），
    # 重跑即覆盖，不存在残留。
    for d in ("01-所有生态-所有源", "02-所有生态-中文源", "03-所有生态-三档源"):
        os.makedirs(os.path.join(a.outdir, d), exist_ok=True)

    # ---- 01 / 02：跨生态总表 + 按生态拆分 ----
    for cat, zh_only in (("01-所有生态-所有源", False), ("02-所有生态-中文源", True)):
        d = os.path.join(a.outdir, cat)
        total = 0
        for k in ECO_ORDER:
            rows = [{"生态": ECO_LABEL[k], "源名": x["name"], "站点域名": x["domain"],
                     "语言": x["lang"], "NSFW": x["nsfw"], "标识/包名": x["key"]}
                    for x in eco[k] if (not zh_only or x["is_zh"])]
            wcsv(os.path.join(d, f"{k}.csv"), rows, ECO_FIELDS)
            total += len(rows)
            print(f"  {cat}/{k}.csv  {len(rows)} 条")
        src = os.path.join(a.master, "03-中文优先" if zh_only else "01-去重主表")
        base = "中文优先清单" if zh_only else "去重主表"
        shutil.copyfile(os.path.join(src, base + ".csv"), os.path.join(d, "00-去重总表.csv"))
        shutil.copyfile(os.path.join(src, base + ".json"), os.path.join(d, "00-去重总表.json"))
        print(f"  {cat} 合计 {total} 条（原始记录）")

    # ---- 03：三档（完整清单 + 按生态）----
    C = os.path.join(a.outdir, "03-所有生态-三档源")
    tier_rows = {}
    for tk in ("一档-首用", "二档-备用", "三档-待复测", "已废-不建议投入"):
        rows = [{"档内排名": i, "站点域名": r["domain"], "子类": r["subclass"],
                 "延迟ms": r["latency_ms"], "速度": r["speed"], "HTTP": r["http_status"],
                 "质量分": r["score"], "质量层": r["quality_tier"], "适配工作量": r["effort"],
                 "官方正版": r["official"], "NSFW": int(bool(r["nsfw"])),
                 "收录生态数": r["eco_count"], "收录生态": "|".join(r["ecosystems"]),
                 "各生态源名": "|".join(r["names"])[:200]}
                for i, r in enumerate(tiers.get(tk, []), 1)]
        tier_rows[tk] = rows
        d = os.path.join(C, tk)
        os.makedirs(os.path.join(d, "按生态"), exist_ok=True)
        wcsv(os.path.join(d, "00-本档完整清单.csv"), rows, TIER_FIELDS)
        nfile = 0
        for k in ECO_ORDER:      # 每个生态都写，无数据则只留表头
            short = ECO_SHORT[k]
            sub = [x for x in rows if short in [e.lower() for e in x["收录生态"].split("|")]]
            wcsv(os.path.join(d, "按生态", f"{k}.csv"), sub, TIER_FIELDS)
            nfile += 1 if sub else 0
        print(f"  03/{tk}/  完整 {len(rows)} 条 … 有数据的生态 {nfile}/{len(ECO_ORDER)}")

    # ---- 03：前两档精选（原始需求：分档的三档的前两档）----
    top2 = tier_rows["一档-首用"] + tier_rows["二档-备用"]
    with open(os.path.join(C, "前两档精选.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["档位"] + TIER_FIELDS)
        for tk in ("一档-首用", "二档-备用"):
            for r in tier_rows[tk]:
                w.writerow([tk] + [r[x] for x in TIER_FIELDS])
    json.dump({tk: tier_rows[tk] for tk in ("一档-首用", "二档-备用")},
              open(os.path.join(C, "前两档精选.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"  03/前两档精选.csv  {len(top2)} 条（一档 {len(tier_rows['一档-首用'])} "
          f"+ 二档 {len(tier_rows['二档-备用'])}）")
    print(f"\n输出到 {a.outdir}")


if __name__ == "__main__":
    main()
