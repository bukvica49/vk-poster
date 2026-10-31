# Минимальный markdown → HTML. Ноль зависимостей.
import re, html as _html

def md_to_html(text):
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("&", "&amp;").replace("<", "&lt;")
    lines = text.split("\n")
    out, para, list_mode, i = [], [], None, 0

    def flush_para():
        nonlocal para
        if para:
            out.append("<p>" + inline("\n".join(para)) + "</p>")
            para = []

    def close_list():
        nonlocal list_mode
        if list_mode:
            out.append(f"</{list_mode}>")
            list_mode = None

    while i < len(lines):
        ln = lines[i]

        if not ln.strip():
            flush_para(); close_list(); i += 1; continue

        m = re.match(r"^(#{1,6})\s+(.+)$", ln)
        if m:
            flush_para(); close_list()
            n = len(m.group(1))
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
            i += 1; continue

        if re.match(r"^-{3,}\s*$", ln):
            flush_para(); close_list()
            out.append("<hr>"); i += 1; continue

        if ln.startswith(">"):
            flush_para(); close_list()
            q = []
            while i < len(lines) and lines[i].startswith(">"):
                q.append(lines[i][1:].lstrip()); i += 1
            out.append("<blockquote>" + inline("\n".join(q)) + "</blockquote>")
            continue

        m = re.match(r"^[-*+]\s+(.+)$", ln)
        if m:
            flush_para()
            if list_mode != "ul":
                close_list(); out.append("<ul>"); list_mode = "ul"
            out.append("<li>" + inline(m.group(1)) + "</li>")
            i += 1; continue

        m = re.match(r"^\d+\.\s+(.+)$", ln)
        if m:
            flush_para()
            if list_mode != "ol":
                close_list(); out.append("<ol>"); list_mode = "ol"
            out.append("<li>" + inline(m.group(1)) + "</li>")
            i += 1; continue

        close_list(); para.append(ln); i += 1

    flush_para(); close_list()
    return "\n".join(out)


def inline(s):
    codes = []
    def _code(m):
        codes.append(m.group(1)); return f"\x00C{len(codes)-1}\x00"
    s = re.sub(r"`([^`]+)`", _code, s)

    s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",
               r'<img alt="\1" src="\2" loading="lazy">', s)

    def _link(m):
        href = m.group(2)
        if not re.match(r'^(https?://|/|#|mailto:)', href):
            return m.group(1)
        return f'<a href="{href}" rel="noopener" target="_blank">{m.group(1)}</a>'
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link, s)

    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"__([^_]+)__",       r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"(?<!_)_([^_\n]+)_(?!_)",    r"<em>\1</em>", s)

    def _uncode(m): return f"<code>{codes[int(m.group(1))]}</code>"
    return re.sub(r"\x00C(\d+)\x00", _uncode, s)
