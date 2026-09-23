# Open Manga Source Index

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Sources](https://img.shields.io/badge/sources-3126%20records%20%2F%201593%20sites-blue.svg)](#data-scale)

[简体中文](README.zh-CN.md) | **English**

A cross-ecosystem, deduplicated, scored and tier-ranked dataset of manga/comic source definitions.

Source definitions are aggregated from **7 mainstream open-source manga reader ecosystems**, normalized and deduplicated by **site domain**, then scored for quality and ranked into three tiers. Every layer ships both a **cross-ecosystem deduplicated table** and **per-ecosystem breakdown tables**, so you can trace provenance by ecosystem or re-target the data into your own format.

> Data only. This repository indexes **public source metadata** (site domains, names, owning ecosystem). It hosts no manga content.

## Data scale

| Category | Source records | Description |
|---|---|---|
| All ecosystems · all sources | **3126** → **1593 unique sites** after dedup | Full coverage of the 7 ecosystems |
| All ecosystems · Chinese sources | **593** → **256 unique sites** after dedup | Chinese-oriented |
| All ecosystems · 3-tier sources | Tier 1: 32 · Tier 2: 115 · Tier 3: 102 · Dead: 7 | Chinese sources ranked by availability and latency |

> Note: the record counts for `05-Venera.csv` and `06-Cimoc.csv` are **raw records** from their source repos/configs. The same source may appear in several community repos, so these counts exceed the deduplicated totals.

## Directory structure

Directory and file names are in Chinese (as the data is Chinese-source-oriented); English glosses are given inline.

```
01-所有生态-所有源/                    01 · all ecosystems / all sources
├── 00-去重总表.csv / .json            deduplicated master table — 1593 unique sites
├── 01-Mihon系.csv                    2372 records
├── 02-Aidoku.csv                     136 records
├── 03-Kotatsu.csv                    137 records
├── 04-阅读Legado.csv                 182 records
├── 05-Venera.csv                     204 records
├── 06-Cimoc.csv                      81 records
└── 07-MangaReader.csv                14 records

02-所有生态-中文源/                    02 · all ecosystems / Chinese sources
├── 00-去重总表.csv / .json            deduplicated master table — 256 unique sites
│                                      (includes quality score and migration effort)
├── 01-Mihon系.csv                    88 records
├── 02-Aidoku.csv                     21 records
├── 03-Kotatsu.csv                    3 records
├── 04-阅读Legado.csv                 182 records
├── 05-Venera.csv                     204 records
├── 06-Cimoc.csv                      81 records
└── 07-MangaReader.csv                14 records

03-所有生态-三档源/                    03 · all ecosystems / 3-tier sources
├── 一档-首用/          Tier 1 – primary  00-本档完整清单.csv 32 rows  +  按生态/*.csv
├── 二档-备用/          Tier 2 – backup   00-本档完整清单.csv 115 rows +  按生态/*.csv
├── 三档-待复测/        Tier 3 – retest   00-本档完整清单.csv 102 rows +  按生态/*.csv
├── 已废-不建议投入/     Dead – skip      00-本档完整清单.csv 7 rows   +  按生态/*.csv
└── 前两档精选.csv / .json             Tier 1 + Tier 2 combined — 147 rows
                                       (按生态/ = per-ecosystem breakdown)

04-工具/                               04 · tooling
├── 全量重建.py          run the whole pipeline end to end (--skip-network for offline)
├── 源工具.py            shared helpers: domain normalization norm(), name folding
├── 重建清单.py          raw extracts → master table + scored table + Chinese list
├── 连通性检测.py        concurrent liveness / latency probe
├── 三档分级.py          tier assignment by availability and latency
├── 开源仓库构建.py      builds this repository's data directories
└── 手机源构建.py        builds an on-device Venera source tree by tier
```

## Field reference

### Deduplicated master table (`00-去重总表.csv`)

| Field | Meaning |
|---|---|
| `domain` | Normalized site domain (protocol, `www/m/mobile/cn/app` prefix, port, path and query stripped). **Dedup primary key.** |
| `ecosystems` | Ecosystems that index this site, `\|`-separated |
| `eco_count` | How many ecosystems index it (higher = more stable, larger catalog) |
| `names` | Source names this site is known by, per ecosystem |
| `score` | Quality score, 0–100 |
| `tier` | Quality tier T1/T2/T3 (by quantile) |
| `official` | Known official/licensed site name; empty means unofficial |
| `nsfw` | Adult content flag |
| `effort` | Migration effort: `已有实现` = a working Venera source already exists / `需新写` = must be written |

### Per-ecosystem tables

| Field | Meaning |
|---|---|
| `生态` | Ecosystem |
| `源名` | Source name within that ecosystem |
| `站点域名` | Normalized domain (Kotatsu domains not yet extracted — column is empty) |
| `语言` | Language tag of the source |
| `NSFW` | Content rating of the extension the source belongs to |
| `标识/包名` | Unique identifier inside that ecosystem (Mihon: extension package name · Aidoku: source directory name · Cimoc: source KEY, etc.) |

### 3-tier tables

All fields above, plus:

| Field | Meaning |
|---|---|
| `档位` | Tier: 一档-首用 (primary) / 二档-备用 (backup) / 三档-待复测 (retest) / 已废-不建议投入 (dead) |
| `档内排名` | Rank within the tier, ascending by latency |
| `子类` | `B-正常可达` (reachable) · `A-反爬拦截(活着)` (bot-blocked but alive) · `C-超时(待复测)` (timeout) · `C-代理/网关错误(待复测)` (proxy/gateway error) · `D-HTTP错误(可能改版)` (HTTP error, possibly redesigned) · `E-其他失败` · `F-DNS/TLS失败(已废)` (DNS/TLS failure) |
| `延迟ms` / `速度` | Homepage response time; 快 &lt;400ms · 中 400–1200ms · 慢 &gt;1200ms |
| `适配工作量` | `已有实现` / `需新写` |
| `收录生态` | Which ecosystems index this site |

## Ecosystem sources

| Ecosystem | Records | Index source |
|---|---|---|
| Mihon family | 2372 | `index.json` from `keiyoushi/extensions` (shared by Mihon / Tachiyomi / Suwayomi / Komikku / Neko) |
| 阅读 Legado | 182 | `sources/*.json` from `aoaostar/legado`, filtered to entries whose `bookSourceGroup` contains "漫画" |
| Kotatsu | 137 | Parser class list from `KotatsuApp/kotatsu-parsers` |
| Aidoku | 136 | `aidoku-community/sources`; domains read from the `BASE_URL` constant in each source's `src/lib.rs` |
| Venera | 204 | `venera-app/venera-configs` plus 5 community source repos (raw records, cross-repo duplicates included) |
| Cimoc | 81 | `sourceBaseUrl.json` from `cimoc.top/cimoc/sourc` |
| MangaReader | 14 | `src/plugins/*.ts` from `youniaogu/MangaReader` |

## Methodology

### Deduplication

**Deduplicated by site domain — not by source name or ID.**

In the Tachiyomi-family (Mihon) index, the same site is **expanded once per language**:
each entry is `{id, name, language, homeUrl}`, so e.g. `xcomic.me` has 109 language entries,
`mangadex.org` has 61, and multilingual sites commonly have dozens to hundreds.
Deduplicating 2372 records by `homeUrl` leaves 1437, and normalizing domains leaves 1413.
**Deduplicating by name or id inflates the count badly.**

Also note: `komikku-app/extensions` is a mirror of `keiyoushi/extensions`
(1396 extensions / 2372 sources, 2371/2372 identical entry by entry), so the two are
merged into a single ecosystem rather than counted twice.

### Quality score (0–100)

| Dimension | Points |
|---|---|
| Cross-ecosystem presence | 4 ecosystems +30 / 3 +24 / 2 +16 / 1 +6 |
| Known official/licensed site | +25 |
| Chinese-oriented | +20 |
| From an actively maintained ecosystem | +12 |
| From an archived ecosystem (Kotatsu) | −6 |
| NSFW | −12 |

Chinese-oriented is determined by: `language` in the `zh` family ∪ ecosystem in
Cimoc/Venera/MangaReader (Chinese-oriented by nature) ∪ source name containing CJK characters.

### Tier rules

Tier is assigned from availability and quality first; **within a tier, sorting is ascending
by latency**, ties broken by descending quality score.

| Tier | Rule |
|---|---|
| 一档-首用 (primary) | HTTP 200 reachable, and (official · indexed by multiple ecosystems · score ≥ 46) |
| 二档-备用 (backup) | HTTP 200 reachable, but a single-ecosystem site |
| 三档-待复测 (retest) | Bot-blocked 403/503, timeout, proxy/gateway error, HTTP 4xx |
| 已废 (dead) | DNS resolution or TLS handshake failure — not worth pursuing |

### Connectivity probe

`04-工具/连通性检测.py` concurrently probes each domain's `https://` and `http://` homepage,
recording status code, latency and page title, and heuristically flagging manga sites.

```bash
python 04-工具/连通性检测.py --input 02-所有生态-中文源/00-去重总表.json --tag local --workers 30
python 04-工具/连通性检测.py --input 02-所有生态-中文源/00-去重总表.json --tag proxy --workers 30
python 04-工具/连通性检测.py --input 02-所有生态-中文源/00-去重总表.json --tag direct --no-proxy
```

```bash
python 04-工具/三档分级.py \
    --sources 02-所有生态-中文源/00-去重总表.json \
    --connectivity connectivity_local.json \
    --outdir 03-所有生态-三档源 --prefix 三档分级清单
```

**Important: connectivity results depend heavily on the network environment.**
Outside mainland China many Chinese sites time out; behind a proxy some sites get a 502 from the
gateway. Neither means the site is dead — re-test in your **target environment** before finalizing
tiers. Reference data: two runs in the same environment found 161 / 160 alive out of 256 — a
difference of just 1, so results are stable and trustworthy.

## Known caveats

- **Domain normalization** strips protocol, `www/m/mobile/cn/app` prefixes, port, path and query,
  and cleans dirty suffixes such as `example.com已整理`. CDN addresses (jsDelivr,
  raw.githubusercontent, …) are never treated as site domains.
- **Kotatsu domains not extracted yet**: its 137 sources are parser classes; domains require
  parsing Kotlin sources one by one, not done yet.
- **Bot-blocked sites**: about 12 high-quality sites return 403/503 to bare requests
  (Cloudflare and friends). They are not dead — send `Referer` / `Cookie` or use a browser engine.
- **Adult content**: 40 of the 256 Chinese sites are flagged NSFW; filter on the `nsfw` field.
- **CDN addresses fully excluded**: the `url` field inside Venera source JS files is the source's
  **update address** (`cdn.jsdelivr.net/...`), not a site domain. An early version mistook it for
  one, collapsing dozens of distinct sources into a single fake site. `源工具.norm()` now excludes
  these uniformly.
- **Migration effort** (`effort` field): of the 256 Chinese sites, **95 already have a working
  Venera source** (install and go) and **161 need to be written**.

## Disclaimer

This project **only aggregates publicly available source metadata** (site domains, names, owning
ecosystem). It **does not host, distribute or mirror any manga content**, and contains no
code that cracks or bypasses paid access.

The overwhelming majority of indexed sites are third-party, unofficial sites. Users must
satisfy themselves that they:
- comply with the laws of their jurisdiction;
- comply with each target site's terms of service and `robots.txt`;
- prefer official, licensed channels to support creators and publishers.

Any consequences of using this dataset are borne by the user.

## License

The **dataset compilation** in this repository is released under the **MIT** license — see
[LICENSE](LICENSE).

**Upstream data is not covered by this license.** Copyright of each source definition belongs to
its original project; this repository only aggregates, normalizes and deduplicates it. If you
redistribute, keep the attribution below and respect the upstream licenses:

- keiyoushi/extensions, komikku-app/extensions — Apache-2.0
- aoaostar/legado, gedoor/legado — GPL-3.0
- aidoku-community/sources — MIT
- KotatsuApp/kotatsu-parsers — Apache-2.0
- venera-app/venera-configs — MIT
- cimoc-related — see the original author's terms
- youniaogu/MangaReader — MIT

If any upstream project considers this repository's inclusion of its data inappropriate, open an
issue and it will be addressed immediately.
