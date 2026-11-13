"""DATA VISUALIZATION — tạo trang HTML trực quan hóa dữ liệu và kết quả Lab 3.

Chạy (từ thư mục LAB 3, sau src.data; phần kết quả cần src.train và src.evaluation):
    python -m src.visualize

Đầu vào : data/rotten_tomatoes/*.csv, results/train_log.json, results/test_metrics.json,
          results/misclassified.csv (thiếu file kết quả nào thì bỏ qua phần đó).
Đầu ra  : results/data_visualization.html — một file duy nhất, mở bằng trình duyệt,
          không cần mạng, không cần cài thêm thư viện (chỉ dùng thư viện chuẩn Python).
"""
import csv
import html
import json
import math
import re
from collections import Counter

from src import config

SPLITS = ("train", "validation", "test")
SPLIT_VI = {"train": "Train", "validation": "Validation", "test": "Test"}
OUT_FILE = config.RESULTS_DIR / "data_visualization.html"

# Từ phổ biến không mang cảm xúc, bỏ khi tìm từ đặc trưng của mỗi lớp
STOPWORDS = set("""
a an the and or but if of to in on at by for with from as is are was were be been being it its it's
this that these those there here he she they them his her their we you your i me my our us who whom
which what when where why how all any both each few more most other some such no nor not only own same
so than too very can will just don't should now do does did doing have has had having would could
into about over under again further then once out up down off s t also film movie one -- n't 're 've
'll 'd 'm ... like even much may might must make makes made get gets lrb rrb
""".split())


# ------------------------------------------------------------------ Đọc dữ liệu
def read_split(split):
    path = config.DATASET_CSV_DIR / f"{split}.csv"
    with open(path, encoding="utf-8", newline="") as f:
        return [(row["text"], int(row["label"])) for row in csv.DictReader(f)]


def read_json(name):
    path = config.RESULTS_DIR / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def read_misclassified():
    path = config.RESULTS_DIR / "misclassified.csv"
    if not path.exists():
        return None
    with open(path, encoding="utf-8", newline="") as f:
        return [dict(r, confidence=float(r["confidence"])) for r in csv.DictReader(f)]


def discriminative_words(rows, top=12, min_count=25):
    """Từ đặc trưng mỗi lớp theo log-odds (làm trơn +1) giữa lớp pos và neg trên tập train."""
    counts = {0: Counter(), 1: Counter()}
    for text, label in rows:
        for w in re.findall(r"[a-z][a-z'-]+", text.lower()):
            if w not in STOPWORDS and len(w) > 2:
                counts[label][w] += 1
    vocab = set(counts[0]) | set(counts[1])
    n0, n1, v = sum(counts[0].values()), sum(counts[1].values()), len(vocab)
    scored = []
    for w in vocab:
        c0, c1 = counts[0][w], counts[1][w]
        if c0 + c1 >= min_count:
            score = math.log((c1 + 1) / (n1 + v)) - math.log((c0 + 1) / (n0 + v))
            scored.append((w, score, c0, c1))
    scored.sort(key=lambda x: x[1])
    neg = [(w, -s, c0, c1) for w, s, c0, c1 in scored[:top]]
    pos = [(w, s, c0, c1) for w, s, c0, c1 in scored[::-1][:top]]
    return neg, pos


# ------------------------------------------------------------------ EDA
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9'-]*")
CUES = [  # (tên, hàm kiểm tra) — dấu hiệu ngôn ngữ đếm theo nhãn
    ("Phủ định (not, no, never, n't…)", lambda t: bool(re.search(r"\b(not|no|never|nothing|nobody|none)\b|n't", t))),
    ("Từ nối tương phản \"but\"", lambda t: re.search(r"\bbut\b", t) is not None),
    ("Dấu hỏi \"?\"", lambda t: "?" in t),
    ("Dấu chấm than \"!\"", lambda t: "!" in t),
]


def eda_stats(data):
    """Kiểm tra chất lượng, rò rỉ giữa các tập, từ vựng và dấu hiệu ngôn ngữ."""
    texts = {s: [t for t, _ in rows] for s, rows in data.items()}
    train_set = set(texts["train"])
    quality = []
    for s in SPLITS:
        c = Counter(texts[s])
        quality.append({
            "split": s, "rows": len(texts[s]),
            "empty": sum(1 for t in texts[s] if not t.strip()),
            "dup": sum(v - 1 for v in c.values() if v > 1),
            "in_train": 0 if s == "train" else sum(1 for t in texts[s] if t in train_set),
            "non_ascii": sum(1 for t in texts[s] if any(ord(ch) > 127 for ch in t)),
        })
    vocab = Counter(w for t in texts["train"] for w in TOKEN_RE.findall(t.lower()))
    vocab_rows = [{"split": "train", "tokens": sum(vocab.values()), "vocab": len(vocab), "oov": 0.0}]
    for s in ("validation", "test"):
        ws = [w for t in texts[s] for w in TOKEN_RE.findall(t.lower())]
        vocab_rows.append({"split": s, "tokens": len(ws), "vocab": len(set(ws)),
                           "oov": sum(1 for w in ws if w not in vocab) / len(ws)})
    hapax = sum(1 for v in vocab.values() if v == 1) / len(vocab)
    cues = []
    for name, fn in CUES:
        rate = {}
        for lab in (0, 1):
            rows = [t for t, l in data["train"] if l == lab]
            rate[lab] = sum(1 for t in rows if fn(t)) / len(rows)
        cues.append((name, rate[0], rate[1]))
    return {"quality": quality, "vocab": vocab_rows, "hapax": hapax, "cues": cues}


