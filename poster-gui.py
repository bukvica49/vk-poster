#!/usr/bin/env python3
"""Автопостер — настольный интерфейс (Tkinter). Запуск: python3 poster-gui.py"""
import json, subprocess, sys
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog
except ImportError:
    print("Установи tkinter:\n  Debian/Ubuntu: sudo apt install python3-tk\n  Arch: sudo pacman -S tk")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content" / "holidays"

FIELDS = [
    ("slug", "Slug", False),
    ("date", "Дата MM-DD", False),
    ("date_to", "Дата окончания", False),
    ("post_time", "Время HH:MM", False),
    ("text", "Заголовок", False),
    ("text_md", "Тело (Markdown)", True),
    ("info", "Info (по строкам)", True),
    ("image", "Картинка", False),
]

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Автопостер — интерфейс")
        self.geometry("1100x720")
        self.current_slug = None
        self.posts = {}
        self.fields = {}
        self._menu()
        self._layout()
        self.refresh()

    def _menu(self):
        mb = tk.Menu(self)
        m = tk.Menu(mb, tearoff=0)
        m.add_command(label="Новый пост", command=self.new_post)
        m.add_command(label="Обновить список", command=self.refresh)
        m.add_separator()
        m.add_command(label="Выход", command=self.quit)
        mb.add_cascade(label="Файл", menu=m)

        m = tk.Menu(mb, tearoff=0)
        m.add_command(label="Проверить базу (validate)", command=self.validate)
        m.add_command(label="Опубликовать контент (git push)", command=self.publish)
        m.add_separator()
        m.add_command(label="Проверить, что выйдет сегодня (dry-run)", command=self.dry_run)
        m.add_command(label="Проверить на дату… (dry-run)", command=self.dry_run_date)
        m.add_separator()
        m.add_command(label="Опубликовать в VK СЕЙЧАС (реальный пост)", command=self.real_publish)
        mb.add_cascade(label="Действия", menu=m)
        self.config(menu=mb)

    def _layout(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(paned, padding=4)
        paned.add(left, weight=1)
        ttk.Label(left, text="Посты", font=("", 10, "bold")).pack(anchor=tk.W)
        sf = ttk.Frame(left); sf.pack(fill=tk.X, pady=2)
        ttk.Label(sf, text="Поиск:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.populate_list())
        ttk.Entry(sf, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.tree = ttk.Treeview(left, columns=("d","s","t"), show="headings")
        for c, txt, w in [("d","Дата",90),("s","Slug",160),("t","Заголовок",250)]:
            self.tree.heading(c, text=txt); self.tree.column(c, width=w)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.load_post(self.tree.selection()[0]) if self.tree.selection() else None)

        right = ttk.Frame(paned, padding=4)
        paned.add(right, weight=2)
        form = ttk.Frame(right); form.pack(fill=tk.BOTH, expand=True)
        for key, label, multiline in FIELDS:
            row = ttk.Frame(form); row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=label, width=15, anchor=tk.W).pack(side=tk.LEFT)
            if multiline:
                w = tk.Text(row, height=4, wrap=tk.WORD)
            else:
                w = ttk.Entry(row)
            w.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.fields[key] = (w, multiline)
        btn = ttk.Frame(right); btn.pack(fill=tk.X, pady=6)
        for txt, cmd in [("💾 Сохранить", self.save_current), ("🗑 Удалить", self.delete_current),
                         ("✅ Проверить", self.validate), ("🚀 Опубликовать", self.publish)]:
            ttk.Button(btn, text=txt, command=cmd).pack(side=tk.LEFT, padx=2)

        lf = ttk.Frame(self, padding=(4,0,4,4)); lf.pack(fill=tk.X)
        ttk.Label(lf, text="Лог:", font=("", 9, "bold")).pack(anchor=tk.W)
        self.log = tk.Text(lf, height=8, wrap=tk.WORD, font=("monospace", 9), state=tk.DISABLED)
        self.log.pack(fill=tk.BOTH, expand=True)

        self.status = tk.StringVar(value="Готов")
        ttk.Label(self, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, side=tk.BOTTOM)

    def log_msg(self, s):
        self.log.config(state=tk.NORMAL); self.log.insert(tk.END, s + "\n")
        self.log.see(tk.END); self.log.config(state=tk.DISABLED)

    def refresh(self):
        self.posts = {}
        for f in sorted(CONTENT.glob("*.json")):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                self.posts[d.get("slug", f.stem)] = (f, d)
            except Exception as e:
                self.log_msg(f"! {f.name}: {e}")
        self.populate_list()
        self.status.set(f"Постов: {len(self.posts)}")

    def populate_list(self):
        self.tree.delete(*self.tree.get_children())
        q = self.search_var.get().lower()
        for slug, (_, d) in sorted(self.posts.items(), key=lambda x: x[1][1].get("date","")):
            date = d.get("date",""); to = d.get("date_to","")
            ds = f"{date}→{to}" if to else date
            if q and q not in f"{slug} {d.get('text','')} {date}".lower(): continue
            self.tree.insert("", tk.END, iid=slug, values=(ds, slug, d.get("text","")))

    def load_post(self, slug):
        if slug not in self.posts: return
        d = self.posts[slug][1]; self.current_slug = slug
        for k, (w, ml) in self.fields.items():
            v = d.get(k, "")
            if k == "info" and isinstance(v, list): v = "\n".join(v)
            if ml: w.delete("1.0", tk.END); w.insert("1.0", str(v))
            else: w.delete(0, tk.END); w.insert(0, str(v))
        self.status.set(f"Выбран: {slug}")

    def save_current(self):
        if not self.current_slug:
            messagebox.showwarning("Внимание", "Выбери пост слева"); return
        f = self.posts[self.current_slug][0]; new = {}
        for k, (w, ml) in self.fields.items():
            v = w.get("1.0", tk.END).rstrip("\n") if ml else w.get().strip()
            if not v: continue
            if k == "info": v = [l for l in v.split("\n") if l.strip()]
            new[k] = v
        try:
            f.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            self.log_msg(f"✓ {f.name}"); self.refresh()
            if self.current_slug in self.posts: self.tree.selection_set(self.current_slug)
        except Exception as e:
            self.log_msg(f"✗ {e}"); messagebox.showerror("Ошибка", str(e))

    def new_post(self):
        slug = simpledialog.askstring("Новый пост", "Slug (латиницей):", parent=self)
        if not slug: return
        slug = slug.strip(); f = CONTENT / f"{slug}.json"
        if f.exists(): messagebox.showerror("Ошибка", f"Уже есть: {f.name}"); return
        f.write_text(json.dumps({"slug": slug, "date": "", "text": ""}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.refresh()
        if slug in self.posts: self.tree.selection_set(slug)

    def delete_current(self):
        if not self.current_slug: return
        if not messagebox.askyesno("Удалить?", f"Удалить {self.current_slug}.json?", parent=self): return
        self.posts[self.current_slug][0].unlink(); self.current_slug = None; self.refresh()

    def run(self, cmd, label):
        self.log_msg(f"$ {label}")
        try:
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=180)
            if r.stdout: self.log_msg(r.stdout)
            if r.stderr: self.log_msg("STDERR: " + r.stderr)
            if r.returncode != 0: self.log_msg(f"exit={r.returncode}")
        except FileNotFoundError:
            self.log_msg(f"✗ не найдено: {cmd[0]}")
        except Exception as e:
            self.log_msg(f"✗ {e}")

    def validate(self): self.run(["./ed.py", "validate"], "ed.py validate")
    def publish(self):
        if not messagebox.askyesno("Git publish", "validate --strict + git push content/. Сайт обновится за 1-2 мин. Продолжить?"): return
        self.run(["./ed.py", "publish"], "ed.py publish")
    def dry_run(self): self.run(["python3", "poster.py", "--dry-run"], "poster.py --dry-run")
    def dry_run_date(self):
        d = simpledialog.askstring("Дата", "YYYY-MM-DD:", parent=self)
        if d: self.run(["python3", "poster.py", "--dry-run", "--date", d], f"poster --dry-run --date {d}")
    def real_publish(self):
        if not messagebox.askyesno("⚠️ РЕАЛЬНЫЙ ПОСТ В VK", "Это отправит пост в VK прямо сейчас. Продолжить?", parent=self): return
        self.run(["python3", "poster.py"], "poster.py")

def main():
    if not (ROOT/"ed.py").exists():
        print(f"Нет ed.py рядом с {__file__}. Запускай из корня репо."); sys.exit(1)
    if not CONTENT.is_dir():
        print(f"Нет {CONTENT}"); sys.exit(1)
    App().mainloop()

if __name__ == "__main__":
    main()
