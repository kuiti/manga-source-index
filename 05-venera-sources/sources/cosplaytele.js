/** @type {import('./_venera_.js')} */

class CosplayTele extends ComicSource {
    name = "CosplayTele"

    key = "cosplaytele"

    version = "1.0.3"

    minAppVersion = "1.4.6"

    url = "https://cdn.jsdelivr.net/gh/maplessovo/venera-configs@main/cosplaytele.js"

    baseUrl = "https://cosplaytele.com"

    apiUrl = `${this.baseUrl}/wp-json/wp/v2`

    pageSize = 18

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }

    imageHeaders = {
        "Referer": `${this.baseUrl}/`,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }

    _buildApiUrl(path, params = {}) {
        let query = Object.entries(params)
            .filter(([, value]) => value !== null && value !== undefined && value !== "")
            .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
            .join("&")
        return `${this.apiUrl}/${path}${query ? `?${query}` : ""}`
    }

    async _request(path, params = {}) {
        let response = await Network.get(this._buildApiUrl(path, params), this.headers)
        if (response.status !== 200) {
            throw `CosplayTele request failed: ${response.status}`
        }
        return {
            data: JSON.parse(response.body),
            headers: response.headers ?? {},
        }
    }

    _getHeader(headers, name) {
        let key = Object.keys(headers ?? {}).find((key) => key.toLowerCase() === name.toLowerCase())
        if (!key) return null
        let value = headers[key]
        return Array.isArray(value) ? value[0] : value
    }

    _htmlToText(html) {
        if (!html) return ""
        let document = new HtmlDocument(`<div>${html}</div>`)
        try {
            return document.querySelector("div")?.text?.trim() ?? ""
        } finally {
            document.dispose()
        }
    }

    _getTerms(post, taxonomy) {
        let groups = post?._embedded?.["wp:term"]
        if (!Array.isArray(groups)) return []

        let terms = []
        for (let group of groups) {
            if (!Array.isArray(group)) continue
            for (let term of group) {
                if (term?.taxonomy === taxonomy && term.name) {
                    terms.push(this._htmlToText(term.name))
                }
            }
        }
        return terms.filter(Boolean)
    }

    _getCover(post) {
        let media = post?._embedded?.["wp:featuredmedia"]?.[0]
        return media?.media_details?.sizes?.medium_large?.source_url
            ?? media?.media_details?.sizes?.medium?.source_url
            ?? media?.source_url
            ?? ""
    }

    _formatDate(value) {
        if (!value) return ""
        let date = new Date(value)
        if (Number.isNaN(date.getTime())) return value.toString().split("T")[0]
        let year = date.getFullYear()
        let month = `${date.getMonth() + 1}`.padStart(2, "0")
        let day = `${date.getDate()}`.padStart(2, "0")
        return `${year}-${month}-${day}`
    }

    _parsePost(post) {
        let categories = this._getTerms(post, "category")
        let postTags = this._getTerms(post, "post_tag")
        return new Comic({
            id: post?.slug ?? post?.id?.toString() ?? "",
            title: this._htmlToText(post?.title?.rendered) || post?.slug || "Untitled",
            subTitle: categories.join(" / "),
            cover: this._getCover(post),
            tags: [...categories, ...postTags],
            description: this._htmlToText(post?.excerpt?.rendered),
            updateTime: this._formatDate(post?.modified ?? post?.date),
        })
    }

    async _loadPosts(params, page, pageSize = this.pageSize) {
        page = Math.max(1, Number(page) || 1)
        let result = await this._request("posts", {
            ...params,
            page: page,
            per_page: pageSize,
            orderby: "date",
            order: "desc",
            _embed: "wp:featuredmedia,wp:term",
            _fields: "id,slug,date,modified,link,title,excerpt,_links,_embedded",
        })
        let posts = Array.isArray(result.data) ? result.data : []
        let totalPages = Number(this._getHeader(result.headers, "x-wp-totalpages"))
        if (!Number.isFinite(totalPages) || totalPages < 1) {
            totalPages = posts.length < pageSize ? page : page + 1
        }
        return {
            comics: posts.map((post) => this._parsePost(post)).filter((comic) => comic.id),
            maxPage: totalPages,
        }
    }

    async _loadPost(id, includeContent = false) {
        let fields = "id,slug,date,modified,link,title,excerpt,_links,_embedded"
        if (includeContent) fields += ",content"

        let result = await this._request("posts", {
            slug: id,
            per_page: 1,
            _embed: "wp:featuredmedia,wp:term",
            _fields: fields,
        })
        let post = Array.isArray(result.data) ? result.data[0] : null
        if (!post) throw `CosplayTele post not found: ${id}`
        return post
    }

    _normalizeUrl(url) {
        if (!url) return ""
        url = url.replaceAll("&amp;", "&").trim()
        if (url.startsWith("//")) return `https:${url}`
        if (url.startsWith("/")) return `${this.baseUrl}${url}`
        return url
    }

    _isGalleryImage(url) {
        if (!url || !url.includes("/wp-content/uploads/")) return false
        let path = url.split(/[?#]/)[0]
        return /\.(?:avif|gif|jpe?g|png|webp)$/i.test(path)
    }

    _extractImages(html) {
        let document = new HtmlDocument(html ?? "")
        let images = []
        let seen = new Set()

        let addImage = (url) => {
            url = this._normalizeUrl(url)
            if (!this._isGalleryImage(url) || seen.has(url)) return
            seen.add(url)
            images.push(url)
        }

        try {
            for (let link of document.querySelectorAll("a[href]")) {
                addImage(link.attributes?.["href"])
            }
            for (let image of document.querySelectorAll("img")) {
                let attributes = image.attributes ?? {}
                addImage(attributes["data-src"] ?? attributes["data-lazy-src"] ?? attributes["src"])
            }
        } finally {
            document.dispose()
        }
        return images
    }

    _extractTopSearchGroups(html) {
        let document = new HtmlDocument(html ?? "")
        let groups = []
        let supportedTitles = ["Top Search", "Cosplayer", "Character", "Game"]

        try {
            for (let heading of document.querySelectorAll("h2")) {
                let title = heading.text?.trim() ?? ""
                if (!supportedTitles.includes(title)) continue

                let container = heading.parent
                let categories = []
                let tags = []
                let terms = []
                for (let link of container?.querySelectorAll("a[href]") ?? []) {
                    let href = link.attributes?.["href"] ?? ""
                    let match = href.match(/\/(category|tag)\/([^/?#]+)\/?/i)
                    if (!match) continue
                    let slug = decodeURIComponent(match[2])
                    let taxonomy = match[1].toLowerCase()
                    let list = taxonomy === "category" ? categories : tags
                    if (!list.includes(slug)) list.push(slug)
                    if (!terms.some((term) => term.taxonomy === taxonomy && term.slug === slug)) {
                        terms.push({
                            taxonomy: taxonomy,
                            slug: slug,
                            label: link.text?.trim() || slug.replaceAll("-", " "),
                        })
                    }
                }
                if (categories.length > 0 || tags.length > 0) {
                    groups.push({ title, categories, tags, terms })
                }
            }
        } finally {
            document.dispose()
        }
        return groups
    }

    async _resolveTerms(path, slugs) {
        if (slugs.length === 0) return new Map()
        let result = await this._request(path, {
            slug: slugs.join(","),
            per_page: 100,
            _fields: "id,name,slug",
        })
        let map = new Map()
        for (let term of Array.isArray(result.data) ? result.data : []) {
            if (term?.slug && term?.id != null) map.set(term.slug, term.id.toString())
        }
        return map
    }

    async _loadTopSearchTerms(limit = 10) {
        let pageResult = await this._request("pages", {
            slug: "top-search",
            per_page: 1,
            _fields: "content",
        })
        let page = Array.isArray(pageResult.data) ? pageResult.data[0] : null
        let groups = this._extractTopSearchGroups(page?.content?.rendered)
        let topSearch = groups.find((group) => group.title === "Top Search")
        if (!topSearch || topSearch.terms.length === 0) throw "Top Search terms not found"

        let terms = topSearch.terms.slice(0, limit)
        let categorySlugs = terms.filter((term) => term.taxonomy === "category").map((term) => term.slug)
        let tagSlugs = terms.filter((term) => term.taxonomy === "tag").map((term) => term.slug)
        let [categoryMap, tagMap] = await Promise.all([
            this._resolveTerms("categories", categorySlugs),
            this._resolveTerms("tags", tagSlugs),
        ])

        return terms.map((term) => {
            let id = term.taxonomy === "category" ? categoryMap.get(term.slug) : tagMap.get(term.slug)
            if (!id) return null
            return {
                value: `${term.taxonomy === "category" ? "c" : "t"}${id}`,
                label: term.label,
            }
        }).filter(Boolean)
    }

    async _loadLevelOptions() {
        let definitions = [
            { label: "Nude", slug: "cosplay-nude" },
            { label: "Ero", slug: "cosplay-ero" },
            { label: "Cosplay", slug: "cosplay" },
        ]
        let categoryMap = await this._resolveTerms("categories", definitions.map((item) => item.slug))
        return definitions.map((item) => {
            let id = categoryMap.get(item.slug)
            return id ? { value: `c${id}`, label: item.label } : null
        }).filter(Boolean)
    }

    async _loadFilteredPosts(filter, page) {
        let match = filter?.toString().match(/^([ct])(\d+)$/)
        if (!match) throw "Invalid CosplayTele filter"
        return this._loadPosts({ [match[1] === "c" ? "categories" : "tags"]: match[2] }, page)
    }

    async _loadPopularPosts(range, timeQuantity = null, timeUnit = null) {
        let params = {
            limit: 20,
            range: range,
            time_quantity: timeQuantity,
            time_unit: timeUnit,
            _embed: "wp:featuredmedia,wp:term",
            _fields: "id,slug,date,modified,link,title,excerpt,_links,_embedded",
        }
        let query = Object.entries(params)
            .filter(([, value]) => value !== null && value !== undefined && value !== "")
            .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
            .join("&")
        let url = `${this.baseUrl}/wp-json/wordpress-popular-posts/v1/popular-posts?${query}`
        let response = await Network.get(url, this.headers)
        if (response.status !== 200) throw `CosplayTele popular posts failed: ${response.status}`
        let posts = JSON.parse(response.body)
        return (Array.isArray(posts) ? posts : []).map((post) => this._parsePost(post))
    }

    async _loadTopCosplayRanking(period) {
        let definitions = {
            "24h": ["custom", 24, "hour"],
            "3d": ["custom", 3, "day"],
            "7d": ["last7days", null, null],
        }
        let selected = definitions[period] ?? definitions["24h"]
        return {
            comics: await this._loadPopularPosts(selected[0], selected[1], selected[2]),
            maxPage: 1,
        }
    }

    _categoryTarget(category, param) {
        return {
            page: "category",
            attributes: { category: category, param: param },
        }
    }

    async _loadTopSearchExplore() {
        let term = (await this._loadTopSearchTerms(10))[0]
        if (!term) throw "Top Search terms not found"
        let result = await this._loadFilteredPosts(term.value, 1)
        return [{
            title: term.label,
            comics: result.comics.slice(0, 12),
            viewMore: this._categoryTarget("Top Search", "top-search"),
        }]
    }

    async _loadLevelExplore() {
        let level = (await this._loadLevelOptions())[0]
        if (!level) throw "Level Cosplay categories not found"
        let result = await this._loadFilteredPosts(level.value, 1)
        return [{
            title: level.label,
            comics: result.comics.slice(0, 12),
            viewMore: this._categoryTarget("Level Cosplay", "level-cosplay"),
        }]
    }

    async _loadTopCosplayExplore() {
        let result = await this._loadTopCosplayRanking("24h")
        return [{
            title: "24 hours",
            comics: result.comics.slice(0, 12),
            viewMore: this._categoryTarget("Top Cosplay", "top-cosplay"),
        }]
    }

    explore = [
        {
            title: "CosplayTele",
            type: "multiPageComicList",
            load: async (page) => this._loadPosts({}, page),
        },
        {
            title: "Top Search",
            type: "multiPartPage",
            load: async () => this._loadTopSearchExplore(),
        },
        {
            title: "Level Cosplay",
            type: "multiPartPage",
            load: async () => this._loadLevelExplore(),
        },
        {
            title: "Top Cosplay",
            type: "multiPartPage",
            load: async () => this._loadTopCosplayExplore(),
        }
    ]

    category = {
        title: "CosplayTele",
        parts: [
            {
                name: "Featured",
                type: "fixed",
                categories: [
                    {
                        label: "Top Search",
                        target: {
                            page: "category",
                            attributes: { category: "Top Search", param: "top-search" },
                        },
                    },
                    {
                        label: "Level Cosplay",
                        target: {
                            page: "category",
                            attributes: { category: "Level Cosplay", param: "level-cosplay" },
                        },
                    },
                    {
                        label: "Top Cosplay",
                        target: {
                            page: "category",
                            attributes: { category: "Top Cosplay", param: "top-cosplay" },
                        },
                    },
                ],
            },
            {
                name: "Categories",
                type: "dynamic",
                loader: async () => {
                    let result = await this._request("categories", {
                        per_page: 50,
                        page: 1,
                        orderby: "count",
                        order: "desc",
                        hide_empty: true,
                        _fields: "id,name,slug,count",
                    })
                    let categories = Array.isArray(result.data) ? result.data : []
                    return categories.map((category) => ({
                        label: this._htmlToText(category.name),
                        target: {
                            page: "category",
                            attributes: {
                                category: this._htmlToText(category.name),
                                param: category.id.toString(),
                            },
                        },
                    }))
                },
            }
        ],
        enableRankingPage: false,
    }

    categoryComics = {
        load: async (category, param, options, page) => {
            let selected = Array.isArray(options) ? options[0] : null
            if (param === "top-search") {
                if (!selected) selected = (await this._loadTopSearchTerms(10))[0]?.value
                return this._loadFilteredPosts(selected, page)
            }
            if (param === "level-cosplay") {
                if (!selected) selected = (await this._loadLevelOptions())[0]?.value
                return this._loadFilteredPosts(selected, page)
            }
            if (param === "top-cosplay") {
                return this._loadTopCosplayRanking(selected ?? "24h")
            }
            if (!param) throw "Invalid category id"
            return this._loadPosts({ categories: param }, page)
        },
        optionLoader: async (category, param) => {
            if (param === "top-search") {
                let terms = await this._loadTopSearchTerms(10)
                return [{
                    label: "Hot Keyword",
                    options: terms.map((term) => `${term.value}-${term.label}`),
                }]
            }
            if (param === "level-cosplay") {
                let levels = await this._loadLevelOptions()
                return [{
                    label: "Level",
                    options: levels.map((level) => `${level.value}-${level.label}`),
                }]
            }
            if (param === "top-cosplay") {
                return [{
                    label: "Period",
                    options: ["24h-24 hours", "3d-3 days", "7d-7 days"],
                }]
            }
            return []
        },
    }

    search = {
        load: async (keyword, options, page) => {
            return this._loadPosts({ search: keyword }, page)
        },
        optionList: [],
        enableTagsSuggestions: false,
    }

    comic = {
        loadInfo: async (id) => {
            id = id?.toString().trim() ?? ""
            if (!id) throw "Invalid CosplayTele post id"

            let post = await this._loadPost(id, true)
            let categories = this._getTerms(post, "category")
            let postTags = this._getTerms(post, "post_tag")
            let content = post?.content?.rendered ?? ""
            let document = new HtmlDocument(content)
            let description = ""
            try {
                description = document.querySelector("blockquote")?.text?.trim() ?? ""
            } finally {
                document.dispose()
            }
            if (!description) description = this._htmlToText(post?.excerpt?.rendered)

            let chapters = new Map()
            chapters.set(post.slug, "Photo Gallery")

            return new ComicDetails({
                title: this._htmlToText(post?.title?.rendered) || post.slug,
                cover: this._getCover(post),
                description: description,
                tags: {
                    "Category": categories,
                    "Tag": postTags,
                },
                chapters: chapters,
                updateTime: this._formatDate(post?.modified ?? post?.date),
                url: post?.link ?? `${this.baseUrl}/${post.slug}/`,
            })
        },

        loadEp: async (comicId, epId) => {
            let id = epId?.toString().trim() || comicId?.toString().trim()
            if (!id) throw "Invalid CosplayTele chapter id"
            let post = await this._loadPost(id, true)
            let images = this._extractImages(post?.content?.rendered)
            if (images.length === 0) throw "No gallery images found"
            return { images: images }
        },

        onImageLoad: () => ({ headers: this.imageHeaders }),

        onThumbnailLoad: () => ({ headers: this.imageHeaders }),

        onClickTag: (namespace, tag) => ({
            page: "search",
            keyword: tag,
        }),

        link: {
            domains: ["cosplaytele.com"],
            linkToId: (url) => {
                let match = url?.match(/^https?:\/\/(?:www\.)?cosplaytele\.com\/([^/?#]+)\/?/i)
                if (!match) return null
                let id = decodeURIComponent(match[1])
                if (["page", "category", "tag", "author", "wp-json"].includes(id)) return null
                return id
            },
        },

        enableTagsTranslate: false,
    }

    translation = {
        "zh_CN": {
            "Featured": "精选",
            "Categories": "分类",
            "Hot Keyword": "热门词",
            "Level": "等级",
            "Period": "排行周期",
            "24 hours": "24 小时",
            "3 days": "3 天",
            "7 days": "7 天",
            "Category": "分类",
            "Tag": "标签",
            "Photo Gallery": "图片集",
        },
        "zh_TW": {
            "Featured": "精選",
            "Categories": "分類",
            "Hot Keyword": "熱門詞",
            "Level": "等級",
            "Period": "排行週期",
            "24 hours": "24 小時",
            "3 days": "3 天",
            "7 days": "7 天",
            "Category": "分類",
            "Tag": "標籤",
            "Photo Gallery": "圖片集",
        },
    }
}
