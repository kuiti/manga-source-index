#!/usr/bin/env python3
"""Build the open-source repository tree (English export).

用法:
    python build_repo.py \
        --outdir "开源漫画源清单" \
        --raw "01-源清单/06-原始提取/原始索引与中间结果" \
        --master "01-源清单" \
        --tiers "01-源清单/04-三档分级/三档分级清单.json"

输出（全英文目录名/文件名/表头/枚举值）:
    01-all-sources/          00-deduplicated-master.csv|.json + 7 per-ecosystem csv
    02-chinese-sources/      00-deduplicated-master.csv|.json + 7 per-ecosystem csv
    03-tiered-sources/       tier1-primary|tier2-backup|tier3-retest|dead-skip
                             ├── 00-full-list.csv + by-ecosystem/*.csv
                             └── tier1-2-selection.csv|.json（仓库根，位于 03/ 下）

**本脚本是唯一的中→英导出层。** 本地 `01-源清单/` 保持中文（内部规范），
只有这里做本地化：目录名、文件名、CSV 表头、枚举值。源名/站点名等专有名词不翻译。

注意：所有文件名都是确定性的（每个生态都写一份，空就是空表），重跑即覆盖、零残留，
不使用任何删除操作。
"""
import argparse
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from source_utils import load, norm   # noqa: E402

ECO_ORDER = ["mihon", "aidoku", "kotatsu", "legado", "venera", "cimoc", "mangareader"]
ECO_FILE = {"mihon": "01-mihon-family.csv", "aidoku": "02-aidoku.csv",
            "kotatsu": "03-kotatsu.csv", "legado": "04-legado.csv",
            "venera": "05-venera.csv", "cimoc": "06-cimoc.csv",
            "mangareader": "07-mangareader.csv"}
ECO_LABEL = {
    "mihon": "Mihon family (Mihon / Tachiyomi / Suwayomi / Komikku / Neko)",
    "aidoku": "Aidoku (iOS)", "kotatsu": "Kotatsu", "legado": "Legado (阅读)",
    "venera": "Venera", "cimoc": "Cimoc", "mangareader": "MangaReader",
}
ZH_ECO = {"legado", "venera", "cimoc", "mangareader"}   # Chinese-oriented by nature

# ---- 枚举值英译 ----
V_TIER = {"一档-首用": "tier1-primary", "二档-备用": "tier2-backup",
          "三档-待复测": "tier3-retest", "已废-不建议投入": "dead-skip"}
V_SPEED = {"快": "fast", "中": "mid", "慢": "slow", "": ""}
V_EFFORT = {"已有实现": "existing", "需新写": "to-build"}
V_SUBCLASS = {
    "B-正常可达": "B-reachable",
    "A-反爬拦截(活着)": "A-bot-blocked (alive)",
    "C-代理/网关错误(待复测)": "C-proxy-or-gateway-error (retest)",
    "C-超时(待复测)": "C-timeout (retest)",
    "D-HTTP错误(可能改版)": "D-http-error (possibly redesigned)",
    "E-其他失败": "E-other-failure",
    "F-DNS失败(已废)": "F-dns-failure (dead)",
    "F-TLS失败(已废)": "F-tls-failure (dead)",
    "Z-未检测": "Z-not-probed",
}
# 官方/授权站英文名，按域名
OFFICIAL_EN = {
    "ac.qq.com": "Tencent Comics (official)",
    "manga.bilibili.com": "Bilibili Comics (official)",
    "bilimanga.net": "Bilibili Comics (official)",
    "kuaikanmanhua.com": "Kuaikan Comics (official)",
    "iqiyi.com": "iQiyi Comics (official)",
    "dmzj.com": "DMZJ (Dongman Zhijia)",
    "idmzj.com": "DMZJ (Dongman Zhijia)",
    "shonenjumpplus.com": "Shonen Jump+ (official)",
    "mangaplus.shueisha.co.jp": "MANGA Plus (official)",
    "comic-walker.com": "Kadokomi (official)",
    "mangadex.org": "MangaDex (open licensed)",
    "webtoons.com": "LINE WEBTOON (official)",
    "tapas.io": "Tapas (official)",
    "namicomi.com": "NamiComi",
    "mangamillion.shueisha.co.jp": "Manga Million (official)",
}

