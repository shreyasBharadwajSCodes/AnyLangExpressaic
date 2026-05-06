import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONCEPT = PROJECT_ROOT / "templates" / "vis2_welcome_template.yaml"
CONFIG_FILE = PROJECT_ROOT / "vis2_config.yaml"

APP_BG = "#f4f6f8"
SURFACE = "#ffffff"
SURFACE_ALT = "#eef2f6"
INK = "#17202a"
MUTED = "#64748b"
LINE = "#d7dee8"
ACCENT = "#2563eb"
ACCENT_DARK = "#1d4ed8"
GREEN = "#148f65"
AMBER = "#b45309"
RED = "#b42318"
PURPLE = "#6d28d9"
CODE_BG = "#111827"
CODE_FG = "#e5e7eb"


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data if isinstance(data, dict) else {}


def clean_title(value):
    return str(value).replace("_", " ").replace("-", " ").title()


def language_key(value):
    text = str(value).strip().lower()
    aliases = {
        "c++": "cpp",
        "c plus plus": "cpp",
        "py": "python",
        "js": "javascript",
    }
    return aliases.get(text, text)


def column_language_key(value, languages):
    text = str(value).strip().lower()
    exact = language_key(text)
    if exact in languages:
        return exact

    for language in languages:
        labels = {language, clean_title(language).lower()}
        if language == "cpp":
            labels.update({"c++", "c plus plus"})
        if language == "python":
            labels.add("py")
        if language == "javascript":
            labels.add("js")

        if any(text.startswith(label) for label in labels):
            return language

    return None


def language_value(data, language):
    if language in data:
        return data.get(language)

    aliases = {
        "cpp": ["c++", "c_plus_plus"],
        "python": ["py"],
        "javascript": ["js"],
    }
    for alias in aliases.get(language, []):
        if alias in data:
            return data.get(alias)

    return None


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def block_name(block):
    if not isinstance(block, dict) or not block:
        return "text", block
    key = next(iter(block))
    return key, block.get(key)


class ScrollFrame(ttk.Frame):
    def __init__(self, parent, bg=APP_BG):
        super().__init__(parent)
        self.mouse_active = False
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<Enter>", self._activate_mousewheel)
        self.canvas.bind("<Leave>", self._deactivate_mousewheel)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_inner_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        if not self.mouse_active:
            return
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear(self):
        for child in self.inner.winfo_children():
            child.destroy()
        self.canvas.yview_moveto(0)

    def _activate_mousewheel(self, _event=None):
        self.mouse_active = True

    def _deactivate_mousewheel(self, _event=None):
        self.mouse_active = False


