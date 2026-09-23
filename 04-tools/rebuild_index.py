#!/usr/bin/env python3
"""从各生态原始提取结果重建去重主表、全量评分表与中文源清单。

用法:
    python 重建清单.py --raw 01-源清单/06-原始提取/原始索引与中间结果 \
                       --venera 02-可用源 \
                       --outdir 01-源清单

输入:
    <raw>/Mihon系-提取结果.json     字段 name/domain/lang/nsfw/key
    <raw>/Aidoku-提取结果.json      字段 name/domain/lang/nsfw/key
    <raw>/Kotatsu-提取结果.json     字段 name/lang/key（无域名）
    <raw>/阅读书源-漫画分组.json     字段 name/url/group
    <raw>/本地生态-提取结果.json     ecosystem=venera|cimoc，字段 name/baseUrl/domain/key
    <venera>/合并全集/index.json、<venera>/Cimoc移植/index.json  （用于判定「已有实现」）

输出:
    01-去重主表/去重主表.csv|.json
    02-质量评分/全量评分表.csv|.json
    03-中文优先/中文优先清单.csv|.json

注意：域名归一化只有 norm() 这一份实现，顺序不可调换
（必须先剥协议、再清非域名字符，否则 https://ac.qq.com 会被拼成 httpsac.qq.com）。
"""
import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from source_utils import fold_name, has_impl, load, load_venera_names, norm   # noqa: E402

ZH_LANG = {"zh", "zh-hans", "zh-hant", "zh-cn", "zh-tw", "zh-hk", "zh-sg"}
ZH_ECO = {"cimoc", "venera", "mangareader"}          # 天然中文向
ACTIVE_ECO = {"mihon", "venera", "cimoc", "legado", "aidoku", "mangareader"}
ARCHIVED_ECO = {"kotatsu"}
CJK = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff]")

OFFICIAL = {
    "ac.qq.com": "腾讯动漫（正版）", "manga.bilibili.com": "哔哩漫画（正版）",
    "bilimanga.net": "哔哩漫画（正版）", "kuaikanmanhua.com": "快看漫画（正版）",
    "iqiyi.com": "爱奇艺漫画（正版）", "dmzj.com": "动漫之家", "idmzj.com": "动漫之家",
    "shonenjumpplus.com": "少年Jump+（正版）", "mangaplus.shueisha.co.jp": "MANGA Plus（正版）",
    "comic-walker.com": "カドコミ（正版）", "mangadex.org": "MangaDex（开放授权）",
    "webtoons.com": "LINE WEBTOON（正版）", "tapas.io": "Tapas（正版）",
    "namicomi.com": "NamiComi", "mangamillion.shueisha.co.jp": "Manga Million（正版）",
}


def score_of(m, is_zh, official):
    """把所有生态的源汇成统一记录。"""
    recs = []
    for x in load(os.path.join(raw, "Mihon系-提取结果.json")):
        recs.append(("mihon", x.get("name", ""), norm(x.get("homeUrl")),
                     x.get("lang", ""), x.get("nsfw", "")))
    for x in load(os.path.join(raw, "Aidoku-提取结果.json")):
        recs.append(("aidoku", x.get("name", ""), norm(x.get("domain")),
                     (x.get("key", "").split(".") or [""])[0], ""))
    for x in load(os.path.join(raw, "Kotatsu-提取结果.json")):
        recs.append(("kotatsu", x.get("name", ""), "", x.get("lang", ""), ""))
    for x in load(os.path.join(raw, "阅读书源-漫画分组.json")):
        recs.append(("legado", x.get("name", ""), norm(x.get("url")), "zh", ""))
    for x in load(os.path.join(raw, "本地生态-提取结果.json")):
        eco = x.get("ecosystem", "")
        recs.append((eco, x.get("name", ""), norm(x.get("baseUrl") or x.get("domain")), "zh", ""))
    MR = {"bzm": "baozimhcn.com", "copy": "mangacopy.com", "dmzj": "idmzj.com",
          "happy": "happymh.com", "jmc": "18comic.vip", "kl": "klmanga.net",
          "mbz": "mangabz.com", "mhdb": "manhuadb.com", "mhg": "mhgui.com",
          "mhgm": "manhuagui.com", "mhm": "maofly.com", "nh": "nhentai.net",
          "pica": "picacomic.com", "rm5": "rouman5.com"}
    for k, v in MR.items():
        recs.append(("mangareader", k, norm(v), "zh", ""))
    return recs


