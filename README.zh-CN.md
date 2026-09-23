# 开源漫画源清单

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Sources](https://img.shields.io/badge/sources-3126%20records%20%2F%201593%20sites-blue.svg)](#数据规模)
[![Chinese](https://img.shields.io/badge/chinese%20sources-256-red.svg)](#数据规模)

**简体中文** | [English](README.md)

> ### 📱 只想在手机上看漫画？
> **[→ 从 START-HERE.zh-CN.md 开始](START-HERE.zh-CN.md)** —— 三步搞定，五分钟，不用代码、
> 不用 clone、不用往手机拷文件。往 Venera 里粘一个地址，按质量档位挑源就行。
>
> 下面这些是本仓库的数据与工程部分，纯粹为了看漫画的话**都不需要看**。

跨生态汇总、去重、评分、分档的漫画源清单数据集。

把 **7 个主流开源漫画阅读器生态**的源定义收集到一起，按**站点域名**归一化去重，
再按质量评分和三档分级。每一层都提供「跨生态去重总表 + 按生态拆分表」，
方便按生态溯源，也方便按目标格式二次适配。

> 只有数据。本仓库只索引**公开的源元信息**（站点域名、名称、所属生态），不托管任何漫画内容。

## 数据规模

| 类别 | 源记录 | 说明 |
|---|---|---|
| 所有生态 · 所有源 | **3126 条** → 去重后 **1593 个唯一站点** | 7 个生态的全量 |
| 所有生态 · 中文源 | **593 条** → 去重后 **256 个唯一站点** | 中文向 |
| 所有生态 · 三档源 | 一档 32 · 二档 115 · 三档 102 · 已废 7 | 中文源按可用性与延迟分档 |

> 注：`05-venera.csv` 与 `06-cimoc.csv` 的条数是各源仓库/配置的**原始记录数**，
> 同一源可能出现在多个社区仓库中，故会大于去重后数量。

## 目录结构

> 仓库内目录名、文件名、表头、枚举值**全部为英文**；只有源名（`names` / `source_name`）
> 保留原始写法（中/日文），因为那是各生态内部的标识符。

```
01-all-sources/                          所有生态 · 所有源
├── 00-deduplicated-master.csv / .json   1593 个唯一站点（含排名与评分）
├── 01-mihon-family.csv                  2372 条
├── 02-aidoku.csv                        136 条
├── 03-kotatsu.csv                       137 条
├── 04-legado.csv                        182 条
├── 05-venera.csv                        204 条
├── 06-cimoc.csv                         81 条
└── 07-mangareader.csv                   14 条

02-chinese-sources/                      所有生态 · 中文源
├── 00-deduplicated-master.csv / .json   256 个唯一站点（含排名与评分）
├── 01-mihon-family.csv                  88 条
├── 02-aidoku.csv                        21 条
├── 03-kotatsu.csv                       3 条
├── 04-legado.csv                        182 条
├── 05-venera.csv                        204 条
├── 06-cimoc.csv                         81 条
└── 07-mangareader.csv                   14 条

03-tiered-sources/                       所有生态 · 三档源
├── tier1-primary/     00-full-list.csv 32 条  +  by-ecosystem/*.csv
├── tier2-backup/      00-full-list.csv 115 条 +  by-ecosystem/*.csv
├── tier3-retest/      00-full-list.csv 102 条 +  by-ecosystem/*.csv
├── dead-skip/         00-full-list.csv 7 条   +  by-ecosystem/*.csv
└── tier1-2-selection.csv / .json        147 条（一档 + 二档）

04-tools/                                可复现流水线
├── rebuild_all.py        一键跑完整条流水线（--skip-network 可离线）
├── source_utils.py       共享函数：域名归一化 norm()、源名折叠 fold_name()
├── rebuild_index.py      原始提取结果 → 去重主表 + 全量评分表 + 中文优先清单
├── check_connectivity.py 并发探测站点存活与延迟
├── build_tiers.py        按可用性与延迟分档
├── build_repo.py         生成本仓库的数据目录（唯一的中→英导出层）
└── build_phone_sources.py 生成手机上用的 Venera 源分档目录

05-venera-sources/                       可直接导入的 Venera 源列表
├── sources/*.js                         79 个可用的 Venera 源文件
├── all/index.json                       全部 79 个，按 tier1 → tier2 → tier3 → extra 排序
├── tier1/index.json                     19 个
├── tier2/index.json                     33 个
├── tier3/index.json                     26 个
├── extra/index.json                     1 个（不在中文三档内）
├── by-ecosystem/<生态>/index.json        同一批源按生态筛选
├── by-ecosystem/<生态>/<档位>/index.json … 以及生态 × 档位
├── files.txt / files.json               每个源文件的直接地址
├── venera-import.json                   配置文件：可直接粘贴的 URL + 说明
└── urls.txt                             纯 URL 清单
```

## 字段说明

### 去重总表（`00-deduplicated-master.csv`）

| 字段 | 含义 |
|---|---|
| `rank` | 表内排名（中文源优先，再按评分降序） |
| `domain` | 归一化后的站点域名（去协议、去 `www/m/mobile/cn/app` 前缀、去端口/路径/查询串），**去重主键** |
| `is_chinese` | 是否判定为中文向，`1`/`0` |
| `score` | 质量评分，0–100 |
| `tier` | 质量层 `T1`/`T2`/`T3`（在中文源内按分位数） |
| `official` | 已知的官方正版/授权站点名称，空表示非官方 |
| `nsfw` | 是否成人向 |
| `eco_count` | 被多少个生态收录（越多说明站点越稳定、内容量越大） |
| `effort` | 适配工作量：`existing` = Venera 已有现成源 · `to-build` = 需新写 |
| `ecosystems` | 收录该站点的生态，`\|` 分隔 |
| `names` | 各生态里该站点的源名称（保留原始写法） |
| `langs` | 该站点出现过的语言标记 |

### 按生态拆分表（`01-*.csv` … `07-*.csv`）

| 字段 | 含义 |
|---|---|
| `ecosystem` | 生态显示名 |
| `source_name` | 该生态里的源名称 |
| `domain` | 归一化域名（Kotatsu 未提取域名，此列为空） |
| `language` | 源的语言标记 |
| `nsfw` | 该源所在扩展的内容分级 |
| `identifier` | 该生态内的唯一标识（Mihon 为扩展包名、Aidoku 为源目录名、Cimoc 为源 KEY、Legado 为书源分组 等） |

### 三档表（`00-full-list.csv`、`tier1-2-selection.csv`）

在总表字段基础上增加：

| 字段 | 含义 |
|---|---|
| `tier` | `tier1-primary` / `tier2-backup` / `tier3-retest` / `dead-skip`（仅出现在精选表） |
| `rank` | 档内按延迟升序的名次 |
| `subclass` | `B-reachable`（正常可达）· `A-bot-blocked (alive)`（反爬拦截，活着）· `C-timeout (retest)`（超时）· `C-proxy-or-gateway-error (retest)`（代理/网关错误）· `D-http-error (possibly redesigned)`（HTTP 错误，可能改版）· `E-other-failure`（其他失败）· `F-dns-failure (dead)` / `F-tls-failure (dead)`（DNS/TLS 失败，已废） |
| `latency_ms` / `speed` | 首页响应耗时；`fast` <400ms · `mid` 400–1200ms · `slow` >1200ms |
| `http_status` | 最近一次探测的 HTTP 状态码 |
| `quality_score` / `quality_tier` | 同总表的 `score` / `tier` |
| `effort` | `existing` / `to-build` |
| `ecosystem_count` / `ecosystems` | 被多少个 / 哪些生态收录 |
| `source_names` | 该站点在各生态的源名称 |

## 各生态来源

| 生态 | 源记录 | 索引来源 |
|---|---|---|
| Mihon 系 | 2372 | `keiyoushi/extensions` 的 `index.json`（Mihon / Tachiyomi / Suwayomi / Komikku / Neko 共用） |
| Legado（阅读） | 182 | `aoaostar/legado` 的 `sources/*.json`，仅取 `bookSourceGroup` 含「漫画」的条目 |
| Kotatsu | 137 | `KotatsuApp/kotatsu-parsers` 解析器类清单 |
| Aidoku | 136 | `aidoku-community/sources`，域名取自各源 `src/lib.rs` 的 `BASE_URL` 常量 |
| Venera | 204 | `venera-app/venera-configs` 及 5 个社区源仓库（原始记录数，含跨仓库重复） |
| Cimoc | 81 | `cimoc.top/cimoc/sourc` 的 `sourceBaseUrl.json` |
| MangaReader | 14 | `youniaogu/MangaReader` 的 `src/plugins/*.ts` |

## 处理口径

### 去重

**按站点域名去重，不按源名或 ID。**

Tachiyomi 系（Mihon）的索引里，同一个站点会**按语言重复展开**：
字段结构是 `{id, name, language, homeUrl}`，例如 `xcomic.me` 有 109 个语言条目、
`mangadex.org` 有 61 个、多语言站普遍有几十到上百条。
2372 条按 `homeUrl` 去重后只剩 1437 个，再归一化域名后为 1413 个。
**按 name 或 id 去重会严重重复计数。**

另注：`komikku-app/extensions` 是 `keiyoushi/extensions` 的镜像
（1396 扩展 / 2372 源，逐条比对 2371/2372 完全一致），已合并为一个生态，不重复统计。

### 质量评分（满分 100）

| 维度 | 分值 |
|---|---|
| 跨生态收录 | 4 个生态 +30 / 3 个 +24 / 2 个 +16 / 1 个 +6 |
| 官方正版授权站 | +25 |
| 中文向 | +20 |
| 来自活跃维护的生态 | +12 |
| 来自已归档生态（Kotatsu） | −6 |
| NSFW | −12 |

中文向判定：`language` 属于 zh 系列 ∪ 生态属于 Cimoc/Venera/Legado/MangaReader（天然中文向）
∪ 源名含中日文字符。

### 三档规则

先按可用性与质量定档，**档内按延迟升序**，同延迟再按质量分降序。

| 档位 | 规则 |
|---|---|
| `tier1-primary`（一档-首用） | HTTP 200 可达，且（官方正版 或 跨生态收录 或 质量分 ≥ 46） |
| `tier2-backup`（二档-备用） | HTTP 200 可达，但为单生态小站 |
| `tier3-retest`（三档-待复测） | 反爬 403/503、超时、代理网关错误、HTTP 4xx |
| `dead-skip`（已废） | DNS 解析失败或 TLS 握手失败，不建议投入 |

### 连通性检测

`04-tools/check_connectivity.py` 并发探测每个域名的 `https://` 与 `http://` 首页，
记录状态码、延迟、页面标题，并粗判是否为漫画站。

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

**重要：连通性结果与网络环境强相关。**
非中国大陆网络下大量中文站会超时；经代理时部分站点会被网关返回 502。
这两类都不代表站点本身失效，建议在**目标使用环境**下重测后再定档。
经验数据：两轮同环境检测的存活数为 161 / 160（共 256），只差 1 个，结果稳定可信。

## 导入到 Venera

`05-venera-sources/` 是**打包好、可直接导入**的 Venera 源列表 —— 不用 clone、不用拷文件。
往 App 里粘一个 URL，源就会列出来，一个个 Add 即可。

**操作步骤**

1. 打开 Venera → **漫画源** → 进 **Comic Source**（源列表）
2. 把下面任一 URL 粘进 **Repo URL** 输入框
3. 点 **Refresh**，列表加载出来
4. 想导哪个就点那条右侧的 **Add**（已装的会显示勾）

| 列表 | 源数 | URL |
|---|---|---|
| 全部（按档位排序） | 79 | `https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/all/index.json` |
| `tier1-primary` 一档 | 19 | `.../05-venera-sources/tier1/index.json` |
| `tier2-backup` 二档 | 33 | `.../05-venera-sources/tier2/index.json` |
| `tier3-retest` 三档 | 26 | `.../05-venera-sources/tier3/index.json` |
| `extra` 未定档 | 1 | `.../05-venera-sources/extra/index.json` |

完整可复制的地址见 [`05-venera-sources/urls.txt`](05-venera-sources/urls.txt)，
机器可读版见 [`venera-import.json`](05-venera-sources/venera-import.json)。

**要知道的几点**

- App 只存**一个** Repo URL —— 想换档位就换 URL 再 Refresh。
- 每个源的名称下方会显示**档位、探测延迟、收录生态数**（走的是 `description` 字段），
  所以在全量列表里可以直接按眼睛挑。
- 每个列表有三种地址形式，都在 `urls.txt` 里：**`@main`**（主用）、
  **`@<commit-sha>`**（内容不可变，绕开 jsDelivr 的分支缓存，想立刻拿到当前快照时用）、
  以及 `raw.githubusercontent.com`（部分网络含中国大陆会超时，仅作最后备选）。
- 所有源的 `minAppVersion` 都 ≤ 1.6.0，Venera 1.6.x 都能加载（含已归档的 1.6.3；
  Venera Prime 比这个要求更新）。
- 列表里含成人向源，不需要的在 App 里单独关掉。

### 为什么不用拷文件也能用

Venera 解析列表条目的逻辑是（见 `comic_source_page.dart`）：条目的 `url` 字段若是合法绝对
地址就直接用，否则拿列表自己的目录去拼 `fileName`。所以
`05-venera-sources/*/index.json` 里**每条都写了绝对 `url`**，79 个 js 因此只需在 `sources/`
放一份，不必按档位复制多份。

## 已知情况

- **域名归一化**：会剥掉协议、`www/m/mobile/cn/app` 前缀、端口、路径与查询串，并清洗脏尾巴；
  CDN 地址（jsDelivr、raw.githubusercontent 等）不作为站点域名。
- **Kotatsu 未提取域名**：其 137 个源是解析器类，域名需逐个解析 Kotlin 源码，暂未补全。
- **反爬站点**：约 12 个高质量站在裸请求下返回 403/503（Cloudflare 等），
  它们并未失效，适配时带上 `Referer` / `Cookie` 或走浏览器内核即可。
- **成人向内容**：中文源 256 个中 40 个标记为 NSFW，可按 `nsfw` 字段过滤。
- **CDN 地址已全部排除**：Venera 源 js 里的 `url` 字段是源的**更新地址**
  （`cdn.jsdelivr.net/...`），不是站点域名；早期版本误把它当站点域，
  导致数十个源被折叠成同一个假站点。现已由 `source_utils.norm()` 统一排除。
- **适配工作量**（`effort` 字段）：中文源 256 个中 **95 个已有现成 Venera 实现**
  （装上即可用），**161 个需新写**。
- **源名不翻译**：`names` / `source_name` 保留原始写法（常为中文或日文），
  它们是各生态内部用于标识源的名称，翻译后会失去对应关系。

## 免责声明

本项目**仅汇总公开的源定义元信息**（站点域名、名称、所属生态），
**不托管、不分发、不镜像任何漫画内容**，也不包含任何破解或绕过付费的实现代码。

清单中的站点绝大多数为第三方非官方站点。使用者应自行确认：
- 遵守所在地法律法规；
- 遵守各目标站点的服务条款与 `robots.txt`；
- 优先通过官方正版渠道支持作者与出版方。

因使用本清单产生的任何后果由使用者自行承担。

## 许可

本项目**数据整理成果**以 **MIT** 协议开源，见 [LICENSE](LICENSE)。

**上游数据不属于本项目**：各源定义的原版权归各自项目所有，
本项目仅对其做汇总、归一化与去重。再次分发请保留来源标注，并遵守上游协议：

- keiyoushi/extensions、komikku-app/extensions — Apache-2.0
- aoaostar/legado、gedoor/legado — GPL-3.0
- aidoku-community/sources — MIT
- KotatsuApp/kotatsu-parsers — Apache-2.0
- venera-app/venera-configs — MIT
- cimoc 相关 — 见原作者声明
- youniaogu/MangaReader — MIT

如有上游项目认为本项目对其数据的收录方式不妥，提 issue 即可，会立即处理。