def flow(steps):
    """Sơ đồ quy trình EDA: các bước nối bằng mũi tên, mỗi bước kèm phát hiện chính."""
    items = []
    for i, (title, finding) in enumerate(steps, 1):
        items.append(f'<li><span class="num">{i}</span><b>{esc(title)}</b><small>{esc(finding)}</small></li>')
    return f'<ol class="flow">{"".join(items)}</ol>'


# ------------------------------------------------------------------ SVG helpers
def esc(s):
    return html.escape(str(s), quote=True)


def fmt_int(n):
    return f"{int(round(n)):,}".replace(",", ".")


def nice_max(v):
    if v <= 0:
        return 1
    exp = 10 ** math.floor(math.log10(v))
    for m in (1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if m * exp >= v:
            return m * exp
    return 10 * exp


def ticks(lo, hi, n=5):
    step = (hi - lo) / n
    return [lo + i * step for i in range(n + 1)]


def legend(items):
    return '<div class="legend">' + "".join(
        f'<span><i style="background:var({c})"></i>{esc(t)}</span>' for t, c in items) + "</div>"


def grouped_bars(groups, series, title_y, fmt=fmt_int, ymax=None, width=640, height=280):
    """groups: tên nhóm trục x; series: [(tên, css_var, [giá trị theo nhóm])]."""
    ml, mr, mt, mb = 56, 12, 28, 34
    pw, ph = width - ml - mr, height - mt - mb
    vmax = ymax or nice_max(max(v for _, _, vals in series for v in vals))
    out = [f'<svg viewBox="0 0 {width} {height}" role="img">']
    for t in ticks(0, vmax, 4):
        y = mt + ph - t / vmax * ph
        out.append(f'<line class="grid" x1="{ml}" x2="{ml + pw}" y1="{y:.1f}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="{ml - 6}" y="{y + 4:.1f}" text-anchor="end">{fmt(t)}</text>')
    gw = pw / len(groups)
    bw = min(36, (gw * 0.7) / len(series))
    for gi, g in enumerate(groups):
        x0 = ml + gi * gw + (gw - bw * len(series) - 2 * (len(series) - 1)) / 2
        for si, (name, var, vals) in enumerate(series):
            v = vals[gi]
            h = max(v / vmax * ph, 0.5)
            x = x0 + si * (bw + 2)
            y = mt + ph - h
            r = min(4, bw / 2, h)
            out.append(
                f'<path data-tip="{esc(g)} · {esc(name)}: {esc(fmt(v))}" fill="var({var})" '
                f'd="M{x:.1f},{mt + ph:.1f} V{y + r:.1f} Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f} '
                f'H{x + bw - r:.1f} Q{x + bw:.1f},{y:.1f} {x + bw:.1f},{y + r:.1f} V{mt + ph:.1f} Z"/>')
        out.append(f'<text class="tick" x="{ml + gi * gw + gw / 2:.1f}" y="{height - 12}" '
                   f'text-anchor="middle">{esc(g)}</text>')
    out.append(f'<line class="axis" x1="{ml}" x2="{ml + pw}" y1="{mt + ph}" y2="{mt + ph}"/>')
    out.append(f'<text class="tick" x="{ml}" y="12" text-anchor="middle">{esc(title_y)}</text>')
    out.append("</svg>")
    return "".join(out)


def line_chart(xs, series, title_x, title_y, fmt_y=lambda v: f"{v:.2f}", ymin=0, ymax=None,
               xlabels=None, width=640, height=280, markers=True, nticks=4):
    """series: [(tên, css_var, [(x, y)], nét đứt?)]."""
    ml, mr, mt, mb = 56, 24, 28, 40
    pw, ph = width - ml - mr, height - mt - mb
    xmin, xmax = min(xs), max(xs)
    vmax = ymax if ymax is not None else nice_max(max(y for _, _, pts, _ in series for _, y in pts))
    sx = lambda x: ml + (x - xmin) / ((xmax - xmin) or 1) * pw
    sy = lambda y: mt + ph - (y - ymin) / (vmax - ymin) * ph
    out = [f'<svg viewBox="0 0 {width} {height}" role="img">']
    for t in ticks(ymin, vmax, nticks):
        out.append(f'<line class="grid" x1="{ml}" x2="{ml + pw}" y1="{sy(t):.1f}" y2="{sy(t):.1f}"/>')
        out.append(f'<text class="tick" x="{ml - 6}" y="{sy(t) + 4:.1f}" text-anchor="end">{fmt_y(t)}</text>')
    for x, lab in (xlabels or [(x, x) for x in xs]):
        out.append(f'<text class="tick" x="{sx(x):.1f}" y="{mt + ph + 16}" text-anchor="middle">{esc(lab)}</text>')
    out.append(f'<line class="axis" x1="{ml}" x2="{ml + pw}" y1="{mt + ph}" y2="{mt + ph}"/>')
    for name, var, pts, dashed in series:
        d = " ".join(f"{'M' if i == 0 else 'L'}{sx(x):.1f},{sy(y):.1f}" for i, (x, y) in enumerate(pts))
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        out.append(f'<path d="{d}" fill="none" stroke="var({var})" stroke-width="2"{dash} '
                   f'stroke-linejoin="round" stroke-linecap="round"/>')
        if markers:
            for x, y in pts:
                out.append(f'<circle class="dot" cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4.5" fill="var({var})"/>')
        for x, y in pts:  # vùng bắt chuột lớn hơn điểm
            out.append(f'<circle data-tip="{esc(name)} · {esc(title_x)} {x:g}: {esc(fmt_y(y))}" '
                       f'cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="11" fill="transparent"/>')
    out.append(f'<text class="tick" x="{ml + pw / 2}" y="{height - 4}" text-anchor="middle">{esc(title_x)}</text>')
    out.append(f'<text class="tick" x="{ml}" y="12" text-anchor="middle">{esc(title_y)}</text>')
    out.append("</svg>")
    return "".join(out)


def hbars(items, var, width=320, row=24):
    """items: [(nhãn, giá trị, chú thích hover)] — thanh ngang, nhãn bên trái."""
    ml, mr = 104, 44
    pw = width - ml - mr
    height = row * len(items) + 8
    vmax = max(v for _, v, _ in items)
    out = [f'<svg viewBox="0 0 {width} {height}" role="img" style="max-width:460px">']
    for i, (lab, v, tip) in enumerate(items):
        y = 4 + i * row
        w = max(v / vmax * pw, 1)
        r = min(4, w)
        out.append(f'<text class="lab" x="{ml - 8}" y="{y + row / 2 + 4}" text-anchor="end">{esc(lab)}</text>')
        out.append(f'<path data-tip="{esc(tip)}" fill="var({var})" d="M{ml},{y + 4} H{ml + w - r:.1f} '
                   f'Q{ml + w:.1f},{y + 4} {ml + w:.1f},{y + 4 + r} V{y + row - 4 - r} '
                   f'Q{ml + w:.1f},{y + row - 4} {ml + w - r:.1f},{y + row - 4} H{ml} Z"/>')
        out.append(f'<text class="tick" x="{ml + w + 6:.1f}" y="{y + row / 2 + 4}">{v:.2f}</text>')
    out.append(f'<line class="axis" x1="{ml}" x2="{ml}" y1="2" y2="{height - 2}"/>')
    out.append("</svg>")
    return "".join(out)


def heatmap(cm, labels):
    n = len(labels)
    cell, ml, mt = 120, 110, 40
    width, height = ml + n * cell + 10, mt + n * cell + 30
    vmax = max(max(r) for r in cm)
    steps = ["--seq-150", "--seq-250", "--seq-350", "--seq-450", "--seq-600"]
    total = sum(sum(r) for r in cm)
    out = [f'<svg viewBox="0 0 {width} {height}" role="img" style="max-width:{width}px">']
    out.append(f'<text class="tick" x="{ml + n * cell / 2}" y="16" text-anchor="middle">Dự đoán</text>')
    for j, lab in enumerate(labels):
        out.append(f'<text class="lab" x="{ml + j * cell + cell / 2}" y="{mt - 8}" text-anchor="middle">{esc(lab)}</text>')
    for i, lab in enumerate(labels):
        out.append(f'<text class="lab" x="{ml - 10}" y="{mt + i * cell + cell / 2 + 4}" text-anchor="end">{esc(lab)}</text>')
        for j in range(n):
            v = cm[i][j]
            k = min(int(v / vmax * (len(steps) - 1) + 0.5), len(steps) - 1)
            ink = "#ffffff" if k >= 3 else "var(--ink-1)"
            kind = "đúng" if i == j else "sai"
            out.append(f'<rect data-tip="Thật {esc(lab)} → đoán {esc(labels[j])}: {v} câu ({v / total:.1%}, {kind})" '
                       f'x="{ml + j * cell + 1}" y="{mt + i * cell + 1}" width="{cell - 2}" height="{cell - 2}" '
                       f'rx="4" fill="var({steps[k]})"/>')
            out.append(f'<text x="{ml + j * cell + cell / 2}" y="{mt + i * cell + cell / 2 + 7}" '
                       f'text-anchor="middle" style="fill:{ink};font-size:22px;font-weight:600;pointer-events:none">{v}</text>')
    out.append(f'<text class="tick" x="14" y="{mt + n * cell / 2}" transform="rotate(-90 14 {mt + n * cell / 2})" '
               f'text-anchor="middle">Nhãn thật</text>')
    out.append("</svg>")
    return "".join(out)


def table(headers, rows, cls=""):
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tbl"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def details(summary, content):
    return f"<details><summary>{esc(summary)}</summary>{content}</details>"


def card(title, note, body, wide=False):
    return (f'<section class="card{" wide" if wide else ""}"><h3>{esc(title)}</h3>'
            f'<p class="note">{note}</p>{body}</section>')


# ------------------------------------------------------------------ Trang HTML
CSS = """
:root{color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--ink-1:#0b0b0b;--ink-2:#52514e;--muted:#898781;
--grid:#e1e0d9;--axis:#c3c2b7;--ring:rgba(11,11,11,.10);--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;
--seq-150:#b7d3f6;--seq-250:#86b6ef;--seq-350:#5598e7;--seq-450:#2a78d6;--seq-600:#184f95}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){color-scheme:dark;--page:#0d0d0d;
--surface:#1a1a19;--ink-1:#f0efec;--ink-2:#c3c2b7;--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);
--s1:#3987e5;--s2:#d95926;--s3:#199e70;--seq-150:#184f95;--seq-250:#1c5cab;--seq-350:#256abf;--seq-450:#3987e5;--seq-600:#6da7ec}}
:root[data-theme="dark"]{color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink-1:#f0efec;--ink-2:#c3c2b7;
--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);--s1:#3987e5;--s2:#d95926;--s3:#199e70;
--seq-150:#184f95;--seq-250:#1c5cab;--seq-350:#256abf;--seq-450:#3987e5;--seq-600:#6da7ec}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink-1);font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1080px;margin:0 auto;padding:28px 16px 64px}
h1{font-size:26px;margin:0 0 6px}h2{font-size:19px;margin:36px 0 12px}h3{font-size:15px;margin:0 0 4px}
.lead{color:var(--ink-2);margin:0 0 20px;max-width:760px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}
.tile{background:var(--surface);border:1px solid var(--ring);border-radius:10px;padding:14px 16px}
.tile b{display:block;font-size:26px;font-weight:600}.tile span{color:var(--ink-2);font-size:13px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,460px),1fr));gap:16px}
.card{background:var(--surface);border:1px solid var(--ring);border-radius:10px;padding:16px;min-width:0}
.card.wide{grid-column:1/-1}
.note{color:var(--ink-2);font-size:13px;margin:0 0 10px}
svg{width:100%;height:auto;display:block;overflow:visible}
svg text{fill:var(--ink-2);font-size:12px}svg .lab{fill:var(--ink-1);font-size:12.5px}
svg .grid{stroke:var(--grid);stroke-width:1}svg .axis{stroke:var(--axis);stroke-width:1}
svg .dot{stroke:var(--surface);stroke-width:2}
svg [data-tip]{cursor:default}svg path[data-tip]:hover,svg rect[data-tip]:hover{opacity:.82}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:13px;color:var(--ink-2);margin:0 0 6px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px;vertical-align:-1px}
.pair{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:12px}
.tbl{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13px}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--grid);vertical-align:top}
th{color:var(--ink-2);font-weight:600}td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
details{margin-top:10px;font-size:13px}summary{cursor:pointer;color:var(--ink-2)}
#tip{position:fixed;pointer-events:none;background:var(--ink-1);color:var(--surface);font-size:12.5px;
padding:5px 8px;border-radius:6px;opacity:0;transition:opacity .08s;max-width:280px;z-index:9}
.tag{display:inline-block;padding:0 6px;border-radius:4px;border:1px solid var(--ring);font-size:12px}
.flow{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:20px}
.flow li{position:relative;background:var(--page);border:1px solid var(--ring);border-radius:10px;padding:12px 12px 10px}
.flow li:not(:last-child)::after{content:"→";position:absolute;right:-16px;top:50%;transform:translateY(-50%);color:var(--muted);font-size:16px}
.flow .num{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;background:var(--s1);color:#fff;font-size:12px;font-weight:600;margin-right:6px}
.flow b{font-size:13.5px}.flow small{display:block;color:var(--ink-2);font-size:12.5px;margin-top:6px;line-height:1.45}
.conclude{margin:0;padding-left:18px;font-size:13.5px}.conclude li{margin:4px 0}
@media (max-width:900px){.flow{grid-template-columns:1fr;gap:18px}.flow li:not(:last-child)::after{content:"↓";right:50%;top:auto;bottom:-19px;transform:translateX(50%)}}
footer{margin-top:40px;color:var(--muted);font-size:12.5px}
"""

JS = """
const tip=document.getElementById('tip');
document.addEventListener('mousemove',e=>{const t=e.target.closest('[data-tip]');
if(!t){tip.style.opacity=0;return}tip.textContent=t.dataset.tip;tip.style.opacity=1;
const x=Math.min(e.clientX+14,innerWidth-tip.offsetWidth-8),y=Math.max(e.clientY-tip.offsetHeight-12,8);
tip.style.left=x+'px';tip.style.top=y+'px'});
"""


def build():
    data = {s: read_split(s) for s in SPLITS}
    words = {s: [len(t.split()) for t, _ in rows] for s, rows in data.items()}
    total = sum(len(r) for r in data.values())
    parts = []

    # ---- Tổng quan
    avg_all = sum(sum(w) for w in words.values()) / total
    parts.append('<div class="tiles">' + "".join(
        f'<div class="tile"><b>{v}</b><span>{esc(k)}</span></div>' for v, k in [
            (fmt_int(total), "câu review phim (3 tập)"),
            (f"{fmt_int(len(data['train']))} / {fmt_int(len(data['validation']))} / {fmt_int(len(data['test']))}",
             "train / validation / test"),
            ("50 / 50", "tỉ lệ NEG / POS ở cả 3 tập"),
            (f"{avg_all:.1f}".replace(".", ","), f"từ / câu trung bình; dài nhất {max(max(w) for w in words.values())} từ"),
        ]) + "</div>")

    # ---- Phần 1: dữ liệu
    eda = eda_stats(data)
    q = {r["split"]: r for r in eda["quality"]}
    leak = q["validation"]["in_train"] + q["test"]["in_train"]
    dups = sum(r["dup"] for r in eda["quality"])
    oov = max(r["oov"] for r in eda["vocab"])
    neg_cue = eda["cues"][0]
    parts.append("<h2>1. EDA — khám phá dữ liệu rotten_tomatoes</h2>")
    parts.append(card("Sơ đồ quy trình EDA",
        "Các bước khám phá dữ liệu trước khi huấn luyện; dưới mỗi bước là phát hiện chính rút ra từ dữ liệu thật.",
        flow([
            ("Tải dữ liệu", f"{fmt_int(total)} câu, 3 tập chia sẵn, cột text + label"),
            ("Kiểm tra chất lượng", f"{sum(r['empty'] for r in eda['quality'])} câu rỗng, {dups} câu trùng, "
                                    f"{leak} câu val/test trùng train"),
            ("Phân bố nhãn", "NEG/POS cân bằng 50/50 ở cả 3 tập"),
            ("Độ dài câu", f"TB {avg_all:.1f} từ, dài nhất {max(max(w) for w in words.values())} từ → max_length 128"),
            ("Từ vựng", f"{fmt_int(eda['vocab'][0]['vocab'])} từ ở train; ≤ {oov:.1%} từ val/test chưa gặp"),
            ("Dấu hiệu theo nhãn", f"Phủ định: {neg_cue[1]:.0%} câu NEG so với {neg_cue[2]:.0%} câu POS"),
            ("Kết luận tiền xử lý", "Không cần làm sạch thêm; tokenizer uncased, padding động"),
        ]), wide=True))
    c_q = card("Kiểm tra chất lượng và rò rỉ dữ liệu",
               "Không có câu rỗng, không trùng lặp trong tập, không câu nào của validation/test xuất hiện trong train "
               "(không rò rỉ), nên kết quả test khách quan. Một số câu có ký tự ngoài ASCII: chữ có dấu (é, á, ó…) và vài ký tự "
               "lỗi mã hóa (dấu gạch, dấu ba chấm kiểu Windows-1252) — ít, không ảnh hưởng đáng kể.",
               table(["Tập", "Số câu", "Rỗng", "Trùng trong tập", "Trùng với train", "Có ký tự ngoài ASCII"],
                     [[SPLIT_VI[r["split"]], fmt_int(r["rows"]), r["empty"], r["dup"],
                       "—" if r["split"] == "train" else r["in_train"], r["non_ascii"]] for r in eda["quality"]], "stats"))
    c_v = card("Từ vựng",
               f"Tách từ đơn giản (chữ thường, bỏ dấu câu). {eda['hapax']:.0%} số từ ở train chỉ xuất hiện 1 lần; "
               f"khoảng {oov:.1%} lượt từ ở validation/test không có trong train. WordPiece tách từ lạ thành mảnh nhỏ "
               "nên model vẫn xử lý được.",
               table(["Tập", "Lượt từ", "Số từ khác nhau", "Lượt từ chưa gặp ở train"],
                     [[SPLIT_VI[r["split"]], fmt_int(r["tokens"]), fmt_int(r["vocab"]),
                       "—" if r["split"] == "train" else f"{r['oov']:.2%}"] for r in eda["vocab"]], "stats"))
    parts.append(f'<div class="grid2">{c_q}{c_v}</div>')
    neg_counts = [sum(1 for _, l in data[s] if l == 0) for s in SPLITS]
    pos_counts = [sum(1 for _, l in data[s] if l == 1) for s in SPLITS]
    c1 = card("Số câu theo nhãn ở mỗi tập",
              "Hai nhãn bằng nhau tuyệt đối ở cả 3 tập, nên accuracy là chỉ số đáng tin; "
              "baseline đoán toàn một nhãn chỉ đạt 50%.",
              legend([("NEGATIVE (0)", "--s2"), ("POSITIVE (1)", "--s1")]) +
              grouped_bars([SPLIT_VI[s] for s in SPLITS],
                           [("NEGATIVE", "--s2", neg_counts), ("POSITIVE", "--s1", pos_counts)], "Số câu") +
              details("Xem bảng số liệu", table(["Tập", "NEGATIVE", "POSITIVE", "Tổng"],
                      [[SPLIT_VI[s], fmt_int(n), fmt_int(p), fmt_int(n + p)]
                       for s, n, p in zip(SPLITS, neg_counts, pos_counts)])))

    bins = list(range(0, 65, 5))
    def hist(ws):
        h = [0] * (len(bins) - 1)
        for w in ws:
            h[min(w // 5, len(h) - 1)] += 1
        return h
    tr_neg = hist([len(t.split()) for t, l in data["train"] if l == 0])
    tr_pos = hist([len(t.split()) for t, l in data["train"] if l == 1])
    labels_b = [f"{b}–{b + 4}" for b in bins[:-1]]
    centers = [b + 2 for b in bins[:-1]]
    c2 = card("Độ dài câu (số từ) trên tập train",
              "Câu ngắn, phần lớn 10–30 từ; dài nhất 59 từ, nên max_length = 128 token không cắt mất nội dung. "
              "Hai nhãn có phân bố độ dài gần như trùng nhau: độ dài không giúp đoán cảm xúc.",
              legend([("NEGATIVE", "--s2"), ("POSITIVE", "--s1")]) +
              line_chart(centers, [("NEGATIVE", "--s2", list(zip(centers, tr_neg)), False),
                                   ("POSITIVE", "--s1", list(zip(centers, tr_pos)), False)],
                         "Số từ", "Số câu", fmt_y=lambda v: fmt_int(int(v)),
                         xlabels=[(c, l) for c, l in zip(centers, labels_b)][::2]) +
              details("Xem bảng số liệu", table(["Số từ", "NEGATIVE", "POSITIVE"],
                      [[l, fmt_int(a), fmt_int(b)] for l, a, b in zip(labels_b, tr_neg, tr_pos)])))
    parts.append(f'<div class="grid2">{c1}{c2}</div>')

    stat_rows = []
    for s in SPLITS:
        ws = sorted(words[s])
        q = lambda p: ws[int(p * (len(ws) - 1))]
        stat_rows.append([SPLIT_VI[s], fmt_int(len(ws)), f"{sum(ws) / len(ws):.1f}", q(0), q(0.25), q(0.5), q(0.75), q(1)])
    c3 = card("Thống kê độ dài theo tập",
              "Ba tập có phân bố độ dài giống nhau, nên validation và test đại diện tốt cho train.",
              table(["Tập", "Số câu", "TB", "Min", "Q1", "Trung vị", "Q3", "Max"], stat_rows, "stats"))

    neg_w, pos_w = discriminative_words(data["train"])
    c4 = card("Từ đặc trưng của mỗi lớp (tập train)",
              "Log-odds: từ xuất hiện nhiều ở lớp này hơn lớp kia (đã bỏ từ chức năng, chỉ lấy từ gặp ≥ 25 lần). "
              "Đây là những dấu hiệu mặt chữ model dễ học — và cũng là lý do câu mỉa mai dùng từ khen dễ bị đoán sai.",
              '<div class="pair"><div>' + legend([("Nghiêng về NEGATIVE", "--s2")]) +
              hbars([(w, s, f"{w}: NEG {c0} lần, POS {c1} lần") for w, s, c0, c1 in neg_w], "--s2") +
              "</div><div>" + legend([("Nghiêng về POSITIVE", "--s1")]) +
              hbars([(w, s, f"{w}: POS {c1} lần, NEG {c0} lần") for w, s, c0, c1 in pos_w], "--s1") +
              "</div></div>", wide=True)
    examples = []
    for lab in (0, 1):
        picked = [t for t, l in data["train"] if l == lab and 10 <= len(t.split()) <= 18][:3]
        examples += [[f'<span class="tag">{config.ID2LABEL[lab]}</span>', esc(t)] for t in picked]
    c5 = card("Ví dụ câu trong tập train",
              "Văn bản đã được viết thường và tách dấu câu sẵn (\"it 's\", \" , \").",
              table(["Nhãn", "Câu"], examples))
    parts.append(f'<div class="grid2">{c4}{c3}{c5}</div>')
    c_c = card("Dấu hiệu ngôn ngữ theo nhãn (tập train)",
               f"Câu tiêu cực chứa từ phủ định nhiều hơn ({neg_cue[1]:.1%} so với {neg_cue[2]:.1%}). Nhưng gần 1/5 câu "
               "tích cực cũng có phủ định (\"not bad\"), nên model phải hiểu ngữ cảnh chứ không chỉ đếm từ.",
               legend([("NEGATIVE", "--s2"), ("POSITIVE", "--s1")]) +
               grouped_bars([n.split(" (")[0].replace("Từ nối tương phản ", "") for n, _, _ in eda["cues"]],
                            [("NEGATIVE", "--s2", [a for _, a, _ in eda["cues"]]),
                             ("POSITIVE", "--s1", [b for _, _, b in eda["cues"]])],
                            "% số câu", fmt=lambda v: f"{v:.0%}", ymax=math.ceil(max(max(a, b) for _, a, b in eda["cues"]) * 10 / 4) * 0.4) +
               details("Xem bảng số liệu", table(["Dấu hiệu", "NEGATIVE", "POSITIVE"],
                       [[esc(n), f"{a:.1%}", f"{b:.1%}"] for n, a, b in eda["cues"]])))
    c_k = card("Kết luận EDA",
               "Những gì EDA cho thấy và quyết định tương ứng khi xây dựng model.",
               '<ul class="conclude">'
               f"<li>Nhãn cân bằng → dùng accuracy làm chỉ số chính, kèm F1.</li>"
               f"<li>Dữ liệu sạch, không rò rỉ giữa các tập → dùng nguyên 3 tập chia sẵn, không lọc thêm.</li>"
               f"<li>Câu ngắn (dài nhất {max(max(w) for w in words.values())} từ) → max_length = 128 đủ, padding động để bớt tính toán thừa.</li>"
               "<li>Văn bản đã viết thường, tách dấu câu → hợp với tokenizer <code>uncased</code> của DistilBERT.</li>"
               f"<li>Khoảng {oov:.1%} lượt từ ở validation/test chưa gặp ở train và cảm xúc phụ thuộc ngữ cảnh (phủ định, \"but\") "
               "→ chọn model đã học sẵn ngôn ngữ (transfer learning) thay vì đếm từ.</li>"
               "<li>Từ khen xuất hiện trong câu mỉa mai → dự đoán trước điểm yếu của model với câu mỉa mai.</li></ul>")
    parts.append(f'<div class="grid2">{c_c}{c_k}</div>')

    # ---- Phần 2: huấn luyện
    log = read_json("train_log.json")
    if log:
        parts.append("<h2>2. Quá trình fine-tune</h2>")
        steps_per_epoch = max(e["step"] for e in log["log_history"] if "loss" in e) / log["hyperparameters"]["num_epochs"]
        steps_per_epoch = math.ceil(steps_per_epoch)
        train_pts = [(e["step"], e["loss"]) for e in log["log_history"] if "loss" in e and "step" in e]
        ep = log["epochs"]
        val_pts = [(e["epoch"] * steps_per_epoch, e["val_loss"]) for e in ep]
        c6 = card("Loss theo bước huấn luyện",
                  f"Training loss giảm đều; validation loss thấp nhất ở epoch 1 ({ep[0]['val_loss']:.4f}) rồi tăng "
                  f"lên {ep[-1]['val_loss']:.4f} ở epoch 3 — dấu hiệu overfitting từ epoch 2.",
                  legend([("Training loss (mỗi 50 bước)", "--s1"), ("Validation loss (cuối epoch)", "--s2")]) +
                  line_chart([x for x, _ in train_pts] + [0],
                             [("Training loss", "--s1", train_pts, False),
                              ("Validation loss", "--s2", val_pts, True)],
                             f"Bước ({steps_per_epoch} bước = 1 epoch)", "Loss", ymax=0.8, markers=True,
                             xlabels=[(0, "0")] + [(e["epoch"] * steps_per_epoch,
                                                    f"{e['epoch'] * steps_per_epoch}") for e in ep]) +
                  details("Xem bảng theo epoch", table(
                      ["Epoch", "Train loss", "Val loss", "Val accuracy", "Val F1"],
                      [[e["epoch"], f"{e['train_loss']:.4f}", f"{e['val_loss']:.4f}",
                        f"{e['val_accuracy']:.2%}", f"{e['val_f1']:.2%}"] for e in ep])))
        before = log["validation_before_finetune"]["accuracy"]
        acc_pts = [(0, before)] + [(e["epoch"], e["val_accuracy"]) for e in ep]
        f1_pts = [(e["epoch"], e["val_f1"]) for e in ep]
        c7 = card("Validation accuracy và F1",
                  f"Từ {before:.2%} (lớp phân loại còn ngẫu nhiên) lên {ep[0]['val_accuracy']:.2%} chỉ sau 1 epoch; "
                  f"epoch 2 và 3 gần như không tăng thêm. Script giữ epoch {log['best_epoch']} (accuracy cao nhất).",
                  legend([("Accuracy", "--s1"), ("F1", "--s3")]) +
                  line_chart([0, 1, 2, 3], [("Accuracy", "--s1", acc_pts, False), ("F1", "--s3", f1_pts, False)],
                             "Epoch", "Validation", fmt_y=lambda v: f"{v:.0%}", ymin=0.4, ymax=0.9, nticks=5,
                             xlabels=[(0, "Trước"), (1, "1"), (2, "2"), (3, "3")]))
        parts.append(f'<div class="grid2">{c6}{c7}</div>')

    # ---- Phần 3: đánh giá
    tm = read_json("test_metrics.json")
    mis = read_misclassified()
    if tm:
        parts.append("<h2>3. Đánh giá trên tập test</h2>")
        names = ["Accuracy", "Precision", "Recall", "F1"]
        keys = ["accuracy", "precision", "recall", "f1"]
        b, f = tm["baseline_not_finetuned"], tm["finetuned"]
        c8 = card("Trước và sau fine-tune",
                  f"Cùng kiến trúc, cùng {tm['test_size']} câu test. Baseline gần như chỉ đoán NEGATIVE "
                  f"nên recall POSITIVE chỉ {b['recall']:.2%}.",
                  legend([("Chưa fine-tune", "--s2"), ("Sau fine-tune", "--s1")]) +
                  grouped_bars(names, [("Chưa fine-tune", "--s2", [b[k] for k in keys]),
                                       ("Sau fine-tune", "--s1", [f[k] for k in keys])],
                               "Giá trị", fmt=lambda v: f"{v:.0%}", ymax=1.0) +
                  details("Xem bảng số liệu", table(["Chỉ số", "Chưa fine-tune", "Sau fine-tune"],
                          [[n, f"{b[k]:.2%}", f"{f[k]:.2%}"] for n, k in zip(names, keys)])))
        cm = tm["confusion_matrix"]
        c9 = card("Confusion matrix",
                  f"{cm[0][0] + cm[1][1]} câu đúng, {tm['num_misclassified']} câu sai. Model nhầm POSITIVE → NEGATIVE "
                  f"({cm[1][0]} câu) nhiều hơn chiều ngược lại ({cm[0][1]} câu).",
                  heatmap(cm, ["NEGATIVE", "POSITIVE"]))
        parts.append(f'<div class="grid2">{c8}{c9}</div>')
    if mis:
        cb = [0.5 + 0.05 * i for i in range(10)]
        hist_mis = {"NEGATIVE": [0] * 10, "POSITIVE": [0] * 10}
        for r in mis:
            hist_mis[r["true_label"]][min(int((r["confidence"] - 0.5) / 0.05), 9)] += 1
        high = sum(1 for r in mis if r["confidence"] > 0.9)
        c10 = card("Độ tin cậy của các câu đoán sai",
                   f"{high}/{len(mis)} câu sai có độ tin cậy trên 90%: model sai một cách tự tin, "
                   "nên độ tin cậy cao không bảo đảm dự đoán đúng.",
                   legend([("Thật là NEGATIVE (đoán POS)", "--s2"), ("Thật là POSITIVE (đoán NEG)", "--s1")]) +
                   grouped_bars([f"{c:.2f}" for c in cb],
                                [("Thật NEGATIVE", "--s2", hist_mis["NEGATIVE"]),
                                 ("Thật POSITIVE", "--s1", hist_mis["POSITIVE"])], "Số câu sai") +
                   '<p class="note">Trục ngang: độ tin cậy từ mốc ghi đến mốc kế tiếp (+0,05).</p>')
        top = sorted(mis, key=lambda r: -r["confidence"])[:10]
        c11 = card("10 câu đoán sai tự tin nhất",
                   "Thường là câu mỉa mai, phủ định, hoặc khen chê lẫn lộn.",
                   table(["Câu", "Thật", "Đoán", "Tin cậy"],
                         [[esc(r["text"]), r["true_label"], r["predicted_label"], f"{r['confidence']:.2%}"] for r in top]))
        parts.append(f'<div class="grid2">{c10}{c11}</div>')

    page = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lab 3 Data Visualization</title><style>{CSS}</style></head>
<body><main>
<h1>Lab 3 — Trực quan hóa dữ liệu và kết quả</h1>
<p class="lead">Phân loại cảm xúc review phim (rotten_tomatoes) bằng DistilBERT fine-tune. Số liệu đọc trực tiếp từ
<code>data/rotten_tomatoes/*.csv</code> và <code>results/</code>; di chuột lên biểu đồ để xem giá trị.</p>
{''.join(parts)}
<footer>Tạo bởi <code>python -m src.visualize</code>. Chạy lại lệnh này sau khi train/đánh giá lại để cập nhật.</footer>
</main><div id="tip" role="tooltip"></div><script>{JS}</script></body></html>"""
    return page


def main():
    config.ensure_dirs()
    OUT_FILE.write_text(build(), encoding="utf-8")
    print(f"Đã tạo {OUT_FILE.relative_to(config.ROOT)} — mở bằng trình duyệt để xem.")


if __name__ == "__main__":
    main()