def collect(raw):
    """把所有生态的源汇成统一记录。"""
    recs = []
    for x in load(os.path.join(raw, "Mihon系-提取结果.json")):
        recs.append(("mihon", x.get("name", ""), norm(x.get("homeUrl")),
                     x.get("lang", ""), x.get("nsfw", "")))
    for x in load(os.path.join(raw, "Aidoku-提取结果.json")):
        recs.append(("aidoku", x.get("name", ""), norm(x.get("domain")),
                     (x.get("key", "").split(".") or [""])[0], ""))
    for x in load(os.path.join(raw, "Kotatsu-提取结果.json")):
        recs.append(("kotatsu", x.get("name", ""), "", x.get("lang", ""), ""))
    for x in load(os.path.join(raw, "阅读书源-漫画分组.json")):
        recs.append(("legado", x.get("name", ""), norm(x.get("url")), "zh", ""))
    for x in load(os.path.join(raw, "本地生态-提取结果.json")):
        eco = x.get("ecosystem", "")
        recs.append((eco, x.get("name", ""), norm(x.get("baseUrl") or x.get("domain")), "zh", ""))
    MR = {"bzm": "baozimhcn.com", "copy": "mangacopy.com", "dmzj": "idmzj.com",
          "happy": "happymh.com", "jmc": "18comic.vip", "kl": "klmanga.net",
          "mbz": "mangabz.com", "mhdb": "manhuadb.com", "mhg": "mhgui.com",
          "mhgm": "manhuagui.com", "mhm": "maofly.com", "nh": "nhentai.net",
          "pica": "picacomic.com", "rm5": "rouman5.com"}
    for k, v in MR.items():
        recs.append(("mangareader", k, norm(v), "zh", ""))
    return recs


