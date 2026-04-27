import os
import yaml
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk, messagebox


APP_BG = "#f5f7fb"
HEADER_BG = "#1f2937"
HEADER_FG = "#ffffff"
ACCENT = "#2563eb"
ACCENT_LIGHT = "#dbeafe"
GREEN = "#16a34a"
RED = "#dc2626"
ORANGE = "#f97316"
CARD_BG = "#ffffff"
TEXT_DARK = "#111827"
TEXT_MUTED = "#6b7280"
CONFIG_FILE = Path.home() / ".anylanguageexpressaic_config.yaml"


def load_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def read_text(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def write_text(file_path, content):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def clean_title(text):
    return str(text).replace("_", " ").replace("-", " ").title()


def render_content(content, level=0):
    indent = "  " * level

    if isinstance(content, list):
        return "".join(f"{indent}- {item}\n" for item in content)

    if isinstance(content, dict):
        text = ""
        for key, value in content.items():
            text += f"\n{indent}{clean_title(key)}\n"
            text += render_content(value, level + 1)
        return text

    if content is None:
        return ""

    return f"{indent}{content}\n"


def render_text_view(concept_data, selected_languages):
    concept = clean_title(concept_data.get("concept", "Unknown Concept"))

    output = f"{concept}\n"
    output += "=" * 80 + "\n\n"

    output += "Overview\n"
    output += "--------\n"
    output += render_content(concept_data.get("overview"))

    for lang in selected_languages:
        lang_data = concept_data.get("languages", {}).get(lang, {})

        output += f"\n\n{lang.title()}\n"
        output += "-" * len(lang) + "\n"

        sections = [
            ("Mental Model", lang_data.get("mental_model")),
            ("How To Think", lang_data.get("how_to_think") or lang_data.get("think")),
            ("What To Avoid", lang_data.get("what_to_avoid") or lang_data.get("not_think")),
            ("Responsibilities", lang_data.get("responsibilities")),
            ("Syntax", lang_data.get("syntax")),
            ("Operations", lang_data.get("operations")),
            ("Traps", lang_data.get("traps")),
            ("Depth", lang_data.get("depth")),
        ]

        for title, content in sections:
            if content:
                output += f"\n{title}\n"
                output += "~" * len(title) + "\n"
                output += render_content(content)

    return output


class AnyLanguageExpressaicGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AnyLanguageExpressaic")
        self.root.geometry("1350x820")
        self.root.minsize(1150, 720)
        self.root.configure(bg=APP_BG)

        self.base_folder = None
        self.current_file = None
        self.concept_data = None
        self.selected_languages = []

        self.setup_style()
        self.build_ui()
        self.bind_shortcuts()
        self.load_last_opened_folder()
    
    def load_app_config(self):
        if not CONFIG_FILE.exists():
            return {}

        try:
            config = yaml.safe_load(read_text(CONFIG_FILE))
            return config if isinstance(config, dict) else {}
        except Exception:
            return {}

    def save_app_config(self):
        config = {
            "last_base_folder": str(self.base_folder) if self.base_folder else ""
        }

        try:
            write_text(CONFIG_FILE, yaml.safe_dump(config, sort_keys=False))
        except Exception:
            pass

    def load_last_opened_folder(self):
        config = self.load_app_config()
        folder = config.get("last_base_folder")

        if not folder:
            return

        folder_path = Path(folder)

        if folder_path.exists() and folder_path.is_dir():
            self.base_folder = folder_path
            self.folder_label.config(text=str(self.base_folder))
            self.populate_tree()
            self.status_label.config(text=f"Loaded previous folder: {self.base_folder}")
    
    def bind_shortcuts(self):
        self.root.bind("<Control-s>", lambda event: self.save_yaml())
        self.root.bind("<Control-S>", lambda event: self.save_yaml())

        self.root.bind("<Control-o>", lambda event: self.open_yaml_file())
        self.root.bind("<Control-O>", lambda event: self.open_yaml_file())

        self.root.bind("<Control-r>", lambda event: self.reload_current_file())
        self.root.bind("<Control-R>", lambda event: self.reload_current_file())

        self.root.bind("<Control-f>", lambda event: self.open_find_window())
        self.root.bind("<Control-F>", lambda event: self.open_find_window())

        self.yaml_box.bind("<Control-a>", self.select_all_yaml)
        self.yaml_box.bind("<Control-A>", self.select_all_yaml)

        self.yaml_box.bind("<Control-z>", lambda event: self.safe_edit_action("undo"))
        self.yaml_box.bind("<Control-Z>", lambda event: self.safe_edit_action("undo"))

        self.yaml_box.bind("<Control-y>", lambda event: self.safe_edit_action("redo"))
        self.yaml_box.bind("<Control-Y>", lambda event: self.safe_edit_action("redo"))

        self.root.bind("<Up>", self.scroll_visual_up)
        self.root.bind("<Down>", self.scroll_visual_down)
        self.root.bind("<Prior>", self.scroll_visual_page_up)      # PageUp
        self.root.bind("<Next>", self.scroll_visual_page_down)     # PageDown
    

    def scroll_visual_up(self, event=None):
        if self.notebook.tab(self.notebook.select(), "text") == "Visual View":
            self.visual_canvas.yview_scroll(-3, "units")
            return "break"


    def scroll_visual_down(self, event=None):
        if self.notebook.tab(self.notebook.select(), "text") == "Visual View":
            self.visual_canvas.yview_scroll(3, "units")
            return "break"


    def scroll_visual_page_up(self, event=None):
        if self.notebook.tab(self.notebook.select(), "text") == "Visual View":
            self.visual_canvas.yview_scroll(-1, "pages")
            return "break"


    def scroll_visual_page_down(self, event=None):
        if self.notebook.tab(self.notebook.select(), "text") == "Visual View":
            self.visual_canvas.yview_scroll(1, "pages")
            return "break"

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Header.TFrame", background=HEADER_BG)
        style.configure("HeaderTitle.TLabel", background=HEADER_BG, foreground=HEADER_FG, font=("Segoe UI", 19, "bold"))
        style.configure("HeaderSub.TLabel", background=HEADER_BG, foreground="#d1d5db", font=("Segoe UI", 10))

        style.configure("Panel.TFrame", background=APP_BG)
        style.configure("Sidebar.TFrame", background="#e5e7eb")
        style.configure("Card.TFrame", background=CARD_BG, relief="flat")
        style.configure("CardTitle.TLabel", background=CARD_BG, foreground=TEXT_DARK, font=("Segoe UI", 12, "bold"))
        style.configure("CardBody.TLabel", background=CARD_BG, foreground=TEXT_DARK, font=("Segoe UI", 10), wraplength=900)

        style.configure("Primary.TButton", background=ACCENT, foreground="white", font=("Segoe UI", 10, "bold"), padding=6)
        style.map("Primary.TButton", background=[("active", "#1d4ed8")])

        style.configure("Success.TButton", background=GREEN, foreground="white", font=("Segoe UI", 10, "bold"), padding=6)
        style.map("Success.TButton", background=[("active", "#15803d")])

        style.configure("Danger.TButton", background=RED, foreground="white", font=("Segoe UI", 10, "bold"), padding=6)
        style.map("Danger.TButton", background=[("active", "#b91c1c")])

        style.configure("Warn.TButton", background=ORANGE, foreground="white", font=("Segoe UI", 10, "bold"), padding=6)
        style.map("Warn.TButton", background=[("active", "#ea580c")])

        style.configure("TNotebook", background=APP_BG, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=(14, 8))


    def build_ui(self):
        self.build_header()
        self.build_body()

    def build_header(self):
        header = ttk.Frame(self.root, style="Header.TFrame")
        header.pack(fill=tk.X)

        left = ttk.Frame(header, style="Header.TFrame")
        left.pack(side=tk.LEFT, padx=18, pady=14)

        ttk.Label(left, text="AnyLanguageExpressaic", style="HeaderTitle.TLabel").pack(anchor="w")

        self.status_label = ttk.Label(
            left,
            text="Choose a base folder containing YAML concepts.",
            style="HeaderSub.TLabel"
        )
        self.status_label.pack(anchor="w", pady=(2, 0))

        right = ttk.Frame(header, style="Header.TFrame")
        right.pack(side=tk.RIGHT, padx=18, pady=14)

        ttk.Button(
            right,
            text="Open Base Folder",
            command=self.open_base_folder,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            right,
            text="Open YAML File",
            command=self.open_yaml_file,
            style="Success.TButton"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            right,
            text="Reload",
            command=self.reload_current_file,
            style="Warn.TButton"
        ).pack(side=tk.LEFT, padx=5)

    def build_body(self):
        self.body = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.body.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.build_sidebar(self.body)
        self.build_main_panel(self.body)
        self.root.after(100, lambda: self.body.sashpos(0, 255))

    def build_sidebar(self, body):
        sidebar = ttk.Frame(body, style="Sidebar.TFrame", width=250)
        sidebar.pack_propagate(False)
        body.add(sidebar, weight=0)

        title = tk.Label(
            sidebar,
            text="Knowledge Folder",
            bg="#e5e7eb",
            fg=TEXT_DARK,
            font=("Segoe UI", 12, "bold")
        )
        title.pack(anchor="w", padx=12, pady=(12, 6))

        self.folder_label = tk.Label(
            sidebar,
            text="No folder selected",
            bg="#e5e7eb",
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
            wraplength=220,
            justify="left"
        )
        self.folder_label.pack(anchor="w", padx=12, pady=(0, 10))

        file_area = tk.Frame(sidebar, bg="#e5e7eb")
        file_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.file_canvas = tk.Canvas(file_area, bg="#e5e7eb", highlightthickness=0)
        self.file_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.file_scroll = ttk.Scrollbar(file_area, orient="vertical", command=self.file_canvas.yview)
        self.file_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_canvas.configure(yscrollcommand=self.file_scroll.set)

        self.file_list_frame = tk.Frame(self.file_canvas, bg="#e5e7eb")
        self.file_list_window = self.file_canvas.create_window(
            (0, 0),
            window=self.file_list_frame,
            anchor="nw"
        )

        self.file_list_frame.bind(
            "<Configure>",
            lambda event: self.file_canvas.configure(scrollregion=self.file_canvas.bbox("all"))
        )

        self.file_canvas.bind(
            "<Configure>",
            lambda event: self.file_canvas.itemconfig(self.file_list_window, width=event.width)
        )

        lang_title = tk.Label(
            sidebar,
            text="Selected Languages",
            bg="#e5e7eb",
            fg=TEXT_DARK,
            font=("Segoe UI", 12, "bold")
        )
        lang_title.pack(anchor="w", padx=12, pady=(6, 6))

        self.selected_listbox = tk.Listbox(
            sidebar,
            height=4,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg=TEXT_DARK,
            selectbackground=ACCENT,
            selectforeground="#ffffff",
            activestyle="none",
        )
        self.selected_listbox.pack(fill=tk.X, padx=10, pady=(0, 8))

        lang_controls = ttk.Frame(sidebar, style="Sidebar.TFrame")
        lang_controls.pack(fill=tk.X, padx=10, pady=(0, 12))

        ttk.Button(
            lang_controls,
            text="Remove Selected",
            command=self.remove_selected_language,
            style="Danger.TButton"
        ).pack(fill=tk.X, pady=3)

        ttk.Button(
            lang_controls,
            text="Clear All",
            command=self.clear_languages,
            style="Warn.TButton"
        ).pack(fill=tk.X, pady=3)

    def build_main_panel(self, body):
        main = ttk.Frame(body, style="Panel.TFrame")
        body.add(main, weight=5)

        self.build_language_bar(main)

        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.welcome_frame = ttk.Frame(self.notebook)
        self.table_frame = ttk.Frame(self.notebook)
        self.code_frame = ttk.Frame(self.notebook)
        self.visual_frame = ttk.Frame(self.notebook)
        self.yaml_frame = ttk.Frame(self.notebook)
        self.text_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.welcome_frame, text="Welcome")
        self.notebook.add(self.table_frame, text="Table View")
        self.notebook.add(self.code_frame, text="Code View")
        self.notebook.add(self.visual_frame, text="Visual View")
        self.notebook.add(self.yaml_frame, text="YAML Edit/View")
        self.notebook.add(self.text_frame, text="Text View")

        self.build_welcome_view()
        self.build_table_view()
        self.build_code_view()
        self.build_visual_view()
        self.build_yaml_view()
        self.build_text_view()

    def build_language_bar(self, parent):
        bar = tk.Frame(parent, bg=APP_BG)
        bar.pack(fill=tk.X, pady=(0, 10))

        controls = tk.Frame(bar, bg=APP_BG)
        controls.pack(fill=tk.X)

        tk.Label(
            controls,
            text="Add language to comparison:",
            bg=APP_BG,
            fg=TEXT_DARK,
            font=("Segoe UI", 10, "bold")
        ).pack(side=tk.LEFT)

        self.language_dropdown = ttk.Combobox(controls, state="readonly", width=18)
        self.language_dropdown.pack(side=tk.LEFT, padx=8)

        ttk.Button(
            controls,
            text="+ Add Language",
            command=self.add_language,
            style="Success.TButton"
        ).pack(side=tk.LEFT, padx=4)

        ttk.Button(
            controls,
            text="Add All",
            command=self.add_all_languages,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=4)

        self.selected_label = tk.Label(
            bar,
            text="Selected: none",
            bg=ACCENT_LIGHT,
            fg="#1e3a8a",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=5,
            anchor="w",
            justify="left"
        )
        self.selected_label.pack(fill=tk.X, pady=(8, 0))
    
    def build_welcome_view(self):
        container = tk.Frame(self.welcome_frame, bg=APP_BG)
        container.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(
            container,
            text="Welcome to AnyLanguageExpressaic",
            bg=APP_BG,
            fg=TEXT_DARK,
            font=("Segoe UI", 20, "bold"),
        )
        title.pack(pady=(60, 10))

        subtitle = tk.Label(
            container,
            text="Learn how programming concepts translate across languages",
            bg=APP_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 11),
        )
        subtitle.pack(pady=(0, 30))

        steps = [
            "1. Open a base folder containing YAML files (recommended)\n(OR) open a single YAML file",
            "2. Add one or more languages to compare",
            "3. Use Table View to see operations",
            "4. Use Code View to compare syntax",
            "5. Use Visual View to understand thinking",
            "6. Edit YAML directly and press Ctrl+S to save",
        ]

        box = tk.Frame(container, bg="#eef2ff", padx=20, pady=20)
        box.pack(padx=20, pady=10)

        for step in steps:
            tk.Label(
                box,
                text=f"• {step}",
                bg="#eef2ff",
                fg="#1e3a8a",
                font=("Segoe UI", 11),
                anchor="w",
                justify="left",
            ).pack(anchor="w", pady=3)

        tips_title = tk.Label(
            container,
            text="Tips",
            bg=APP_BG,
            fg=TEXT_DARK,
            font=("Segoe UI", 13, "bold"),
        )
        tips_title.pack(pady=(30, 5))

        tips = [
            "Use Ctrl+S to save quickly",
            "Use Ctrl+F to search in YAML",
            "Start with 2 languages for clarity",
            "Use Visual View to understand thinking shifts",
        ]

        tips_box = tk.Frame(container, bg="#ecfdf5", padx=20, pady=15)
        tips_box.pack(padx=20, pady=5)

        for tip in tips:
            tk.Label(
                tips_box,
                text=f"• {tip}",
                bg="#ecfdf5",
                fg="#065f46",
                font=("Segoe UI", 10),
            ).pack(anchor="w", pady=2)

    def build_table_view(self):
        self.table_canvas = tk.Canvas(self.table_frame, bg=APP_BG, highlightthickness=0)
        self.table_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=8)

        self.table_scroll_y = ttk.Scrollbar(
            self.table_frame,
            orient="vertical",
            command=self.table_canvas.yview
        )
        self.table_scroll_y.pack(side=tk.RIGHT, fill=tk.Y, pady=8)

        self.table_scroll_x = ttk.Scrollbar(
            self.table_frame,
            orient="horizontal",
            command=self.table_canvas.xview
        )
        self.table_scroll_x.pack(side=tk.BOTTOM, fill=tk.X, padx=8)

        self.table_canvas.configure(
            yscrollcommand=self.table_scroll_y.set,
            xscrollcommand=self.table_scroll_x.set
        )

        self.table_inner = tk.Frame(self.table_canvas, bg=APP_BG)
        self.table_window = self.table_canvas.create_window(
            (0, 0),
            window=self.table_inner,
            anchor="nw"
        )

        self.table_inner.bind(
            "<Configure>",
            lambda event: self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))
        )

    def build_code_view(self):
        self.code_box = tk.Text(
            self.code_frame,
            wrap=tk.NONE,
            font=("Consolas", 11),
            bg="#0f172a",
            fg="#e5e7eb",
            insertbackground="#ffffff",
            padx=14,
            pady=14
        )
        self.code_box.pack(fill=tk.BOTH, expand=True)

    def build_visual_view(self):
        self.visual_canvas = tk.Canvas(self.visual_frame, background=APP_BG, highlightthickness=0)
        self.visual_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.visual_scroll = ttk.Scrollbar(
            self.visual_frame,
            orient="vertical",
            command=self.visual_canvas.yview,
        )
        self.visual_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.visual_canvas.configure(yscrollcommand=self.visual_scroll.set)

        self.visual_inner = ttk.Frame(self.visual_canvas, style="Panel.TFrame")
        self.visual_window = self.visual_canvas.create_window((0, 0), window=self.visual_inner, anchor="nw")

        self.visual_inner.bind(
            "<Configure>",
            lambda event: self.visual_canvas.configure(scrollregion=self.visual_canvas.bbox("all"))
        )

        self.visual_canvas.bind(
            "<Configure>",
            lambda event: self.visual_canvas.itemconfig(self.visual_window, width=event.width)
        )

    def build_yaml_view(self):
        top = tk.Frame(self.yaml_frame, bg=APP_BG)
        top.pack(fill=tk.X, padx=8, pady=8)

        ttk.Button(top, text="Reload YAML", command=self.reload_current_file, style="Warn.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Save", command=self.save_yaml, style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Save As", command=self.save_yaml_as, style="Primary.TButton").pack(side=tk.LEFT, padx=4)

        self.yaml_path_label = tk.Label(top, text="No file loaded", bg=APP_BG, fg=TEXT_MUTED)
        self.yaml_path_label.pack(side=tk.LEFT, padx=12)

        self.yaml_box = tk.Text(
            self.yaml_frame,
            wrap=tk.NONE,
            font=("Consolas", 11),
            bg="#fff7ed",
            fg="#111827",
            insertbackground="#111827",
            padx=14,
            pady=14,
            undo=True,
            maxundo=-1,
            autoseparators=True,
        )
        self.yaml_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        
    def build_text_view(self):
        self.output_box = tk.Text(
            self.text_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg="#ffffff",
            fg=TEXT_DARK,
            padx=14,
            pady=14
        )
        self.output_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def open_base_folder(self):
        folder = filedialog.askdirectory()

        if not folder:
            return

        self.base_folder = Path(folder)
        self.folder_label.config(text=str(self.base_folder))
        self.save_app_config()
        self.populate_tree()

    def populate_tree(self):
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()

        if not self.base_folder:
            return

        self.add_folder_heading(self.base_folder.name, 0)
        self.add_file_nodes(self.base_folder, 0)

    def add_folder_heading(self, folder_name, level):
        label = tk.Label(
            self.file_list_frame,
            text=("    " * level) + "📁 " + folder_name,
            bg="#e5e7eb",
            fg=TEXT_DARK,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            justify="left",
            padx=6,
            pady=4
        )
        label.pack(fill=tk.X, anchor="w")

    def add_file_button(self, file_path, level):
        button = tk.Button(
            self.file_list_frame,
            text=("    " * level) + "📄 " + file_path.name,
            bg="#ffffff",
            fg=TEXT_DARK,
            activebackground=ACCENT_LIGHT,
            activeforeground=TEXT_DARK,
            relief=tk.FLAT,
            anchor="w",
            justify="left",
            font=("Segoe UI", 10),
            padx=6,
            pady=5,
            command=lambda path=file_path: self.load_concept_file(path)
        )
        button.pack(fill=tk.X, anchor="w", padx=4, pady=1)

    def add_file_nodes(self, folder_path, level):
        try:
            entries = sorted(folder_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            return

        for entry in entries:
            if entry.is_dir():
                self.add_folder_heading(entry.name, level + 1)
                self.add_file_nodes(entry, level + 1)
            elif entry.suffix.lower() in [".yaml", ".yml"]:
                self.add_file_button(entry, level + 1)

    def open_yaml_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("YAML files", "*.yaml *.yml")])

        if not file_path:
            return

        self.load_concept_file(Path(file_path))

    def load_concept_file(self, file_path):
        try:
            self.current_file = Path(file_path)
            self.concept_data = load_yaml(self.current_file)

            raw_yaml = read_text(self.current_file)
            self.yaml_box.delete("1.0", tk.END)
            self.yaml_box.insert(tk.END, raw_yaml)
            self.yaml_path_label.config(text=str(self.current_file))

            languages = list(self.concept_data.get("languages", {}).keys())
            self.language_dropdown["values"] = languages

            self.selected_languages = []
            self.selected_listbox.delete(0, tk.END)

            if languages:
                self.selected_languages.append(languages[0])
                self.selected_listbox.insert(tk.END, languages[0])
                self.language_dropdown.current(0)

                if len(languages) > 1:
                    self.selected_languages.append(languages[1])
                    self.selected_listbox.insert(tk.END, languages[1])

            concept = clean_title(self.concept_data.get("concept", self.current_file.stem))
            self.status_label.config(text=f"Loaded: {concept}  |  {self.current_file.name}")
            self.notebook.select(1)

            self.refresh_view()

        except Exception as error:
            messagebox.showerror("Error Loading YAML", str(error))

    def reload_current_file(self):
        if not self.current_file:
            messagebox.showwarning("No file", "No YAML file is currently loaded.")
            return

        self.load_concept_file(self.current_file)

    def save_yaml(self):
        if not self.current_file:
            self.save_yaml_as()
            return

        try:
            content = self.yaml_box.get("1.0", tk.END)
            yaml.safe_load(content)
            write_text(self.current_file, content)
            self.load_concept_file(self.current_file)
            messagebox.showinfo("Saved", "YAML saved successfully.")
        except Exception as error:
            messagebox.showerror("Save Error", str(error))

    def save_yaml_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml *.yml")]
        )

        if not file_path:
            return

        try:
            content = self.yaml_box.get("1.0", tk.END)
            yaml.safe_load(content)
            write_text(Path(file_path), content)
            self.load_concept_file(Path(file_path))
            messagebox.showinfo("Saved", "YAML saved successfully.")
        except Exception as error:
            messagebox.showerror("Save Error", str(error))

    def add_language(self):
        if not self.concept_data:
            return

        language = self.language_dropdown.get()

        if not language:
            return

        if language not in self.selected_languages:
            self.selected_languages.append(language)
            self.selected_listbox.insert(tk.END, language)

        self.refresh_view()

    def add_all_languages(self):
        if not self.concept_data:
            return

        languages = list(self.concept_data.get("languages", {}).keys())

        self.selected_languages = languages
        self.selected_listbox.delete(0, tk.END)

        for lang in languages:
            self.selected_listbox.insert(tk.END, lang)

        self.refresh_view()

    def remove_selected_language(self):
        selection = self.selected_listbox.curselection()

        if not selection:
            messagebox.showinfo("Remove Language", "Select a language from the left list first.")
            return

        index = selection[0]
        language = self.selected_listbox.get(index)

        if language in self.selected_languages:
            self.selected_languages.remove(language)

        self.selected_listbox.delete(index)
        self.refresh_view()

    def clear_languages(self):
        self.selected_languages = []
        self.selected_listbox.delete(0, tk.END)
        self.refresh_view()

    def refresh_view(self):
        self.update_selected_label()
        self.show_table_view()
        self.show_code_view()
        self.show_visual_view()
        self.show_text_view()

    def update_selected_label(self):
        if not self.selected_languages:
            self.selected_label.config(text="Selected: none")
        else:
            self.selected_label.config(text="Selected: " + "  |  ".join(lang.title() for lang in self.selected_languages))

    def clear_table(self):
        for widget in self.table_inner.winfo_children():
            widget.destroy()

    def make_table_cell(self, text, row, column, is_header=False):
        background = HEADER_BG if is_header else "#ffffff"
        foreground = HEADER_FG if is_header else TEXT_DARK
        font = ("Segoe UI", 10, "bold") if is_header else ("Segoe UI", 10)

        cell = tk.Label(
            self.table_inner,
            text=str(text),
            bg=background,
            fg=foreground,
            font=font,
            padx=10,
            pady=8,
            wraplength=260,
            justify="left",
            anchor="nw",
            relief=tk.SOLID,
            borderwidth=1
        )
        cell.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
        return cell

    def show_table_view(self):
        self.clear_table()

        if not self.concept_data or not self.selected_languages:
            return

        rows = self.concept_data.get("operations_map", [])
        columns = ["idea"] + self.selected_languages

        for col_index, col_name in enumerate(columns):
            self.make_table_cell(clean_title(col_name), 0, col_index, is_header=True)

        for row_index, row in enumerate(rows, start=1):
            values = [row.get("idea", "")]

            for lang in self.selected_languages:
                values.append(row.get(lang, ""))

            for col_index, value in enumerate(values):
                self.make_table_cell(value, row_index, col_index)

        for col_index in range(len(columns)):
            self.table_inner.grid_columnconfigure(col_index, weight=1, minsize=280)

    def show_code_view(self):
        self.code_box.delete("1.0", tk.END)

        if not self.concept_data or not self.selected_languages:
            return

        rows = self.concept_data.get("operations_map", [])
        output = ""

        for row in rows:
            idea = row.get("idea", "Unnamed Operation")
            output += f"## {clean_title(idea)}\n\n"

            for lang in self.selected_languages:
                code = row.get(lang, "")
                output += f"[{lang.title()}]\n"
                output += "-" * (len(lang) + 2) + "\n"
                output += f"{code}\n\n"

            output += "\n" + "=" * 80 + "\n\n"

        self.code_box.insert(tk.END, output)

    def clear_visual(self):
        for widget in self.visual_inner.winfo_children():
            widget.destroy()

    def add_card(self, title, body, color=ACCENT):
        outer = tk.Frame(self.visual_inner, bg=color, padx=4, pady=0)
        outer.pack(fill=tk.X, padx=16, pady=9)

        card = tk.Frame(outer, bg=CARD_BG)
        card.pack(fill=tk.X)

        tk.Label(
            card,
            text=title,
            bg=CARD_BG,
            fg=color,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", padx=14, pady=(12, 5))

        tk.Label(
            card,
            text=body.strip() if body else "Not available",
            bg=CARD_BG,
            fg=TEXT_DARK,
            font=("Segoe UI", 10),
            wraplength=900,
            justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 14))

    def show_visual_view(self):
        self.clear_visual()

        if not self.concept_data:
            self.add_card("No Concept Loaded", "Open a base folder or YAML file to begin.", RED)
            return

        if not self.selected_languages:
            self.add_card("No Languages Selected", "Use + Add Language or Add All to start comparison.", ORANGE)
            return

        concept = clean_title(self.concept_data.get("concept", "Unknown Concept"))
        self.add_card(concept, self.concept_data.get("overview", ""), ACCENT)
        '''self.add_card(
            "How To Use This Page",
            "- Start with the mental model\n- Compare operations in Table View\n- Read Code View for direct syntax mapping\n- Use YAML Edit/View to improve the source file\n- Save with Ctrl+S",
            GREEN,
        )'''

        colors = [ACCENT, GREEN, ORANGE, RED, "#7c3aed", "#0891b2"]

        for index, lang in enumerate(self.selected_languages):
            lang_data = self.concept_data.get("languages", {}).get(lang, {})
            color = colors[index % len(colors)]

            self.add_card(f"{lang.title()} Mental Model", render_content(lang_data.get("mental_model")), color)
            self.add_card(f"{lang.title()} How To Think", render_content(lang_data.get("how_to_think") or lang_data.get("think")), color)
            self.add_card(f"{lang.title()} Traps", render_content(lang_data.get("traps")), color)
            depth = lang_data.get("depth", {})
            if depth:
                self.add_card(
                    f"{lang.title()} Depth",
                    render_content(depth),
                    "#92400e",
                )

        if len(self.selected_languages) >= 2:
            shifts = self.concept_data.get("mental_shift", {})

            for i in range(len(self.selected_languages)):
                for j in range(len(self.selected_languages)):
                    if i == j:
                        continue

                    src = self.selected_languages[i]
                    tgt = self.selected_languages[j]
                    key = f"{src}_to_{tgt}"

                    if key in shifts:
                        self.add_card(
                            f"Mental Shift: {src.title()} → {tgt.title()}",
                            render_content(shifts[key]),
                            "#7c3aed",
                        )

                    not_think = (
                        self.concept_data
                        .get("languages", {})
                        .get(tgt, {})
                        .get("not_think", {})
                        .get(f"from_{src}")
                    )

                    if not_think:
                        self.add_card(
                            f"What To Avoid: {src.title()} → {tgt.title()}",
                            render_content(not_think),
                            RED,
                        )

    def show_text_view(self):
        self.output_box.delete("1.0", tk.END)

        if not self.concept_data or not self.selected_languages:
            return

        output = render_text_view(self.concept_data, self.selected_languages)
        self.output_box.insert(tk.END, output)
    
    def select_all_yaml(self, event=None):
        self.yaml_box.tag_add("sel", "1.0", tk.END)
        return "break"

    def safe_edit_action(self, action):
        try:
            if action == "undo":
                self.yaml_box.edit_undo()
            elif action == "redo":
                self.yaml_box.edit_redo()
        except tk.TclError:
            pass

        return "break"


    def open_find_window(self):
        if not self.current_file:
            return

        find_window = tk.Toplevel(self.root)
        find_window.title("Find in YAML")
        find_window.geometry("360x110")
        find_window.configure(bg=APP_BG)

        tk.Label(
            find_window,
            text="Find:",
            bg=APP_BG,
            fg=TEXT_DARK,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=12, pady=(12, 4))

        entry = tk.Entry(find_window, font=("Segoe UI", 10))
        entry.pack(fill=tk.X, padx=12)

        def find_text():
            query = entry.get()

            if not query:
                return

            self.yaml_box.tag_remove("find_match", "1.0", tk.END)

            start = "1.0"
            first_match = None

            while True:
                pos = self.yaml_box.search(query, start, stopindex=tk.END, nocase=True)

                if not pos:
                    break

                end = f"{pos}+{len(query)}c"
                self.yaml_box.tag_add("find_match", pos, end)

                if first_match is None:
                    first_match = pos

                start = end

            self.yaml_box.tag_config("find_match", background="#fde68a", foreground="#111827")

            if first_match:
                self.yaml_box.see(first_match)
                self.yaml_box.mark_set(tk.INSERT, first_match)

        ttk.Button(
            find_window,
            text="Find",
            command=find_text,
            style="Primary.TButton"
        ).pack(pady=10)

        entry.bind("<Return>", lambda event: find_text())
        entry.focus()


def main():
    root = tk.Tk()
    AnyLanguageExpressaicGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()