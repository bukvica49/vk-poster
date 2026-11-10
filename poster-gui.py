#!/usr/bin/env python3
"""Автопостер — настольный интерфейс (Tkinter). Запуск: python3 poster-gui.py"""
import json, subprocess, sys, shutil
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog, filedialog
except ImportError:
    print("Установи tkinter:\n  Debian/Ubuntu: sudo apt install python3-tk\n  Arch: sudo pacman -S tk")
    sys.exit(1)

ROOT   = Path(__file__).resolve().parent
CONTENT = ROOT / "content" / "holidays"
IMAGES  = ROOT / "images"

FIELDS = [
    ("slug",      "Slug",             False),
    ("date",      "Дата MM-DD",       False),
    ("date_to",   "Дата окончания",   False),
    ("post_time", "Время HH:MM или HH-MM", False),
    ("text",      "Заголовок",        False),
    ("text_md",   "Тело (Markdown)",  True),
    ("info",      "Info (по строкам)",True),
    ("image",     "Картинка",         False),
]

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Автопостер — интерфейс")
        self.geometry("1150x750")
        self.current_slug = None
        self.posts = {}
        self.fields = {}
        self._menu()
        self._layout()
        self.refresh()

    def _menu(self):
        mb = tk.Menu(self)
        m = tk.Menu(mb, tearoff=0)
        m.add_command(label="Новый пост",              command=self.new_post)
        m.add_command(label="Обновить список",         command=self.refresh)
        m.add_separator()
        m.add_command(label="Выход",                   command=self.quit)
        mb.add_cascade(label="Файл", menu=m)

        m = tk.Menu(mb, tearoff=0)
        m.add_command(label="Проверить базу (validate)",       command=self.validate)
        m.add_command(label="Опубликовать контент (git push)", command=self.publish)
        m.add_separator()
        m.add_command(label="Проверить, что выйдет сегодня (dry-run)", command=self.dry_run)
        m.add_command(label="Проверить на дату… (dry-run)",            command=self.dry_run_date)
        mb.add_cascade(label="Действия", menu=m)
        self.config(menu=mb)

    def _layout(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # ── левая панель ─────────────────────────────────────
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
        self.tree.bind("<<TreeviewSelect>>",
                       lambda e: self.load_post(self.tree.selection()[0])
                       if self.tree.selection() else None)

        # ── правая панель: форма ─────────────────────────────
        right = ttk.Frame(paned, padding=4)
        paned.add(right, weight=2)
        form = ttk.Frame(right); form.pack(fill=tk.BOTH, expand=True)
        for key, label, multiline in FIELDS:
            row = ttk.Frame(form); row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=label, width=15, anchor=tk.W).pack(side=tk.LEFT)
            w = tk.Text(row, height=4, wrap=tk.WORD) if multiline else ttk.Entry(row)
            w.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.fields[key] = (w, multiline)

        btn = ttk.Frame(right); btn.pack(fill=tk.X, pady=6)
        for txt, cmd in [
            ("💾 Сохранить",   self.save_current),
            ("🗑 Удалить",     self.delete_current),
            ("📷 Картинку",    self.upload_image),
            ("👁 Превью VK",   self.preview_vk),
            ("✅ Проверить",   self.validate),
            ("🚀 Опубликовать",self.publish),
        ]:
            ttk.Button(btn, text=txt, command=cmd).pack(side=tk.LEFT, padx=2)

        # ── лог ─────────────────────────────────────────────
        lf = ttk.Frame(self, padding=(4,0,4,4)); lf.pack(fill=tk.X)
        ttk.Label(lf, text="Лог:", font=("", 9, "bold")).pack(anchor=tk.W)
        self.log = tk.Text(lf, height=8, wrap=tk.WORD, font=("monospace", 9), state=tk.DISABLED)
        self.log.pack(fill=tk.BOTH, expand=True)

        self.status = tk.StringVar(value="Готов")
        ttk.Label(self, textvariable=self.status, relief=tk.SUNKEN,
                  anchor=tk.W).pack(fill=tk.X, side=tk.BOTTOM)

    def log_msg(self, s):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, s + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

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
            st = d.get("slavic_to")
            s_to = f" ({st['month']} {st['day']})" if isinstance(st, dict) and st.get("month") and st.get("day") else ""
            ds = f"{date}→{to}{s_to}" if to else date
            if q and q not in f"{slug} {d.get('text','')} {date}".lower(): continue
            self.tree.insert("", tk.END, iid=slug, values=(ds, slug, d.get("text","")))

    def load_post(self, slug):
        if slug not in self.posts: return
        d = self.posts[slug][1]; self.current_slug = slug
        for k, (w, ml) in self.fields.items():
            v = d.get(k, "")
            if k == "info" and isinstance(v, list): v = "\n".join(v)
            if ml: w.delete("1.0", tk.END); w.insert("1.0", str(v))
            else:  w.delete(0, tk.END);     w.insert(0, str(v))
        self.status.set(f"Выбран: {slug}")

    def save_current(self):
        if not self.current_slug:
            messagebox.showwarning("Внимание", "Выбери пост слева"); return
        f, d_old = self.posts[self.current_slug]
        new = dict(d_old)                       # сохраняем поля, которых нет в FIELDS
        for k, (w, ml) in self.fields.items():
            v = w.get("1.0", tk.END).rstrip("\n") if ml else w.get().strip()
            if k == "info":
                v = [l for l in v.split("\n") if l.strip()]
                if v: new[k] = v
                else: new.pop(k, None)
            elif k in ("slug", "date"):
                if v: new[k] = v                # обязательные — пустые не трогаем
            else:
                if v: new[k] = v
                else: new.pop(k, None)          # пусто = удалить из JSON
        # 🔴 guard: если civil-дата изменилась, старый slavic(_to) не должен
        # пережить сохранение — иначе poster возьмёт его и покажет неверное.
        if new.get("date") != d_old.get("date") and "slavic" in new:
            new.pop("slavic")
            self.log_msg("⚠ date изменился → slavic сброшен (fallback)")
        if new.get("date_to") != d_old.get("date_to") and "slavic_to" in new:
            new.pop("slavic_to")
            self.log_msg("⚠ date_to изменился → slavic_to сброшен (fallback)")
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
        f.write_text(json.dumps({"slug": slug, "date": "", "text": ""},
                                ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.refresh()
        if slug in self.posts: self.tree.selection_set(slug)

    def delete_current(self):
        if not self.current_slug: return
        if not messagebox.askyesno("Удалить?", f"Удалить {self.current_slug}.json?", parent=self): return
        self.posts[self.current_slug][0].unlink()
        self.current_slug = None; self.refresh()

    # ── 📷 загрузка картинки ────────────────────────────────
    def upload_image(self):
        if not self.current_slug:
            messagebox.showwarning("Внимание", "Сначала выбери пост слева"); return
        path = filedialog.askopenfilename(
            title="Выбери картинку",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.webp *.gif"), ("Все файлы", "*.*")],
        )
        if not path: return
        src = Path(path)
        if not src.exists():
            messagebox.showerror("Ошибка", f"Файл не найден: {path}"); return
        IMAGES.mkdir(exist_ok=True)
        dest = IMAGES / src.name
        if dest.exists():
            if not messagebox.askyesno("Перезаписать?", f"{dest.name} уже есть. Заменить?", parent=self):
                return
        try:
            shutil.copy2(src, dest)
        except Exception as e:
            messagebox.showerror("Ошибка копирования", str(e)); return
        w, _ = self.fields['image']
        w.delete(0, tk.END)
        w.insert(0, f"/images/{src.name}")
        self.save_current()
        self.log_msg(f"✓ скопировано → images/{src.name}, image = /images/{src.name}")
        self.status.set(f"Картинка: {src.name}")

    def _form_data(self, slug):
        """Данные из полей формы; пустые поля — из кэша файла.
        Нужно для живого превью: изменения в полях видны без сохранения."""
        base = dict(self.posts[slug][1]) if slug in self.posts else {}
        for k, (w, ml) in self.fields.items():
            v = w.get("1.0", tk.END).rstrip("\n") if ml else w.get().strip()
            if k == "info":
                v = [l for l in v.split("\n") if l.strip()]
                if v: base[k] = v
                else: base.pop(k, None)
            elif k in ("slug", "date"):
                if v: base[k] = v
            else:
                if v: base[k] = v
                else: base.pop(k, None)
        # тот же guard, без логирования (живой превью вызывает часто)
        d_old = self.posts[slug][1] if slug in self.posts else {}
        if base.get("date") != d_old.get("date"): base.pop("slavic", None)
        if base.get("date_to") != d_old.get("date_to"): base.pop("slavic_to", None)
        return base

    # ── 👁 превью VK-поста ─────────────────────────────────
    def preview_vk(self):
        if not self.current_slug:
            messagebox.showwarning("Внимание", "Сначала выбери пост слева"); return
        d = self._form_data(self.current_slug)
        win = tk.Toplevel(self)
        win.title(f"Предпросмотр VK — {self.current_slug}")
        win.geometry("620x780")
        win.minsize(500, 500)

        top = ttk.Frame(win, padding=(10, 8)); top.pack(fill=tk.X)
        ttk.Label(top, text="Так пост будет выглядеть в ВК:",
                  font=("", 10, "bold")).pack(anchor=tk.W)
        ttk.Label(top, text=f"slug: {self.current_slug}  ·  date: {d.get('date','—')}"
                            f"  ·  post_time: {str(d.get('post_time','18:00 (по умолчанию)')).replace('-', ':')}",
                  foreground="#666", font=("", 8)).pack(anchor=tk.W)

        # картинка
        img_field = d.get("image", "").strip()
        if img_field:
            img_path = ROOT / img_field.lstrip("/")
            if img_path.exists():
                loaded = False
                try:
                    from PIL import Image, ImageTk
                    im = Image.open(img_path); im.thumbnail((560, 420))
                    photo = ImageTk.PhotoImage(im)
                    lbl = tk.Label(win, image=photo, bg="#f0f0f0")
                    lbl.image = photo
                    lbl.pack(padx=10, pady=6, fill=tk.X)
                    loaded = True
                except ImportError:
                    pass
                except Exception as e:
                    self.log_msg(f"preview img: {e}")
                if not loaded:
                    ttk.Label(win, text=f"[картинка: {img_field}]  (jpg-превью требует: pip install Pillow)",
                              foreground="#888", font=("", 9, "italic"), padding=10).pack(fill=tk.X)
            else:
                ttk.Label(win, text=f"[картинка не найдена: {img_field}]",
                          foreground="#c33", font=("", 9, "italic"), padding=10).pack(fill=tk.X)

        # тело поста
        body = tk.Frame(win, bg="white", bd=1, relief=tk.SOLID)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        inner = tk.Frame(body, bg="white"); inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        title = d.get("text", "").strip()
        if title:
            tk.Label(inner, text=title, bg="white", fg="#0a0a0a",
                     font=("", 12, "bold"), wraplength=560, justify=tk.LEFT,
                     anchor=tk.W).pack(fill=tk.X, pady=(0, 8))

        md = d.get("text_md", "").strip()
        if md:
            tb = tk.Text(inner, wrap=tk.WORD, font=("", 10), bg="white", bd=0,
                         height=min(20, max(4, md.count("\n") + 1)))
            tb.insert("1.0", md); tb.config(state=tk.DISABLED)
            tb.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        info = d.get("info", [])
        if info:
            info_text = "\n".join(info) if isinstance(info, list) else str(info)
            tk.Frame(inner, bg="#ddd", height=1).pack(fill=tk.X, pady=(6, 6))
            tk.Label(inner, text=info_text, bg="white", fg="#333",
                     font=("", 9), wraplength=560, justify=tk.LEFT,
                     anchor=tk.W).pack(fill=tk.X)

        if not (title or md or info):
            tk.Label(inner, text="(пусто — заполни поля и сохрани)",
                     bg="white", fg="#999", font=("", 10, "italic")).pack(pady=20)

        ttk.Button(win, text="Закрыть", command=win.destroy).pack(pady=8)

    # ── запуск внешних команд ──────────────────────────────
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

    def validate(self):
        self.run(["./ed.py", "validate"], "ed.py validate")

    def publish(self):
        if not messagebox.askyesno(
            "Git publish",
            "validate --strict + git push content/.\n"
            "Сайт обновится за 1-2 мин.\n\n"
            "В ВК НЕ отправится — это делает автопостер (GitHub Actions) по расписанию.\n\n"
            "Продолжить?", parent=self):
            return
        self.run(["./ed.py", "publish"], "ed.py publish")

    def dry_run(self):
        self.run(["python3", "poster.py", "--dry-run"], "poster.py --dry-run")

    def dry_run_date(self):
        d = simpledialog.askstring("Дата", "YYYY-MM-DD:", parent=self)
        if d: self.run(["python3", "poster.py", "--dry-run", "--date", d],
                       f"poster --dry-run --date {d}")

def main():
    if not (ROOT/"ed.py").exists():
        print(f"Нет ed.py рядом с {__file__}. Запускай из корня репо."); sys.exit(1)
    if not CONTENT.is_dir():
        print(f"Нет {CONTENT}"); sys.exit(1)
    App().mainloop()

if __name__ == "__main__":
    main()
