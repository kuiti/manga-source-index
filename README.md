# Open Manga Source Index

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Sources](https://img.shields.io/badge/sources-3126%20records%20%2F%201593%20sites-blue.svg)](#data-scale)
[![Chinese](https://img.shields.io/badge/chinese%20sources-256-red.svg)](#data-scale)

[简体中文](README.zh-CN.md) | **English**

> ### 📱 Just want to read manga on your phone?
> **[→ START-HERE.md](START-HERE.md)** — three steps, five minutes. No code, no cloning,
> no copying files. Paste one URL into the Venera app and pick sources by quality tier.
>
> Everything below is the data/engineering side of this repo; you don't need any of it to read manga.

A cross-ecosystem, deduplicated, scored and tier-ranked dataset of manga/comic source definitions.

Source definitions are aggregated from **7 mainstream open-source manga reader ecosystems**, normalized and deduplicated by **site domain**, then scored for quality and ranked into three tiers. Every layer ships both a **cross-ecosystem deduplicated table** and **per-ecosystem breakdown tables**, so you can trace provenance by ecosystem or re-target the data into your own format.

> Data only. This repository indexes **public source metadata** (site domains, names, owning ecosystem). It hosts no manga content.

## Data scale

| Category | Source records | Description |
|---|---|---|
| All ecosystems · all sources | **3126** → **1593 unique sites** after dedup | Full coverage of the 7 ecosystems |
| All ecosystems · Chinese sources | **593** → **256 unique sites** after dedup | Chinese-oriented |
| All ecosystems · 3-tier sources | tier1 32 · tier2 115 · tier3 102 · dead 7 | Chinese sources ranked by availability and latency |

> Note: the record counts for `05-venera.csv` and `06-cimoc.csv` are **raw records** from their source repos/configs. The same source may appear in several community repos, so these counts exceed the deduplicated totals.

## Directory structure

```
01-all-sources/                          every source, all 7 ecosystems
├── 00-deduplicated-master.csv / .json   1593 unique sites, ranked + scored
├── 01-mihon-family.csv                  2372 records
├── 02-aidoku.csv                        136 records
├── 03-kotatsu.csv                       137 records
├── 04-legado.csv                        182 records
├── 05-venera.csv                        204 records
├── 06-cimoc.csv                         81 records
└── 07-mangareader.csv                   14 records

02-chinese-sources/                      Chinese-oriented sources only
├── 00-deduplicated-master.csv / .json   256 unique sites, ranked + scored
├── 01-mihon-family.csv                  88 records
├── 02-aidoku.csv                        21 records
├── 03-kotatsu.csv                       3 records
├── 04-legado.csv                        182 records
├── 05-venera.csv                        204 records
├── 06-cimoc.csv                         81 records
└── 07-mangareader.csv                   14 records

03-tiered-sources/                       Chinese sources split by tier
├── tier1-primary/     00-full-list.csv 32 rows  +  by-ecosystem/*.csv
├── tier2-backup/      00-full-list.csv 115 rows +  by-ecosystem/*.csv
├── tier3-retest/      00-full-list.csv 102 rows +  by-ecosystem/*.csv
├── dead-skip/         00-full-list.csv 7 rows   +  by-ecosystem/*.csv
└── tier1-2-selection.csv / .json        147 rows (tier1 + tier2 combined)

04-tools/                                reproducible pipeline
├── rebuild_all.py        run the whole pipeline in one command (--skip-network to stay offline)
├── source_utils.py       shared helpers: domain normalization norm(), name folding fold_name()
├── rebuild_index.py      raw extracts → master table + scored table + Chinese list
├── check_connectivity.py concurrent liveness / latency probe
├── build_tiers.py        tier assignment by availability and latency
├── build_repo.py         builds this repository's data tree
└── build_phone_sources.py builds an on-device Venera source tree by tier

05-venera-sources/                       ready-to-import Venera source lists
├── sources/*.js                         80 working Venera source files
├── sources/index.json                   all 80 in **exact official format** (see below)
├── sources/index-<tier>.json            official format, per tier
├── sources/index-eco-<eco>.json         official format, per ecosystem
├── all/index.json                       all 80, sorted tier1 → tier2 → tier3 → extra
├── tier1/index.json                     19 sources
├── tier2/index.json                     33 sources
├── tier3/index.json                     27 sources
├── extra/index.json                     1 source (not in the Chinese tiers)
├── by-ecosystem/<eco>/index.json        same sources filtered by ecosystem
├── by-ecosystem/<eco>/<tier>/index.json … and by ecosystem × tier
├── files.txt / files.json               a direct URL for every single source file
├── venera-import.json                   config file: the paste-ready URLs, with notes
└── urls.txt                             plain URL list
```

**Coverage:** the list is a strict **superset of Venera's own `venera-configs`** —
all **33/33** official source files are present, plus 47 more (80 total).

## Field reference

### Deduplicated master table (`00-deduplicated-master.csv`)

| Field | Meaning |
|---|---|
| `rank` | Rank within the table (Chinese sources first, then descending score) |
| `domain` | Normalized site domain (protocol, `www/m/mobile/cn/app` prefix, port, path and query stripped). **Dedup primary key.** |
| `is_chinese` | `1` if classified as Chinese-oriented |
| `score` | Quality score, 0–100 |
| `tier` | Quality tier T1/T2/T3 (by quantile among Chinese sources) |
| `official` | Known official/licensed site name; empty means unofficial |
| `nsfw` | Adult content flag |
| `eco_count` | How many ecosystems index it (higher = more stable, larger catalog) |
| `effort` | Migration effort: `existing` = a working Venera source already exists · `to-build` = must be written |
| `ecosystems` | Ecosystems that index this site, `\|`-separated |
| `names` | Source names this site is known by, per ecosystem (original spelling, may be Chinese) |
| `langs` | Language tags seen for this site |

### Per-ecosystem tables (`01-*.csv` … `07-*.csv`)

| Field | Meaning |
|---|---|
| `ecosystem` | Ecosystem display name |
| `source_name` | Source name within that ecosystem |
| `domain` | Normalized domain (Kotatsu domains not yet extracted — column is empty) |
| `language` | Language tag of the source |
| `nsfw` | Content rating of the extension the source belongs to |
| `identifier` | Unique identifier inside that ecosystem (Mihon: extension package name · Aidoku: source directory name · Cimoc: source KEY · Legado: book-source group, etc.) |

### 3-tier tables (`00-full-list.csv`, `tier1-2-selection.csv`)

All master fields, plus:

| Field | Meaning |
|---|---|
| `tier` | `tier1-primary` · `tier2-backup` · `tier3-retest` · `dead-skip` (present in the selection file only) |
| `rank` | Rank within the tier, ascending by latency |
| `subclass` | `B-reachable` · `A-bot-blocked (alive)` · `C-timeout (retest)` · `C-proxy-or-gateway-error (retest)` · `D-http-error (possibly redesigned)` · `E-other-failure` · `F-dns-failure (dead)` · `F-tls-failure (dead)` |
| `latency_ms` / `speed` | Homepage response time; `fast` &lt;400ms · `mid` 400–1200ms · `slow` &gt;1200ms |
| `http_status` | HTTP status of the last probe |
| `quality_score` / `quality_tier` | Same as `score` / `tier` above |
| `effort` | `existing` / `to-build` |
| `ecosystem_count` / `ecosystems` | How many / which ecosystems index this site |
| `source_names` | Source names across ecosystems |

## Ecosystem sources

| Ecosystem | Records | Index source |
|---|---|---|
| Mihon family | 2372 | `index.json` from `keiyoushi/extensions` (shared by Mihon / Tachiyomi / Suwayomi / Komikku / Neko) |
| Legado (阅读) | 182 | `sources/*.json` from `aoaostar/legado`, filtered to entries whose `bookSourceGroup` contains `漫画` |
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
Cimoc/Venera/Legado/MangaReader (Chinese-oriented by nature) ∪ source name containing CJK characters.

### Tier rules

Tier is assigned from availability and quality first; **within a tier, sorting is ascending
by latency**, ties broken by descending quality score.

| Tier | Rule |
|---|---|
| `tier1-primary` | HTTP 200 reachable, and (official · indexed by multiple ecosystems · score ≥ 46) |
| `tier2-backup` | HTTP 200 reachable, but a single-ecosystem site |
| `tier3-retest` | Bot-blocked 403/503, timeout, proxy/gateway error, HTTP 4xx |
| `dead-skip` | DNS resolution or TLS handshake failure — not worth pursuing |

### Connectivity probe

`04-tools/check_connectivity.py` concurrently probes each domain's `https://` and `http://`
homepage, recording status code, latency and page title, and heuristically flagging manga sites.

```bash
python 04-tools/check_connectivity.py --input 02-chinese-sources/00-deduplicated-master.json --tag local --workers 30
python 04-tools/check_connectivity.py --input 02-chinese-sources/00-deduplicated-master.json --tag proxy --workers 30
python 04-tools/check_connectivity.py --input 02-chinese-sources/00-deduplicated-master.json --tag direct --no-proxy
```

```bash
python 04-tools/build_tiers.py \
    --sources 02-chinese-sources/00-deduplicated-master.json \
    --connectivity connectivity_local.json \
    --outdir 03-tiered-sources --prefix tiers
```

**Important: connectivity results depend heavily on the network environment.**
Outside mainland China many Chinese sites time out; behind a proxy some sites get a 502 from the
gateway. Neither means the site is dead — re-test in your **target environment** before finalizing
tiers. Reference data: two runs in the same environment found 161 / 160 alive out of 256 — a
difference of just 1, so results are stable and trustworthy.

## Import the sources into Venera

`05-venera-sources/` is a **ready-to-import** Venera source list — no cloning, no file copying.
Paste one URL into the app and the sources show up as a list you can add one by one.

**Steps**

1. Open Venera → **Comic Source** (漫画源) → the **Comic Source** entry (源列表)
2. Paste one of the URLs below into the **Repo URL** field
3. Tap **Refresh** — the list loads
4. Tap **Add** on each source you want (sources already installed show a check mark)

| List | Sources | URL |
|---|---|---|
| All (sorted by tier) | 79 | `https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/all/index.json` |
| `tier1-primary` | 19 | `.../05-venera-sources/tier1/index.json` |
| `tier2-backup` | 33 | `.../05-venera-sources/tier2/index.json` |
| `tier3-retest` | 26 | `.../05-venera-sources/tier3/index.json` |
| `extra` (not in Chinese tiers) | 1 | `.../05-venera-sources/extra/index.json` |

The full list, ready to copy, is in [`05-venera-sources/urls.txt`](05-venera-sources/urls.txt)
and machine-readable in [`venera-import.json`](05-venera-sources/venera-import.json).

**Things to know**

- The app stores **one** Repo URL at a time — to switch tiers, just replace the URL and Refresh.
- Every entry shows its tier, probe latency and ecosystem count **under the source name**
  (that's the `description` field), so you can pick by eye in the all-list.
- Each list comes in three URL forms, all in `urls.txt`: **`@main`** (primary),
  **`@<commit-sha>`** (immutable — bypasses jsDelivr's branch cache when you need the exact
  snapshot now), and `raw.githubusercontent.com` (times out on some networks including
  mainland China — last resort only).
- All sources declare `minAppVersion` ≤ 1.6.0, so they load on Venera 1.6.x
  (including the archived 1.6.3; Venera Prime is newer than that requirement).
- Adult sources are included — disable the ones you don't want inside the app.

### Why it works without copying files

Venera resolves each list entry like this (see `comic_source_page.dart`): use the entry's `url`
field when it is a valid absolute URL, otherwise resolve `fileName` against the list's own
directory. `05-venera-sources/*/index.json` therefore carries an **absolute `url` per entry**,
which is why all 80 JS files can live once in `sources/` instead of being duplicated per tier.

### Official-format lists

If you need a list whose entries look **exactly** like Venera's own `venera-configs`
(`{name, key, version, fileName}` — no extra fields):

```
https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/sources/index.json
```

Per-tier and per-ecosystem variants sit beside it as `index-tier1.json`, `index-eco-mihon.json`, …

Two consequences of the strict format worth knowing:

1. **They must live next to the JS files.** The official format has no `url` field, so the app
   can only resolve `fileName` against the list URL's own directory — hence `sources/index.json`
   sits *inside* `sources/`.
2. **No tier hints in the app.** Tier/latency live in the `description` field, which the strict
   format drops. For everyday use prefer the rich lists (`all/`, `tier1/`, …).

Our entries are also a compatible **superset** of the official format: the rich lists carry all
four official fields plus extras, and Venera ignores what it doesn't know.

## Known caveats

- **Domain normalization** strips protocol, `www/m/mobile/cn/app` prefixes, port, path and query,
  and cleans dirty suffixes. CDN addresses (jsDelivr, raw.githubusercontent, …) are never treated
  as site domains.
- **Kotatsu domains not extracted yet**: its 137 sources are parser classes; domains require
  parsing Kotlin sources one by one, not done yet.
- **Bot-blocked sites**: about 12 high-quality sites return 403/503 to bare requests
  (Cloudflare and friends). They are not dead — send `Referer` / `Cookie` or use a browser engine.
- **Adult content**: 40 of the 256 Chinese sites are flagged NSFW; filter on the `nsfw` field.
- **CDN addresses fully excluded**: the `url` field inside Venera source JS files is the source's
  **update address** (`cdn.jsdelivr.net/...`), not a site domain. An early version mistook it for
  one, collapsing dozens of distinct sources into a single fake site. `source_utils.norm()` now
  excludes these uniformly.
- **Migration effort** (`effort` field): of the 256 Chinese sites, **95 already have a working
  Venera source** (install and go) and **161 need to be written**.
- **Source names are not translated**: `names` / `source_name` columns keep the original spelling
  (often Chinese or Japanese), because they are identifiers used inside their own ecosystems.

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
