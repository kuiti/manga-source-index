# I just want to read manga on my phone — start here

**No code, no cloning, no copying files to your phone.** Three steps, five minutes.

> Everything else in this repository (`01-` … `05-` data tables, scripts) is for developers and
> people re-targeting the data into their own reader. If you just want to read manga, **ignore all of it**.

---

## Three steps

### 1. Install the app (Android)

Venera is an Android app — grab the APK from its official release page:

- **Venera Prime** (recommended, actively maintained): <https://github.com/venera-app/venera-prime/releases>
- **Venera** (archived original; the sources here work on it too): <https://github.com/venera-app/venera/releases>

Android will ask you to allow installing from an unknown source — allow it.
(There is no iOS version; iOS needs a different setup.)

### 2. Open the source list

Venera → **Comic Source** (漫画源) → open the **Comic Source** list entry.

### 3. Paste a URL → Refresh → tap Add

Paste this into the **Repo URL** field:

```
https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/all/index.json
```

Tap **Refresh** and the list appears. Each source has an **Add** button on the right —
tap it to install that source.

**Beginners: just use that one URL.** It is all 79 sources, already sorted best-first.
Under each source name you'll see a line like `tier1-primary · 110ms · 2 ecosystems` —
that's its tier, response time, and how many ecosystems index the site.

---

## What the tiers mean

Every source was probed live, twice, and ranked by "does it work + is it fast". Plain language:

| Tier | Count | Plain language |
|---|---|---|
| **Tier 1** `tier1` | 19 | **Most stable and fastest.** Both probe rounds returned 200. **Start with these** |
| **Tier 2** `tier2` | 33 | Works, but smaller sites or indexed by a single ecosystem. Come back when tier 1 isn't enough |
| **Tier 3** `tier3` | 26 | **Needs patience**: bot-blocked, timing out, or the site was redesigned. Try if you like |
| Extra `extra` | 1 | Not classified above (no domain info to judge) |

**Only want the reliable ones** → use the tier 1 URL.
**Want everything** → use the all URL.

---

## Table 1: by tier

Only one URL can be set at a time — to switch tiers, replace the URL and Refresh.

| List | Sources | URL (copy directly) |
|---|---|---|
| All | 79 | `https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/all/index.json` |
| Tier 1 · primary | 19 | `https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/tier1/index.json` |
| Tier 2 · backup | 33 | `https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/tier2/index.json` |
| Tier 3 · retest | 26 | `https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/tier3/index.json` |
| Extra · unmapped | 1 | `https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/extra/index.json` |

---

## Table 2: by ecosystem

Most sites are indexed by several reader ecosystems at once. If you specifically want
"only sites that other readers also list", filter by ecosystem — each one also drills down to a tier.

| Ecosystem | Sources | All tiers | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|---|---|
| Mihon family | 23 | [`…/mihon/index.json`](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/mihon/index.json) | [t1](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/mihon/tier1/index.json) | — | [t3](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/mihon/tier3/index.json) |
| Venera | 75 | [`…/venera/index.json`](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/venera/index.json) | [t1](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/venera/tier1/index.json) | [t2](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/venera/tier2/index.json) | [t3](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/venera/tier3/index.json) |
| Cimoc | 12 | [`…/cimoc/index.json`](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/cimoc/index.json) | [t1](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/cimoc/tier1/index.json) | [t2](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/cimoc/tier2/index.json) | [t3](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/cimoc/tier3/index.json) |
| Aidoku (iOS) | 11 | [`…/aidoku/index.json`](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/aidoku/index.json) | [t1](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/aidoku/tier1/index.json) | — | [t3](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/aidoku/tier3/index.json) |
| Legado (阅读) | 4 | [`…/legado/index.json`](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/legado/index.json) | [t1](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/legado/tier1/index.json) | — | — |
| MangaReader | 4 | [`…/mangareader/index.json`](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/mangareader/index.json) | — | — | [t3](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/mangareader/tier3/index.json) |
| Unmapped | 3 | [`…/unmapped/index.json`](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/unmapped/index.json) | — | [t2](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/unmapped/tier2/index.json) | [t3](https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/by-ecosystem/unmapped/tier3/index.json) |

> **This dimension overlaps.** One source can cover a site indexed by several ecosystems,
> so the per-ecosystem counts add up to **more than 79**. It's for "I only want that kind of site";
> beginners can ignore it and use the tier URLs above.

---

## Add just one source

The Comic Source page also has a single-URL field at the top: paste one `.js` URL to add exactly
that one source.

**Per-file URLs for all 79 sources** (with tier and latency):

- Human-readable: [`05-venera-sources/files.txt`](05-venera-sources/files.txt)
- Machine-readable: [`05-venera-sources/files.json`](05-venera-sources/files.json)

Each entry looks like:

```
https://cdn.jsdelivr.net/gh/kuiti/manga-source-index@main/05-venera-sources/sources/mkzhan.js
```

Swap the filename at the end for any other source.

---

## FAQ

| Question | Answer |
|---|---|
| **I imported a source but search returns nothing** | That source is broken or the site was redesigned. This happens constantly — sources follow third-party sites. Try another one, or wait for a repo update |
| **How do I update sources?** | Paste the URL again and Refresh. The app compares versions against the list and offers updates |
| **The jsDelivr URL won't load** | Use the `pinned` variant (see [`urls.txt`](05-venera-sources/urls.txt)) — or replace `@main` with a specific commit hash. `raw.githubusercontent.com` often times out on home broadband; don't rely on it |
| **The list is too long to pick from** | Use the tier 1 URL only — 19 sources. Add more later |
| **Adult content** | The lists do include adult sources (~40 sites). Disable the ones you don't want in the app's source manager |
| **Is this legal?** | See the disclaimer below. Nearly all indexed sites are third-party and unofficial — judge for yourself and prefer official channels |
| **Where does this data come from?** | Source definitions collected from 7 open-source manga reader ecosystems, deduplicated, scored and probed. Details in [README.md](README.md) |
| **Does it work on iPhone?** | No — Venera is Android-only. iOS has a different ecosystem; this repo's Aidoku data may help |

---

## Disclaimer

This repository **only aggregates public source metadata** (site domains, names, owning ecosystem).
It **does not host, distribute or mirror any manga content**.

Nearly all indexed sites are third-party and unofficial. Before using them, make sure you comply
with the laws of your jurisdiction and with each site's terms of service, and prefer official,
licensed channels to support creators and publishers. Any consequences are borne by the user.

---

**For the data tables, scripts and scoring methodology** → [README.md](README.md)
**中文说明** → [START-HERE.zh-CN.md](START-HERE.zh-CN.md)
