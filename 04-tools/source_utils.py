#!/usr/bin/env python3
"""源清单流水线共享工具。

**域名归一化只有 norm() 这一份实现**，所有脚本一律从这里导入，
不要各自复制——历史上因为两处实现不一致，出现过 `httpsac.qq.com`
和把 `cdn.jsdelivr.net` 当成站点域的 bug。
"""
import json
import os
import re

VALID = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$")
# 这些是源的「更新地址 / 代码托管」，不是站点域名
SKIP = ("jsdelivr", "githubusercontent", "github.com", "gitee.com", "raw.git")


def norm(u):
    """归一化域名。去协议、端口、路径、查询串与常见子域前缀；非法或托管地址返回空串。

    顺序不可调换：必须先剥协议，再清非域名字符。
    反例：先清字符会把 `https://ac.qq.com` 变成 `httpsac.qq.com`。
    """
    if not u:
        return ""
    s = str(u).strip().lower()
    s = re.sub(r"^[a-z][a-z0-9+.-]*://", "", s)          # 1. 剥协议
    s = s.split("#")[0].split("?")[0].split("/")[0].split(":")[0]
    s = re.sub(r"[^a-z0-9.\-]", "", s)                   # 2. 清非域名字符
    s = re.sub(r"^(www|m|mobile|cn|app|touch)\.", "", s).strip(".")
    parts = s.split(".")                                 # 3. 只保留最前面的合法域名段
    while len(parts) > 2 and not VALID.match(".".join(parts)):
        parts.pop()
    s = ".".join(parts)
    if not VALID.match(s) or any(k in s for k in SKIP):
        return ""
    return s


def fold_name(s):
    """源名折叠：去括号注释与非字母数字，用于跨生态按名称匹配。"""
    s = str(s or "").lower()
    s = re.sub(r"[（(][^）)]*[）)]", "", s)
    return re.sub(r"[^0-9a-z\u4e00-\u9fff\u3040-\u30ff]", "", s)


def load(path):
    if not os.path.exists(path):
        return []
    return json.load(open(path, encoding="utf-8-sig"))


def pick_base(txt):
    """从 Venera 源 js 里取站点基址。

    优先 `baseUrl = "..."`；否则取第一个非 CDN 的 https 地址。
    注意不能直接用 `url =` 字段——那是源的更新地址（jsDelivr）。
    """
    m = re.search(r"\bbaseUrl\s*=\s*[\"'](https?://[^\"']+)", txt)
    if m and norm(m.group(1)):
        return m.group(1)
    for m in re.finditer(r"(https?://[a-zA-Z0-9._~:/?#\[\]@!$&'()*+,;=%-]+)", txt):
        if norm(m.group(1)):
            return m.group(1)
    return ""


def load_venera_names(vdir):
    """已有 Venera 可用源的名称集合（折叠后）。"""
    names = set()
    for sub in ("合并全集", "Cimoc移植"):
        for x in load(os.path.join(vdir, sub, "index.json")):
            f = fold_name(x.get("name"))
            if f:
                names.add(f)
    return names


def has_impl(names, vset):
    """该站点是否已有现成 Venera 源实现。"""
    for n in names:
        f = fold_name(n)
        if not f:
            continue
        if f in vset:
            return True
        if len(f) >= 4 and any(len(v) >= 4 and (f in v or v in f) for v in vset):
            return True
    return False
