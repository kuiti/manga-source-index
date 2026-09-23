#!/usr/bin/env python3
"""漫画源站点连通性检测。

用法:
    python check_connectivity.py --input zh_sources.json --tag no_proxy
    python check_connectivity.py --input master_sources.json --tag with_proxy

默认走系统环境里的代理设置（urllib 会读取 HTTP_PROXY / HTTPS_PROXY）。
加 --no-proxy 可强制直连，用于对比。
"""
import argparse
import csv
import json
import os
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = ("Mozilla/5.0 (Linux; Android 16) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36")

TIMEOUT = 10
MAX_READ = 65536


def probe(domain, no_proxy=False):
    """探测单个域名，返回结果 dict。"""
    res = {
        "domain": domain, "alive": 0, "scheme": "", "status": 0,
        "final_url": "", "latency_ms": 0, "size": 0, "title": "",
        "error": "", "looks_manga": 0,
    }
    handlers = []
    if no_proxy:
        handlers.append(urllib.request.ProxyHandler({}))
    opener = urllib.request.build_opener(*handlers)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for scheme in ("https", "http"):
        url = f"{scheme}://{domain}/"
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
        t0 = time.time()
        try:
            with opener.open(req, timeout=TIMEOUT) as r:
                body = r.read(MAX_READ)
                res["latency_ms"] = int((time.time() - t0) * 1000)
                res["scheme"] = scheme
                res["status"] = r.status
                res["final_url"] = r.geturl()
                res["size"] = len(body)
                res["alive"] = 1
                html = body.decode("utf-8", "ignore")
                m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
                if m:
                    res["title"] = re.sub(r"\s+", " ", m.group(1)).strip()[:80]
                kw = ("漫画", "comic", "manga", "manhua", "漫畫", "chapter", "話", "话")
                low = html.lower()
                res["looks_manga"] = int(sum(1 for k in kw if k.lower() in low) >= 2)
                return res
        except urllib.error.HTTPError as e:
            res["latency_ms"] = int((time.time() - t0) * 1000)
            res["scheme"] = scheme
            res["status"] = e.code
            res["error"] = f"HTTP {e.code}"
            # 403/451/503 说明主机活着，只是拒绝我们
            if e.code in (401, 403, 405, 429, 451, 503):
                res["alive"] = 1
                return res
        except urllib.error.URLError as e:
            reason = str(getattr(e, "reason", e))
            if isinstance(getattr(e, "reason", None), socket.timeout):
                res["error"] = "timeout"
            elif "Name or service not known" in reason or "getaddrinfo" in reason:
                res["error"] = "dns_fail"
            elif "CERTIFICATE" in reason.upper() or "SSL" in reason.upper():
                res["error"] = f"tls: {reason[:40]}"
            else:
                res["error"] = reason[:60]
        except socket.timeout:
            res["error"] = "timeout"
        except Exception as e:
            res["error"] = f"{type(e).__name__}: {str(e)[:50]}"

    if not res["error"]:
        res["error"] = "unreachable"
    return res


def load_domains(path):
    d = json.load(open(path, encoding="utf-8-sig"))
    if isinstance(d, dict) and "domains" in d:          # master_sources.json
        return sorted(d["domains"].keys())
    if isinstance(d, list):                              # zh_sources.json / curated
        return sorted({x["domain"] for x in d if x.get("domain")})
    raise SystemExit("无法识别的输入格式")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--tag", required=True, help="输出文件后缀，如 no_proxy / with_proxy")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--workers", type=int, default=30)
    ap.add_argument("--no-proxy", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    domains = load_domains(a.input)
    if a.limit:
        domains = domains[:a.limit]
    print(f"待测域名: {len(domains)}   并发: {a.workers}   代理: "
          f"{'直连(强制)' if a.no_proxy else '按环境变量'}")
    if not a.no_proxy:
        for k in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy"):
            if os.environ.get(k):
                print(f"  环境代理 {k} = {os.environ[k]}")
                break

    results = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(probe, d, a.no_proxy): d for d in domains}
        done = 0
        for f in as_completed(futs):
            results.append(f.result())
            done += 1
            if done % 25 == 0 or done == len(domains):
                ok = sum(1 for r in results if r["alive"])
                print(f"  进度 {done}/{len(domains)}  存活 {ok}  "
                      f"({time.time() - t0:.0f}s)", flush=True)

    results.sort(key=lambda r: (-r["alive"], r["domain"]))
    out = os.path.join(a.outdir, f"connectivity_{a.tag}.csv")
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)

    alive = [r for r in results if r["alive"]]
    manga = [r for r in alive if r["looks_manga"]]
    print(f"\n=== 汇总 ({a.tag}) ===")
    print(f"  总计   {len(results)}")
    print(f"  存活   {len(alive)}  ({len(alive)*100//max(1,len(results))}%)")
    print(f"  疑似漫画站 {len(manga)}")
    from collections import Counter
    print(f"  失败原因: {Counter(r['error'] for r in results if not r['alive']).most_common(8)}")
    print(f"  输出 {out}  耗时 {time.time()-t0:.0f}s")
    json.dump(results, open(os.path.join(a.outdir, f"connectivity_{a.tag}.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