def score_of(m, is_zh, official):
    """质量评分（满分 100）。"""
    s = {4: 30, 3: 24, 2: 16}.get(m["eco_count"], 6)
    if official:
        s += 25
    if is_zh:
        s += 20
    if set(m["ecosystems"]) & ACTIVE_ECO:
        s += 12
    if set(m["ecosystems"]) & ARCHIVED_ECO:
        s -= 6
    if m["nsfw"]:
        s -= 12
    return max(0, min(100, s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--venera", default="", help="02-可用源 目录，用于判定「已有实现」")
    a = ap.parse_args()

    vset = load_venera_names(a.venera) if a.venera else set()
    recs = collect(a.raw)
    print(f"原始源记录: {len(recs)}")
    if vset:
        print(f"已有 Venera 实现（源名）: {len(vset)}")

    bydom, nodom = defaultdict(list), []
    for eco, name, dom, lang, nsfw in recs:
        (bydom[dom] if dom else nodom).append((eco, name, lang, nsfw))
    print(f"唯一域名: {len(bydom)}   无域名记录: {len(nodom)}")

    # ---- 去重主表 ----
    master = {}
    for d, v in bydom.items():
        ecos = sorted({e for e, *_ in v})
        langs = {str(l).lower() for _, _, l, _ in v if l}
        master[d] = {
            "domain": d,
            "ecosystems": ecos,
            "eco_count": len(ecos),
            "names": sorted({n for _, n, _, _ in v if n}),
            "langs": sorted(langs),
            "nsfw": any(s for _, _, _, s in v),
        }

    # ---- 全量评分 + 中文判定 ----
    all_rows, zh_rows = [], []
    for d, m in master.items():
        ecos, names = set(m["ecosystems"]), m["names"]
        is_zh = (bool(set(m["langs"]) & ZH_LANG) or bool(ecos & ZH_ECO)
                 or any(CJK.search(n) for n in names))
        official = OFFICIAL.get(d, "")
        effort = "已有实现" if has_impl(names, vset) else "需新写"
        row = {
            "domain": d, "score": score_of(m, is_zh, official),
            "tier": "", "ecosystems": m["ecosystems"], "eco_count": m["eco_count"],
            "is_zh": is_zh, "official": official, "nsfw": m["nsfw"],
            "names": names[:4], "langs": m["langs"], "effort": effort,
        }
        all_rows.append(row)
        if is_zh:
            zh_rows.append(row)

    # 中文源按分位数定质量层（T1 前 15% / T2 到 50% / T3 其余）
    zh_rows.sort(key=lambda r: (-r["score"], r["domain"]))
    n = len(zh_rows)
    q1, q2 = int(n * 0.15), int(n * 0.50)
    for i, r in enumerate(zh_rows):
        r["tier"] = "T1" if i < q1 else ("T2" if i < q2 else "T3")
    # 非中文行用中文源的分位分数界线定层，保证两份文件口径一致
    cut1 = zh_rows[q1]["score"] if q1 < n else 0
    cut2 = zh_rows[q2]["score"] if q2 < n else 0
    for r in all_rows:
        if not r["is_zh"]:
            r["tier"] = "T1" if r["score"] >= cut1 else ("T2" if r["score"] >= cut2 else "T3")
    all_rows.sort(key=lambda r: (-r["is_zh"], -r["score"], r["domain"]))

    # ---- 输出 ----
    for sub in ("01-去重主表", "02-质量评分", "03-中文优先"):
        os.makedirs(os.path.join(a.outdir, sub), exist_ok=True)

    json.dump({"domains": {d: m for d, m in master.items()},
               "no_domain": [{"ecosystem": e, "name": n2} for e, n2, _, _ in nodom]},
              open(os.path.join(a.outdir, "01-去重主表/去重主表.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    with open(os.path.join(a.outdir, "01-去重主表/去重主表.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["domain", "ecosystems", "names", "eco_count", "record_count"])
        for d, m in sorted(master.items()):
            w.writerow([d, "|".join(m["ecosystems"]), "|".join(m["names"])[:300],
                        m["eco_count"], sum(1 for _, _, dd, _, _ in recs if dd == d)])

    json.dump({"all": all_rows, "zh": zh_rows},
              open(os.path.join(a.outdir, "02-质量评分/全量评分表.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    with open(os.path.join(a.outdir, "02-质量评分/全量评分表.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["domain", "score", "tier", "is_zh", "official", "nsfw", "eco_count",
                    "effort", "ecosystems", "names", "langs"])
        for r in all_rows:
            w.writerow([r["domain"], r["score"], r["tier"], int(r["is_zh"]), r["official"],
                        int(r["nsfw"]), r["eco_count"], r["effort"],
                        "|".join(r["ecosystems"]), "|".join(r["names"])[:200],
                        "|".join(r["langs"])])

    json.dump(zh_rows, open(os.path.join(a.outdir, "03-中文优先/中文优先清单.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(a.outdir, "03-中文优先/中文优先清单.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["rank", "domain", "score", "tier", "official", "nsfw", "eco_count",
                    "ecosystems", "names", "langs", "effort"])
        for i, r in enumerate(zh_rows, 1):
            w.writerow([i, r["domain"], r["score"], r["tier"], r["official"], int(r["nsfw"]),
                        r["eco_count"], "|".join(r["ecosystems"]), "|".join(r["names"])[:200],
                        "|".join(r["langs"]), r["effort"]])

    from collections import Counter
    print(f"去重主表 {len(master)} 站   全量评分 {len(all_rows)} 行   中文源 {len(zh_rows)} 站")
    print(f"  中文源质量层: {dict(Counter(r['tier'] for r in zh_rows))}")
    print(f"  适配工作量:   {dict(Counter(r['effort'] for r in zh_rows))}")
    print(f"  官方正版命中: {sum(1 for r in zh_rows if r['official'])}")
    print(f"输出到 {a.outdir}/01-去重主表、02-质量评分、03-中文优先")


if __name__ == "__main__":
    main()
