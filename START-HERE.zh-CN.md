# 我只想在手机上看漫画 —— 从这里开始

**不用看代码、不用 clone、不用往手机拷文件。** 照下面三步做，五分钟就能开始看。

> 这个仓库里其他目录（`01-` ~ `05-` 的数据表、脚本）是给开发者和做二次适配的人看的，
> 你只是想看漫画的话**完全不需要碰**。

---

## 三步搞定

### 1. 装 App（安卓）

Venera 是安卓应用，从官方发布页下载安装包：

- **Venera Prime**（推荐，仍在更新）：<https://github.com/venera-app/venera-prime/releases>
- **Venera**（已归档的旧版，本仓库的源同样兼容）：<https://github.com/venera-app/venera/releases>

安装时系统会提示「允许安装未知来源应用」，允许即可。
（iPhone 用不了 Venera，那需要另一套方案。）

### 2. 打开「源列表」

Venera → **漫画源** → 找到 **Comic Source**（源列表）这一项，点进去。

### 3. 粘地址 → 刷新 → 点 Add

把这一条粘进 **Repo URL** 输入框：

```
https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/all/index.json
```

点 **Refresh**，列表就出来了。每个源右边有一个 **Add** 按钮，点一下就把这个源装进去。

**新手直接用这一条就行** —— 它是全部 80 个源，已经按质量排好序（好的在前面）。
每个源的名字下面会有一行小字，比如 `tier1-primary · 110ms · 2 ecosystems`，
那是它的档位、响应速度和被多少个生态收录。看着顺眼就 Add。

---

## 「档位」是什么

我把所有源都实际探测过两轮，按「能不能用 + 快不快」分成四档。人话版本：

| 档位 | 数量 | 人话 |
|---|---|---|
| **一档** `tier1` | 19 | **最稳最快的**。两轮探测都是正常 200，站点也稳定。**先装这一批** |
| **二档** `tier2` | 33 | 能用，但站点小一些，或者只被一个生态收录。一档不够时再来拿 |
| **三档** `tier3` | 27 | **要折腾的**：被反爬拦、或超时、或站点改版了。想碰运气就试 |
| 其他 `extra` | 1 | 没归进上面的（缺域名信息，没法判断） |

**只想装最靠谱的** → 用一档那条地址。
**全都想要** → 用 all 那条。

---

## 地址表（一）：按档位选

一次只能填一个地址，想换档位就把地址换掉再 Refresh。

| 列表 | 源数 | 地址（直接复制） |
|---|---|---|
| 全部 | 80 | `https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/all/index.json` |
| 一档 · 首用 | 19 | `https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/tier1/index.json` |
| 二档 · 备用 | 33 | `https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/tier2/index.json` |
| 三档 · 待复测 | 27 | `https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/tier3/index.json` |
| 其他 · 未定档 | 1 | `https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/extra/index.json` |

---

## 地址表（二）：按生态选

一张源表会被多个阅读器生态同时收录。如果你想「只要那些别的阅读器里也有的站」，
可以按生态筛。下面的地址可以再往下钻一层到具体档位。

| 生态 | 源数 | 全部档 | 一档 | 二档 | 三档 |
|---|---|---|---|---|---|
| Mihon 系 | 23 | [`…/mihon/index.json`](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/mihon/index.json) | [一档](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/mihon/tier1/index.json) | — | [三档](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/mihon/tier3/index.json) |
| Venera | 76 | [`…/venera/index.json`](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/venera/index.json) | [一档](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/venera/tier1/index.json) | [二档](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/venera/tier2/index.json) | [三档](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/venera/tier3/index.json) |
| Cimoc | 12 | [`…/cimoc/index.json`](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/cimoc/index.json) | [一档](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/cimoc/tier1/index.json) | [二档](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/cimoc/tier2/index.json) | [三档](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/cimoc/tier3/index.json) |
| Aidoku（iOS） | 11 | [`…/aidoku/index.json`](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/aidoku/index.json) | [一档](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/aidoku/tier1/index.json) | — | [三档](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/aidoku/tier3/index.json) |
| 阅读 Legado | 4 | [`…/legado/index.json`](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/legado/index.json) | [一档](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/legado/tier1/index.json) | — | — |
| MangaReader | 4 | [`…/mangareader/index.json`](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/mangareader/index.json) | — | — | [三档](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/mangareader/tier3/index.json) |
| 未归类 | 3 | [`…/unmapped/index.json`](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/unmapped/index.json) | — | [二档](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/unmapped/tier2/index.json) | [三档](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/unmapped/tier3/index.json) |

> **这是重叠分类**：一个源覆盖的站点可能同时被好几个生态收录，所以各生态的源数相加会 **大于 80**。
> 这个维度是给「只想要某类站」的人用的，新手忽略它，直接用上面的档位地址就好。

---

## 只想加某一个源

Venera 的源页顶部还有一个单独的 URL 输入框，粘一个 `.js` 地址就能直接加那一个源。

**全部 80 个源的逐条地址**（带档位和延迟）在这两个文件里：

- 人看：[`05-venera-sources/files.txt`](05-venera-sources/files.txt)
- 程序读：[`05-venera-sources/files.json`](05-venera-sources/files.json)

每条地址长这样：

```
https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/sources/mkzhan.js
```

把最后的文件名换掉就是别的源。

---

## 常见问题

| 问题 | 回答 |
|---|---|
| **导进去后搜索没结果 / 打不开** | 那个源挂了或站点改版了。这是常事——源是跟着第三方站点走的。换一个源试，或者等仓库更新 |
| **怎么更新源？** | 把地址重新粘一遍 + Refresh。App 会拿列表里的版本号和已装的对比，有新版会提示 |
| **jsDelivr 地址打不开** | 换 `pinned` 版本（地址见 [`urls.txt`](05-venera-sources/urls.txt)），或在地址里把 `@main` 换成具体 commit 号。`raw.githubusercontent.com` 在家宽下经常超时，别当主用 |
| **列表太长看不过来** | 只用一档那条地址，19 个，看完再考虑加 |
| **有成人内容** | 列表里确实含成人向源（约 40 个站点）。不需要的在 App 的源管理里单独关掉 |
| **会不会有法律问题？** | 见下面免责声明。清单里的站绝大多数是第三方非官方站，用之前自己判断，优先支持正版 |
| **这些数据哪来的？** | 从 7 个开源漫画阅读器生态收集的源定义，去重、评分、实测后分档。**已包含 Venera 官方源列表的全部 33 个源**，另外多了 47 个。细节看 [README.zh-CN.md](README.zh-CN.md) |
| **iPhone 能用吗？** | Venera 是安卓应用，用不了。iOS 那边生态不一样，本仓库有 Aidoku 的源清单数据可以参考 |

---

## 免责声明

本仓库**只整理公开的源元信息**（站点域名、名称、所属生态），**不托管、不分发、不镜像任何漫画内容**。

清单里的站点绝大多数是第三方非官方站点。使用前请自行确认：遵守所在地法律法规、
遵守目标站点的服务条款、尽量通过官方正版渠道支持作者和出版社。
因使用本清单产生的任何后果由使用者自行承担。

---

**上面的数据表、脚本、评分口径** → [README.zh-CN.md](README.zh-CN.md)
**English version** → [START-HERE.md](START-HERE.md)
