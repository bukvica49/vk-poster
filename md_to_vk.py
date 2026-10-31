# Markdown → VK message. Ноль зависимостей.
# VK понимает: **bold**, *italic*, ~~strike~~, __underline__, [url|text], #hashtag
# Не понимает: # H1, > quote, - list, ---
import re


def md_to_vk(text):
    if not text:
        return ""
    s = text.replace("\r\n", "\n").replace("\r", "\n")

    # 1) Картинки: ![alt](url) → url (VK прикрепит отдельно)
    s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"\2", s)

    # 2) Ссылки: [text](url) → [url|text]  (VK-формат)
    def _link(m):
        txt, url = m.group(1), m.group(2)
        return url if txt == url else f"[{url}|{txt}]"
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link, s)

    # 3) Заголовки: ## Text → **Text**
    s = re.sub(r"^#{1,6}\s+(.+)$", r"**\1**", s, flags=re.M)

    # 4) Горизонтальная линия: --- → ———
    s = re.sub(r"^-{3,}\s*$", "———", s, flags=re.M)

    # 5) Цитаты: собираем многстрочные "> a\n> b" → «a b»
    lines = s.split("\n")
    out, i = [], 0
    while i < len(lines):
        if lines[i].lstrip().startswith(">"):
            parts = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                parts.append(lines[i].lstrip().lstrip(">").strip())
                i += 1
            out.append("«" + " ".join(p for p in parts if p) + "»")
        else:
            out.append(lines[i])
            i += 1
    s = "\n".join(out)

    # 6) Списки: - item → • item  (VK не рендерит "-")
    s = re.sub(r"^[-*+]\s+(.+)$", r"• \1", s, flags=re.M)

    # 7) __text__ в markdown = bold, но в VK = underline → конвертим
    s = re.sub(r"__([^_\n]+)__", r"**\1**", s)

    # 8) Схлопываем 3+ пустых строки в 2
    s = re.sub(r"\n{3,}", "\n\n", s)

    return s.strip()