MASTER_FIELDS = ["rank", "domain", "is_chinese", "score", "tier", "official", "nsfw",
                 "eco_count", "effort", "ecosystems", "names", "langs"]
ECO_FIELDS = ["ecosystem", "source_name", "domain", "language", "nsfw", "identifier"]
TIER_FIELDS = ["rank", "domain", "subclass", "latency_ms", "speed", "http_status",
               "quality_score", "quality_tier", "effort", "official", "nsfw",
               "ecosystem_count", "ecosystems", "source_names"]

MR = {"bzm": "baozimhcn.com", "copy": "mangacopy.com", "dmzj": "idmzj.com",
      "happy": "happymh.com", "jmc": "18comic.vip", "kl": "klmanga.net",
      "mbz": "mangabz.com", "mhdb": "manhuadb.com", "mhg": "mhgui.com",
      "mhgm": "manhuagui.com", "mhm": "maofly.com", "nh": "nhentai.net",
      "pica": "picacomic.com", "rm5": "rouman5.com"}


def en(v, table):
    """枚举值英译，未收录的原样返回（便于发现遗漏）。"""
    return table.get(v, v)


def collect_by_eco(raw):
    """按生态收集源记录，保留各自唯一标识。"""
    eco = {k: [] for k in ECO_ORDER}
    for x in load(os.path.join(raw, "Mihon系-提取结果.json")):
        eco["mihon"].append({"name": x.get("name", ""), "domain": norm(x.get("homeUrl")),
                             "lang": x.get("lang", ""), "nsfw": x.get("nsfw", ""),
                             "key": x.get("ext", "")})
    for x in load(os.path.join(raw, "Aidoku-提取结果.json")):
        eco["aidoku"].append({"name": x.get("name", ""), "domain": norm(x.get("domain")),
                              "lang": x.get("key", "").split(".")[0], "nsfw": "",
                              "key": x.get("key", "")})
    for x in load(os.path.join(raw, "Kotatsu-提取结果.json")):
        eco["kotatsu"].append({"name": x.get("name", ""), "domain": "",
                               "lang": x.get("lang", ""), "nsfw": "",
                               "key": x.get("file", "")})
    for x in load(os.path.join(raw, "阅读书源-漫画分组.json")):
        eco["legado"].append({"name": x.get("name", ""), "domain": norm(x.get("url")),
                              "lang": "zh", "nsfw": "", "key": x.get("group", "")})
    for x in load(os.path.join(raw, "本地生态-提取结果.json")):
        k = "venera" if x.get("ecosystem") == "venera" else "cimoc"
        eco[k].append({"name": x.get("name", ""),
                       "domain": norm(x.get("baseUrl") or x.get("domain")),
                       "lang": "zh", "nsfw": "",
                       "key": x.get("key", "") or x.get("repo", "")})
    for k, v in MR.items():
        eco["mangareader"].append({"name": k, "domain": norm(v), "lang": "zh",
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


def en_master_row(r, i):
    """把中文清单行转成英文导出行。"""
    return {
        "rank": i, "domain": r["domain"], "is_chinese": int(bool(r.get("is_zh", True))),
        "score": r["score"], "tier": r["tier"],
        "official": OFFICIAL_EN.get(r["domain"], r.get("official", "")),
        "nsfw": int(bool(r.get("nsfw"))), "eco_count": r.get("eco_count", 0),
        "effort": en(r.get("effort", ""), V_EFFORT),
        "ecosystems": "|".join(r.get("ecosystems", [])),
        "names": "|".join(r.get("names", []))[:200],
        "langs": "|".join(r.get("langs", [])),
    }


def en_tier_row(r, i):
    return {
        "rank": i, "domain": r["domain"], "subclass": en(r["subclass"], V_SUBCLASS),
        "latency_ms": r["latency_ms"], "speed": en(r["speed"], V_SPEED),
        "http_status": r["http_status"], "quality_score": r["score"],
        "quality_tier": r["quality_tier"], "effort": en(r["effort"], V_EFFORT),
        "official": OFFICIAL_EN.get(r["domain"], r.get("official", "")),
        "nsfw": int(bool(r.get("nsfw"))), "ecosystem_count": r["eco_count"],
        "ecosystems": "|".join(r.get("ecosystems", [])),
        "source_names": "|".join(r.get("names", []))[:200],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--master", required=True)
    ap.add_argument("--tiers", required=True)
    a = ap.parse_args()

    eco = collect_by_eco(a.raw)
    tiers = load(a.tiers)
    scored = load(os.path.join(a.master, "02-质量评分/全量评分表.json"))

    D1 = os.path.join(a.outdir, "01-all-sources")
    D2 = os.path.join(a.outdir, "02-chinese-sources")
    D3 = os.path.join(a.outdir, "03-tiered-sources")
    for d in (D1, D2, D3):
        os.makedirs(d, exist_ok=True)

    # ---- 01 / 02：跨生态总表 + 按生态拆分 ----
    for d, rows_src, tag in ((D1, scored["all"], "01-all-sources"),
                             (D2, scored["zh"], "02-chinese-sources")):
        out = [en_master_row(r, i) for i, r in enumerate(rows_src, 1)]
        wcsv(os.path.join(d, "00-deduplicated-master.csv"), out, MASTER_FIELDS)
        json.dump(out, open(os.path.join(d, "00-deduplicated-master.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)
        total = 0
        for k in ECO_ORDER:
            rows = [{"ecosystem": ECO_LABEL[k], "source_name": x["name"],
                     "domain": x["domain"], "language": x["lang"],
                     "nsfw": x["nsfw"], "identifier": x["key"]}
                    for x in eco[k] if (tag.startswith("01") or x["is_zh"])]
            wcsv(os.path.join(d, ECO_FILE[k]), rows, ECO_FIELDS)
            total += len(rows)
        print(f"  {tag}: 总表 {len(out)} 行 + 7 张按生态表（合计 {total} 条）")

    # ---- 03：三档 ----
    tier_rows = {}
    for tk in ("一档-首用", "二档-备用", "三档-待复测", "已废-不建议投入"):
        en_key = V_TIER[tk]
        rows = [en_tier_row(r, i) for i, r in enumerate(tiers.get(tk, []), 1)]
        tier_rows[en_key] = rows
        d = os.path.join(D3, en_key)
        os.makedirs(os.path.join(d, "by-ecosystem"), exist_ok=True)
        wcsv(os.path.join(d, "00-full-list.csv"), rows, TIER_FIELDS)
        nfile = 0
        for k in ECO_ORDER:          # 每个生态都写，无数据则只留表头
            sub = [x for x in rows if k in [e.lower() for e in x["ecosystems"].split("|")]]
            wcsv(os.path.join(d, "by-ecosystem", ECO_FILE[k]), sub, TIER_FIELDS)
            nfile += 1 if sub else 0
        print(f"  03/{en_key}/: {len(rows)} 条 … 有数据的生态 {nfile}/{len(ECO_ORDER)}")

    top2 = []
    for tk in ("tier1-primary", "tier2-backup"):
        for r in tier_rows[tk]:
            top2.append({"tier": tk, **r})
    wcsv(os.path.join(D3, "tier1-2-selection.csv"), top2, ["tier"] + TIER_FIELDS)
    json.dump({k: tier_rows[k] for k in ("tier1-primary", "tier2-backup")},
              open(os.path.join(D3, "tier1-2-selection.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"  03/tier1-2-selection: {len(top2)} 条"
          f"（tier1 {len(tier_rows['tier1-primary'])} + tier2 {len(tier_rows['tier2-backup'])}）")

    # ---- 校验：不应再出现未翻译的枚举值 ----
    untranslated = set()
    for rows in tier_rows.values():
        for r in rows:
            for field, table in (("subclass", V_SUBCLASS), ("speed", V_SPEED),
                                 ("effort", V_EFFORT)):
                v = r[field]
                if v and v in table and table[v] == v:
                    untranslated.add(f"{field}={v}")
            if re.search(r"[\u4e00-\u9fff]", r["official"] or ""):
                untranslated.add(f"official={r['official']}")
    print(f"\n输出到 {a.outdir}")
    print(f"未翻译的非专有名词项: {len(untranslated)}" +
          (f" → {sorted(untranslated)[:8]}" if untranslated else ""))


if __name__ == "__main__":
    main()
