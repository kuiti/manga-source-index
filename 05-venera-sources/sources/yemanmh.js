/** @type {import('./_venera_.js')} */

/**
 * 野漫漫画（站点标题：漫神）
 * 由 Cimoc 源配置 YEMANMH 移植为 Venera 源。
 *
 * 移植依据（均已在 2026-09-23 对线上站点实测通过）：
 *   search            GET  {base}/search?searchkey={kw}
 *                     列表容器   #js_comicSortList > li
 *                     标题/详情  p.title / a[href]
 *                     封面       img[src]
 *                     更新       span.chapter
 *   parseInfoTitle    h1.name
 *   parseInfoCover    div#detail（cover 在 style 的 background-image 里）
 *   parseInfoIntro    p#js_desc_content
 *   parseInfoAuthor   span.author
 *   parseInfoStatus   span.origin
 *   parseInfoUpdate   span.update_time
 *   parseChapterList1 ul#js_chapters > li > a   →  /chapter/{aid}/{cid}.html
 *   parseImageList    #imgsec img.calwh
 *
 * 注意：章节页 HTML 里不含真实图片地址（img.src 是占位 load.gif），
 * 必须调接口 POST /api/comic/read/pics（参数 id/aid/offset/limit，单次最多返回 10 张）。
 */
class YeManMh extends ComicSource {
    name = "野漫漫画(漫神)"

    key = "yemanmh"

    version = "1.0.0"

    minAppVersion = "1.6.0"

    url = ""

    baseUrl = "https://m.mhkami.com"

    ua = "Mozilla/5.0 (Linux; Android 16) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36"

    _headers(extra) {
        let h = {
            "user-agent": this.ua,
            "referer": this.baseUrl + "/",
        }
        if (extra) {
            for (let k in extra) h[k] = extra[k]
        }
        return h
    }

    _abs(url) {
        if (!url) return ""
        if (url.startsWith("http")) return url
        if (url.startsWith("//")) return "https:" + url
        return this.baseUrl + (url.startsWith("/") ? url : "/" + url)
    }

    search = {
        load: async (keyword, options, page) => {
            // Cimoc 配置 search = "/search?searchkey=%s"，无分页参数
            let url = `${this.baseUrl}/search?searchkey=${encodeURIComponent(keyword)}`
            let res = await Network.get(url, this._headers())
            if (res.status !== 200) throw `Invalid status code: ${res.status}`

            let doc = new HtmlDocument(res.body)
            let comics = []
            for (let item of doc.querySelectorAll("#js_comicSortList > li")) {
                let a = item.querySelector("a")
                if (!a) continue
                let href = a.attributes["href"] || ""
                let m = href.match(/\/book\/(\d+)/)
                if (!m) continue

                let titleNode = item.querySelector("p.title")
                let coverNode = item.querySelector("img")
                let updateNode = item.querySelector("span.chapter")
                let cover = coverNode
                    ? (coverNode.attributes["data-src"] || coverNode.attributes["src"] || "")
                    : ""

                comics.push(new Comic({
                    id: m[1],
                    title: titleNode ? titleNode.text.trim() : (a.attributes["title"] || "").trim(),
                    cover: this._abs(cover),
                    subTitle: updateNode ? updateNode.text.trim() : "",
                }))
            }
            return { comics: comics, maxPage: 1 }
        }
    }

    comic = {
        loadInfo: async (id) => {
            let url = `${this.baseUrl}/book/${id}/`
            let res = await Network.get(url, this._headers())
            if (res.status !== 200) throw `Invalid status code: ${res.status}`

            let doc = new HtmlDocument(res.body)

            let authorNode = doc.querySelector("span.author")
            let author = authorNode ? authorNode.text.trim() : ""

            // h1.name 里嵌套了 <span class="author">，需要把作者从标题里剥掉
            let titleNode = doc.querySelector("h1.name")
            let title = titleNode ? titleNode.text.trim() : ""
            if (author && title.endsWith(author)) {
                title = title.substring(0, title.length - author.length).trim()
            }

            let introNode = doc.querySelector("p#js_desc_content")
            let statusNode = doc.querySelector("span.origin")
            let updateNode = doc.querySelector("span.update_time")

            // 封面在 div#detail 的 style="background-image:url('...')"
            let cover = ""
            let detailNode = doc.querySelector("div#detail")
            if (detailNode) {
                let style = detailNode.attributes["style"] || ""
                let sm = style.match(/url\(\s*['"]?([^'")]+)['"]?\s*\)/)
                if (sm) cover = sm[1]
            }

            let chapters = {}
            for (let a of doc.querySelectorAll("ul#js_chapters > li > a")) {
                let href = a.attributes["href"] || ""
                let m = href.match(/\/chapter\/\d+\/(\d+)\.html/)
                if (!m) continue
                chapters[m[1]] = a.text.trim()
            }

            let tags = {}
            if (author) tags["作者"] = [author]
            if (statusNode) tags["状态"] = [statusNode.text.trim()]
            if (updateNode) tags["更新"] = [updateNode.text.trim()]

            return new ComicDetails({
                title: title,
                cover: this._abs(cover),
                description: introNode ? introNode.text.trim() : "",
                tags: tags,
                chapters: chapters,
                isFavorite: false,
                url: url,
            })
        },

        loadEp: async (comicId, epId) => {
            // 接口单次最多返回 10 张，按 offset 翻页
            const LIMIT = 10
            let images = []
            let offset = 0
            let total = null

            while (true) {
                let body = `id=${epId}&aid=${comicId}&offset=${offset}&limit=${LIMIT}`
                let res = await Network.post(
                    `${this.baseUrl}/api/comic/read/pics`,
                    this._headers({
                        "content-type": "application/x-www-form-urlencoded;charset=utf-8",
                        "x-requested-with": "XMLHttpRequest",
                        "referer": `${this.baseUrl}/chapter/${comicId}/${epId}.html`,
                    }),
                    body
                )
                if (res.status !== 200) throw `Invalid status code: ${res.status}`

                let data = JSON.parse(res.body)
                if (!data || data.code !== 1 || !data.data || !data.data.pic) {
                    throw "接口返回异常，无法获取图片列表"
                }

                let pic = data.data.pic
                if (total === null) total = data.data.total || 0
                if (pic.length === 0) break

                for (let p of pic) {
                    images.push(this._abs(p.pic || p.url || ""))
                }

                offset += LIMIT
                if (offset >= total) break
                if (offset > 3000) break
            }

            if (images.length === 0) throw "该章节没有取到图片"
            return { images: images }
        },

        idMatch: "m\\.mhkami\\.com/book/(\\d+)",
    }

    settings = {}
}