class Vis2App:
    def __init__(self, root):
        self.root = root
        self.root.title("AnyLanguageExpressaic Vis2")
        self.root.geometry("1420x860")
        self.root.minsize(1050, 680)
        self.root.configure(bg=APP_BG)

        self.current_file = None
        self.base_folder = None
        self.concept = {}
        self.image_refs = []
        self.yaml_files = []
        self.available_languages = []
        self.language_vars = {}

        self.mode_var = tk.StringVar(value="lesson")
        self.source_var = tk.StringVar()
        self.target_var = tk.StringVar()

        self._setup_style()
        self._build_layout()
        self.bind_shortcuts()

        if not self.load_last_session() and DEFAULT_CONCEPT.exists():
            self.load_file(DEFAULT_CONCEPT)

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=APP_BG)
        style.configure("Sidebar.TFrame", background=SURFACE_ALT)
        style.configure("TButton", font=("Segoe UI", 10), padding=(10, 6))
        style.configure("Primary.TButton", background=ACCENT, foreground="white")
        style.map("Primary.TButton", background=[("active", ACCENT_DARK)])
        style.configure("TCombobox", padding=5)
        style.configure("Mode.TRadiobutton", background=SURFACE_ALT, foreground=INK, font=("Segoe UI", 10, "bold"))

    def _build_layout(self):
        header = tk.Frame(self.root, bg=INK)
        header.pack(fill=tk.X)

        title_area = tk.Frame(header, bg=INK)
        title_area.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=18, pady=14)

        self.title_label = tk.Label(
            title_area,
            text="Vis2",
            bg=INK,
            fg="white",
            font=("Segoe UI", 20, "bold"),
            anchor="w",
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = tk.Label(
            title_area,
            text="Component lesson visualizer",
            bg=INK,
            fg="#cbd5e1",
            font=("Segoe UI", 10),
            anchor="w",
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))

        body = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.sidebar_shell = ttk.Frame(body, style="Sidebar.TFrame", width=330)
        body.add(self.sidebar_shell, weight=0)
        self.main = ttk.Frame(body)
        body.add(self.main, weight=5)

        self.sidebar = tk.Frame(self.sidebar_shell, bg=SURFACE_ALT)
        self.sidebar.pack(fill=tk.BOTH, expand=True)

        self._build_sidebar()
        self.content = ScrollFrame(self.main)
        self.content.pack(fill=tk.BOTH, expand=True)

    def _build_sidebar(self):
        tk.Label(
            self.sidebar,
            text="YAML Files",
            bg=SURFACE_ALT,
            fg=INK,
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", padx=14, pady=(16, 8))

        ttk.Button(
            self.sidebar,
            text="Open Folder",
            command=self.open_folder,
            style="Primary.TButton",
        ).pack(fill=tk.X, padx=14, pady=(0, 8))

        file_area = tk.Frame(self.sidebar, bg=SURFACE_ALT)
        file_area.pack(fill=tk.X, padx=14, pady=(0, 18))

        self.file_list = tk.Listbox(
            file_area,
            height=9,
            bg="white",
            fg=INK,
            selectbackground=ACCENT,
            selectforeground="white",
            activestyle="none",
            relief=tk.FLAT,
            font=("Segoe UI", 10),
            exportselection=False,
        )
        file_scroll = ttk.Scrollbar(file_area, orient="vertical", command=self.file_list.yview)
        self.file_list.configure(yscrollcommand=file_scroll.set)
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_list.bind("<<ListboxSelect>>", self.on_file_select)
        self.file_list.bind("<Up>", lambda _event: self.select_relative_file(-1))
        self.file_list.bind("<Down>", lambda _event: self.select_relative_file(1))
        self.file_list.bind("<Prior>", lambda _event: self.select_relative_file(-8))
        self.file_list.bind("<Next>", lambda _event: self.select_relative_file(8))
        self.file_list.bind("<Home>", lambda _event: self.select_file_at(0))
        self.file_list.bind("<End>", lambda _event: self.select_file_at(len(self.yaml_files) - 1))

        tk.Label(
            self.sidebar,
            text="View",
            bg=SURFACE_ALT,
            fg=INK,
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", padx=14, pady=(0, 8))

        for label, value in [
            ("Lesson", "lesson"),
            ("Revision", "revision"),
            ("Transition", "transition"),
            ("Raw Structure", "raw"),
        ]:
            ttk.Radiobutton(
                self.sidebar,
                text=label,
                value=value,
                variable=self.mode_var,
                command=self.render,
                style="Mode.TRadiobutton",
            ).pack(anchor="w", padx=14, pady=4)

        self.blank_sections_space = tk.Frame(self.sidebar, bg=SURFACE_ALT)
        self.blank_sections_space.pack(fill=tk.BOTH, expand=True)

    def bind_shortcuts(self):
        self.root.bind("<Control-o>", lambda _event: self.open_folder())
        self.root.bind("<Control-O>", lambda _event: self.open_folder())
        self.root.bind("<Control-r>", lambda _event: self.reload_current_file())
        self.root.bind("<Control-R>", lambda _event: self.reload_current_file())

        self.root.bind("<Control-Key-1>", lambda _event: self.set_mode("lesson"))
        self.root.bind("<Control-Key-2>", lambda _event: self.set_mode("revision"))
        self.root.bind("<Control-Key-3>", lambda _event: self.set_mode("transition"))
        self.root.bind("<Control-Key-4>", lambda _event: self.set_mode("raw"))

        self.root.bind("<Up>", lambda _event: self.select_relative_file(-1))
        self.root.bind("<Down>", lambda _event: self.select_relative_file(1))
        self.root.bind("<Control-Left>", lambda _event: self.select_relative_mode(-1))
        self.root.bind("<Control-Right>", lambda _event: self.select_relative_mode(1))
        self.root.bind("<Control-Return>", lambda _event: self.show_transition())
        self.root.bind("<Control-t>", lambda _event: self.show_transition())
        self.root.bind("<Control-T>", lambda _event: self.show_transition())
        self.root.bind("<Control-Shift-T>", lambda _event: self.swap_transition_languages())

    def load_app_config(self):
        if not CONFIG_FILE.exists():
            return {}

        try:
            config = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
            return config if isinstance(config, dict) else {}
        except Exception:
            return {}

    def save_app_config(self):
        if not self.base_folder:
            return

        last_yaml_file = ""
        if self.current_file:
            try:
                last_yaml_file = str(self.current_file.relative_to(self.base_folder))
            except ValueError:
                last_yaml_file = ""

        config = {
            "last_yaml_folder": str(self.base_folder),
            "last_yaml_file": last_yaml_file,
        }

        try:
            CONFIG_FILE.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
        except Exception as error:
            messagebox.showwarning("Config Save Failed", str(error))

    def load_last_session(self):
        config = self.load_app_config()
        folder = config.get("last_yaml_folder")

        if not folder:
            return False

        folder_path = Path(folder)
        if not folder_path.exists() or not folder_path.is_dir():
            return False

        self.load_folder(folder_path, preferred_file=config.get("last_yaml_file"), save_config=False)
        return True

    def open_folder(self):
        folder = filedialog.askdirectory(title="Open YAML folder")
        if not folder:
            return

        self.load_folder(Path(folder))

    def load_folder(self, folder, preferred_file=None, save_config=True):
        self.base_folder = Path(folder)
        self.populate_file_list(preferred_file=preferred_file)
        if save_config:
            self.save_app_config()

    def populate_file_list(self, preferred_file=None):
        self.file_list.delete(0, tk.END)

        if not self.base_folder:
            return

        self.yaml_files = sorted(
            [
                path
                for path in self.base_folder.rglob("*")
                if path.is_file() and path.suffix.lower() in {".yaml", ".yml"}
            ],
            key=lambda path: str(path.relative_to(self.base_folder)).lower(),
        )

        for path in self.yaml_files:
            label = str(path.relative_to(self.base_folder))
            self.file_list.insert(tk.END, label)

        if not self.yaml_files:
            messagebox.showinfo("No YAML files", "This folder does not contain any .yaml or .yml files.")
            return

        selected_index = 0
        if preferred_file:
            for index, path in enumerate(self.yaml_files):
                if str(path.relative_to(self.base_folder)) == preferred_file:
                    selected_index = index
                    break

        self.select_file_at(selected_index)

    def on_file_select(self, _event=None):
        if not self.base_folder:
            return

        selection = self.file_list.curselection()
        if not selection:
            return

        relative_path = self.file_list.get(selection[0])
        self.load_file(self.base_folder / relative_path)

    def select_file_at(self, index):
        if not self.yaml_files:
            return "break"

        index = max(0, min(index, len(self.yaml_files) - 1))
        self.file_list.selection_clear(0, tk.END)
        self.file_list.selection_set(index)
        self.file_list.activate(index)
        self.file_list.see(index)
        self.load_file(self.yaml_files[index])
        return "break"

    def select_relative_file(self, offset):
        if not self.yaml_files:
            return "break"

        selection = self.file_list.curselection()
        current = selection[0] if selection else 0
        self.select_file_at(current + offset)
        return "break"

    def load_file(self, path):
        try:
            self.concept = load_yaml(path)
            self.current_file = Path(path)
        except Exception as error:
            messagebox.showerror("Could not load YAML", str(error))
            return

        title = self.concept.get("title") or clean_title(self.concept.get("id", "Untitled Concept"))
        self.title_label.config(text=title)
        self.subtitle_label.config(text=str(self.current_file))
        self._populate_languages()
        self.render()
        self.save_app_config()

    def reload_current_file(self):
        if self.current_file:
            self.load_file(self.current_file)
        return "break"

    def _populate_languages(self):
        languages = self.concept.get("languages", [])
        if isinstance(languages, dict):
            languages = list(languages.keys())

        self.available_languages = [language_key(language) for language in languages]
        old_vars = self.language_vars
        self.language_vars = {
            language: old_vars.get(language, tk.BooleanVar(value=True))
            for language in self.available_languages
        }

        if languages:
            if self.source_var.get() not in self.available_languages:
                self.source_var.set(self.available_languages[0])
            if self.target_var.get() not in self.available_languages:
                self.target_var.set(self.available_languages[1] if len(self.available_languages) > 1 else self.available_languages[0])

    def show_transition(self):
        return self.set_mode("transition")

    def set_mode(self, mode):
        self.mode_var.set(mode)
        self.render()
        return "break"

    def select_relative_mode(self, offset):
        modes = ["lesson", "revision", "transition", "raw"]
        current = self.mode_var.get()
        try:
            index = modes.index(current)
        except ValueError:
            index = 0

        self.set_mode(modes[(index + offset) % len(modes)])
        return "break"

    def swap_transition_languages(self):
        source = self.source_var.get()
        target = self.target_var.get()
        self.source_var.set(target)
        self.target_var.set(source)
        self.set_mode("transition")
        return "break"

    def render(self):
        self.image_refs = []
        self.content.clear()

        if not self.concept:
            self._empty_state("Open a component-style YAML concept to begin.")
            return

        mode = self.mode_var.get()
        if mode == "lesson":
            self._render_lesson()
        elif mode == "revision":
            self._render_revision()
        elif mode == "transition":
            self._render_transition()
        else:
            self._render_raw()

    def _page_title(self, eyebrow, title, body=None):
        panel = tk.Frame(self.content.inner, bg=APP_BG)
        panel.pack(fill=tk.X, padx=18, pady=(8, 14))

        tk.Label(panel, text=eyebrow.upper(), bg=APP_BG, fg=ACCENT, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(panel, text=title, bg=APP_BG, fg=INK, font=("Segoe UI", 24, "bold"), anchor="w").pack(anchor="w")
        if body:
            tk.Label(
                panel,
                text=body,
                bg=APP_BG,
                fg=MUTED,
                font=("Segoe UI", 11),
                wraplength=980,
                justify="left",
            ).pack(anchor="w", pady=(6, 0))

    def _card(self, title=None, accent=ACCENT):
        outer = tk.Frame(self.content.inner, bg=APP_BG)
        outer.pack(fill=tk.X, padx=18, pady=8)

        stripe = tk.Frame(outer, bg=accent, width=5)
        stripe.pack(side=tk.LEFT, fill=tk.Y)

        card = tk.Frame(outer, bg=SURFACE, padx=16, pady=14, highlightbackground=LINE, highlightthickness=1)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if title:
            tk.Label(
                card,
                text=title,
                bg=SURFACE,
                fg=accent,
                font=("Segoe UI", 14, "bold"),
                anchor="w",
            ).pack(anchor="w", fill=tk.X, pady=(0, 8))
        return card

    def _text(self, parent, text, size=10, color=INK, bold=False, mono=False):
        if not text:
            return
        font_family = "Consolas" if mono else "Segoe UI"
        font = (font_family, size, "bold") if bold else (font_family, size)
        tk.Label(
            parent,
            text=str(text).strip(),
            bg=parent.cget("bg"),
            fg=color,
            font=font,
            wraplength=980,
            justify="left",
            anchor="w",
        ).pack(anchor="w", fill=tk.X, pady=2)

    def _bullet_list(self, parent, items):
        for item in as_list(items):
            if self._hidden_language_text(item):
                continue
            if isinstance(item, dict):
                if item:
                    first = True
                    for key, value in item.items():
                        label = clean_title(key)
                        color = MUTED if first else INK
                        self._text(parent, f"{label}: {value}", color=color, bold=not first)
                        first = False
                    continue
            self._text(parent, f"- {item}")

    def _hidden_language_text(self, item):
        if not isinstance(item, str) or not self.available_languages:
            return False

        selected = set(self.selected_languages())
        if not selected:
            return True

        text = item.strip().lower()
        for language in self.available_languages:
            labels = {language, clean_title(language).lower()}
            if language == "cpp":
                labels.add("c++")
            if any(text.startswith(label) for label in labels):
                return language not in selected

        return False

    def selected_languages(self):
        return [
            language
            for language in self.available_languages
            if self.language_vars.get(language) and self.language_vars[language].get()
        ]

    def _language_filter(self):
        if not self.available_languages:
            return

        bar = tk.Frame(self.content.inner, bg=APP_BG)
        bar.pack(fill=tk.X, padx=18, pady=(0, 8))

        tk.Label(
            bar,
            text="Visible languages",
            bg=APP_BG,
            fg=MUTED,
            font=("Segoe UI", 10, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 8))

        selected_languages = self.selected_languages()
        if not selected_languages:
            selected = "No languages selected"
        elif len(selected_languages) <= 3:
            selected = ", ".join(clean_title(language) for language in selected_languages)
        else:
            first_labels = ", ".join(clean_title(language) for language in selected_languages[:2])
            selected = f"{first_labels} +{len(selected_languages) - 2}"
        menu_button = tk.Menubutton(
            bar,
            text=selected,
            bg=SURFACE,
            fg=INK,
            activebackground="#e0e7ff",
            activeforeground=INK,
            relief=tk.SOLID,
            borderwidth=1,
            font=("Segoe UI", 10),
            padx=10,
            pady=5,
            anchor="w",
        )
        menu = tk.Menu(menu_button, tearoff=False)
        menu_button.config(menu=menu)

        for language in self.available_languages:
            menu.add_checkbutton(
                label=clean_title(language),
                variable=self.language_vars[language],
                command=self.render,
            )

        menu.add_separator()
        menu.add_command(label="Show all", command=self.show_all_languages)
        menu_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def show_all_languages(self):
        for variable in self.language_vars.values():
            variable.set(True)
        self.render()

    def _render_lesson(self):
        self._page_title(
            "Lesson Mode",
            self.concept.get("title", "Untitled Concept"),
            self.concept.get("goal"),
        )
        self._language_filter()

        for block in self.concept.get("lesson", []):
            self._render_component(block)

        if self.concept.get("examples"):
            self._section_heading("Examples")
            for block in self.concept.get("examples", []):
                self._render_component(block)

    def _render_revision(self):
        revision = self.concept.get("revision", {})
        self._page_title("Revision Mode", self.concept.get("title", "Untitled Concept"), "Fast review material.")
        self._language_filter()

        if revision.get("quick_summary"):
            card = self._card("Quick Summary", GREEN)
            self._bullet_list(card, revision.get("quick_summary"))

        if revision.get("cheat_table"):
            self._render_table(revision["cheat_table"], accent=PURPLE)

        if revision.get("flashcards"):
            card = self._card("Flashcards", AMBER)
            for index, item in enumerate(revision["flashcards"], start=1):
                q = item.get("question", "")
                a = item.get("answer", "")
                self._text(card, f"{index}. {q}", bold=True)
                self._text(card, a, color=MUTED)

    def _render_transition(self):
        selected = self.selected_languages()
        if selected and self.source_var.get() not in selected:
            self.source_var.set(selected[0])
        if selected and self.target_var.get() not in selected:
            fallback = selected[1] if len(selected) > 1 else selected[0]
            self.target_var.set(fallback)

        source = self.source_var.get()
        target = self.target_var.get()
        key = f"{source}_to_{target}"
        transition = self.concept.get("transitions", {}).get(key)

        self._page_title(
            "Transition Mode",
            clean_title(key),
            "How to change habits when moving from one language to another.",
        )

        self._language_filter()
        self._transition_controls()

        if len(selected) < 2:
            self._empty_state("Select at least two visible languages to compare a transition path.")
            return

        if not transition:
            self._empty_state(f"No transition path found for '{key}'.")
            return

        card = self._card(transition.get("title", clean_title(key)), PURPLE)

        if transition.get("mindset_shift"):
            self._mini_heading(card, "Mindset Shift")
            self._bullet_list(card, transition.get("mindset_shift"))

        if transition.get("habit_swaps"):
            self._mini_heading(card, "Habit Swaps")
            self._bullet_list(card, transition.get("habit_swaps"))

        if transition.get("false_friends"):
            self._mini_heading(card, "False Friends")
            for item in transition.get("false_friends", []):
                self._text(card, item.get("term", ""), bold=True, color=RED)
                self._text(card, item.get("warning", ""), color=INK)

    def _transition_controls(self):
        visible_languages = self.selected_languages()
        if not visible_languages:
            return

        card = self._card("Transition Path", ACCENT)
        row = tk.Frame(card, bg=SURFACE)
        row.pack(fill=tk.X)

        tk.Label(row, text="From", bg=SURFACE, fg=MUTED, font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        source_combo = ttk.Combobox(row, textvariable=self.source_var, state="readonly", values=visible_languages)
        source_combo.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        source_combo.bind("<<ComboboxSelected>>", lambda _event: self.show_transition())

        tk.Label(row, text="To", bg=SURFACE, fg=MUTED, font=("Segoe UI", 10, "bold")).grid(
            row=0, column=1, sticky="w", padx=(0, 8)
        )
        target_combo = ttk.Combobox(row, textvariable=self.target_var, state="readonly", values=visible_languages)
        target_combo.grid(row=1, column=1, sticky="ew", padx=(0, 10))
        target_combo.bind("<<ComboboxSelected>>", lambda _event: self.show_transition())

        ttk.Button(row, text="Show Path", command=self.show_transition).grid(row=1, column=2, sticky="ew")
        ttk.Button(row, text="Swap", command=self.swap_transition_languages).grid(row=1, column=3, sticky="ew", padx=(8, 0))

        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)

    def _render_raw(self):
        self._page_title("Raw Structure", self.concept.get("title", "Untitled Concept"))
        self._language_filter()
        card = self._card("Filtered YAML Preview", ACCENT)
        text = yaml.safe_dump(self._filtered_raw_concept(), sort_keys=False, allow_unicode=True)
        box = tk.Text(card, height=34, bg=CODE_BG, fg=CODE_FG, insertbackground="white", font=("Consolas", 10))
        box.pack(fill=tk.BOTH, expand=True)
        box.insert("1.0", text)
        box.config(state=tk.DISABLED)

    def _filtered_raw_concept(self):
        selected = set(self.selected_languages())
        if not selected:
            return {
                key: value
                for key, value in self.concept.items()
                if key not in {"languages", "lesson", "examples", "transitions", "revision"}
            }

        filtered = dict(self.concept)
        languages = self.concept.get("languages", [])
        if isinstance(languages, dict):
            filtered["languages"] = {
                key: value
                for key, value in languages.items()
                if language_key(key) in selected
            }
        else:
            filtered["languages"] = [
                language
                for language in languages
                if language_key(language) in selected
            ]

        filtered["lesson"] = self._filter_blocks(self.concept.get("lesson", []), selected)
        filtered["examples"] = self._filter_blocks(self.concept.get("examples", []), selected)

        transitions = {}
        for key, value in self.concept.get("transitions", {}).items():
            parts = key.split("_to_")
            if len(parts) == 2 and parts[0] in selected and parts[1] in selected:
                transitions[key] = value
        filtered["transitions"] = transitions

        if isinstance(self.concept.get("revision"), dict):
            revision = dict(self.concept["revision"])
            if revision.get("cheat_table"):
                columns, rows = self._visible_table_data(
                    revision["cheat_table"].get("columns", []),
                    revision["cheat_table"].get("rows", []),
                )
                revision["cheat_table"] = dict(revision["cheat_table"])
                revision["cheat_table"]["columns"] = columns
                revision["cheat_table"]["rows"] = rows
            filtered["revision"] = revision

        return filtered

    def _filter_blocks(self, blocks, selected):
        filtered = []
        for block in blocks:
            kind, data = block_name(block)
            if not isinstance(data, dict):
                filtered.append(block)
                continue

            if kind == "language_lens" and language_key(data.get("language", "")) not in selected:
                continue

            if kind == "code_compare":
                next_data = {}
                for key, value in data.items():
                    key_language = column_language_key(key, self.available_languages)
                    if key_language is None or key_language in selected:
                        next_data[key] = value
                filtered.append({kind: next_data})
                continue

            if kind in {"compare_table", "table"}:
                columns, rows = self._visible_table_data(data.get("columns", []), data.get("rows", []))
                next_data = dict(data)
                next_data["columns"] = columns
                next_data["rows"] = rows
                filtered.append({kind: next_data})
                continue

            filtered.append(block)
        return filtered

    def _render_component(self, block):
        kind, data = block_name(block)
        data = data if isinstance(data, dict) else {"body": data}

        if kind == "explain":
            card = self._card(data.get("title", "Explanation"), ACCENT)
            self._text(card, data.get("body"), size=11)
        elif kind == "image":
            self._render_image(data)
        elif kind in ("compare_table", "table"):
            self._render_table(data)
        elif kind == "language_lens":
            if language_key(data.get("language", "")) not in self.selected_languages():
                return
            self._render_language_lens(data)
        elif kind == "code_compare":
            self._render_code_compare(data)
        else:
            card = self._card(clean_title(kind), MUTED)
            self._render_dict(card, data)

    def _render_language_lens(self, data):
        language = clean_title(data.get("language", "language"))
        card = self._card(data.get("title", f"{language} Lens"), GREEN)
        self._text(card, data.get("body"), size=11)

        if data.get("default_instincts"):
            self._mini_heading(card, "Default Instincts")
            self._bullet_list(card, data.get("default_instincts"))

        if data.get("avoid"):
            self._mini_heading(card, "Avoid")
            self._bullet_list(card, data.get("avoid"))

    def _render_code_compare(self, data):
        card = self._card(data.get("title", "Code Comparison"), AMBER)
        self._text(card, data.get("idea"), color=MUTED)

        grid = tk.Frame(card, bg=SURFACE)
        grid.pack(fill=tk.X, pady=(8, 6))

        languages = [language for language in self.selected_languages() if language_value(data, language)]
        if not languages:
            self._text(card, "No selected languages are available for this example.", color=MUTED)
            return
        for column, language in enumerate(languages):
            grid.grid_columnconfigure(column, weight=1, uniform="code")
            cell = tk.Frame(grid, bg=CODE_BG, padx=10, pady=8)
            cell.grid(row=0, column=column, sticky="nsew", padx=4)
            tk.Label(
                cell,
                text=language.upper(),
                bg=CODE_BG,
                fg="#93c5fd",
                font=("Segoe UI", 9, "bold"),
                anchor="w",
            ).pack(anchor="w")
            tk.Label(
                cell,
                text=str(language_value(data, language)).rstrip(),
                bg=CODE_BG,
                fg=CODE_FG,
                font=("Consolas", 10),
                justify="left",
                anchor="nw",
                wraplength=300,
            ).pack(anchor="nw", fill=tk.BOTH, expand=True, pady=(6, 0))

        self._text(card, data.get("note"), color=MUTED)

    def _render_table(self, data, accent=ACCENT):
        card = self._card(data.get("title", "Table"), accent)
        columns, rows = self._visible_table_data(data.get("columns", []), data.get("rows", []))

        table = tk.Frame(card, bg=LINE)
        table.pack(fill=tk.X, pady=(4, 0))

        for column, name in enumerate(columns):
            table.grid_columnconfigure(column, weight=1, uniform="table")
            self._table_cell(table, name, 0, column, header=True)

        for row_index, row in enumerate(rows, start=1):
            for column, value in enumerate(row):
                self._table_cell(table, value, row_index, column)

    def _visible_table_data(self, columns, rows):
        if not self.available_languages:
            return columns, rows

        selected = set(self.selected_languages())
        available = set(self.available_languages)
        visible_indexes = []

        for index, column in enumerate(columns):
            key = column_language_key(column, available)
            if key is None or key in selected:
                visible_indexes.append(index)

        visible_columns = [columns[index] for index in visible_indexes]
        visible_rows = []

        for row in rows:
            visible_rows.append([
                row[index] if index < len(row) else ""
                for index in visible_indexes
            ])

        return visible_columns, visible_rows

    def _table_cell(self, parent, text, row, column, header=False):
        bg = INK if header else SURFACE
        fg = "white" if header else INK
        font = ("Segoe UI", 10, "bold") if header else ("Segoe UI", 10)
        tk.Label(
            parent,
            text=str(text),
            bg=bg,
            fg=fg,
            font=font,
            padx=10,
            pady=8,
            wraplength=230,
            justify="left",
            anchor="nw",
        ).grid(row=row, column=column, sticky="nsew", padx=1, pady=1)

    def _render_image(self, data):
        asset_name = data.get("asset")
        asset = self.concept.get("assets", {}).get(asset_name, {})
        path_value = data.get("path") or asset.get("path")
        caption = data.get("caption") or asset.get("alt") or asset_name
        card = self._card(caption, PURPLE)

        path = self._resolve_asset(path_value)
        if path and path.exists():
            try:
                image = tk.PhotoImage(file=str(path))
                self.image_refs.append(image)
                tk.Label(card, image=image, bg=SURFACE).pack(anchor="w", pady=(2, 8))
                return
            except tk.TclError:
                pass

        placeholder = tk.Frame(card, bg="#f1f5f9", height=140, highlightbackground=LINE, highlightthickness=1)
        placeholder.pack(fill=tk.X, pady=(2, 8))
        placeholder.pack_propagate(False)
        self._text(placeholder, f"Image placeholder: {path_value}", color=MUTED)

    def _resolve_asset(self, path_value):
        if not path_value:
            return None
        path = Path(path_value)
        if path.is_absolute():
            return path
        if self.current_file:
            nearby = self.current_file.parent / path
            if nearby.exists():
                return nearby
        return PROJECT_ROOT / path

    def _render_dict(self, parent, data):
        if isinstance(data, dict):
            for key, value in data.items():
                self._mini_heading(parent, clean_title(key))
                if isinstance(value, (list, tuple)):
                    self._bullet_list(parent, value)
                elif isinstance(value, dict):
                    self._render_dict(parent, value)
                else:
                    self._text(parent, value)
        else:
            self._text(parent, data)

    def _section_heading(self, text):
        tk.Label(
            self.content.inner,
            text=text,
            bg=APP_BG,
            fg=INK,
            font=("Segoe UI", 18, "bold"),
            anchor="w",
        ).pack(anchor="w", fill=tk.X, padx=18, pady=(18, 4))

    def _mini_heading(self, parent, text):
        tk.Label(
            parent,
            text=text,
            bg=parent.cget("bg"),
            fg=INK,
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(anchor="w", fill=tk.X, pady=(10, 2))

    def _empty_state(self, message):
        card = self._card("Nothing to show", RED)
        self._text(card, message, size=11, color=MUTED)


def main():
    root = tk.Tk()
    Vis2App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
