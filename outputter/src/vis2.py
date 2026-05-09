import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import yaml


PROJECT_ROOT = ''
if getattr(sys, 'frozen', False):
    PROJECT_ROOT = Path(sys.executable).resolve().parents[3]
else:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONCEPT = PROJECT_ROOT / "templates" / "vis2_welcome_template.yaml"
CONFIG_FILE = PROJECT_ROOT / "vis2_config.yaml"
LESSON_BUILDER_VIS2 = PROJECT_ROOT / "outputter" / "src" / "lesson_builder_vis2.py"

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
CODE_BG = "#fff7ed"
CODE_FG = "#1f2937"
CODE_ACCENT = "#9a3412"
BOOKLET_LINK_COLORS = [
    ACCENT,
    GREEN,
    AMBER,
    PURPLE,
    "#0f766e",
    "#be123c",
    "#7c3aed",
    "#0369a1",
]


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


def is_booklet(data):
    return isinstance(data, dict) and (data.get("type") == "booklet" or isinstance(data.get("chapters"), list))


def topic_color(value):
    text = str(value or "")
    return BOOKLET_LINK_COLORS[sum(ord(ch) for ch in text) % len(BOOKLET_LINK_COLORS)]


def maximize_window(root):
    root.update_idletasks()
    try:
        root.state("zoomed")
        return
    except tk.TclError:
        pass
    try:
        root.attributes("-zoomed", True)
    except tk.TclError:
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.geometry(f"{width}x{height}+0+0")


def bind_wrap(label, container, margin=36, minimum=180):
    def update(event=None):
        try:
            width = (event.width if event else container.winfo_width()) - margin
            label.configure(wraplength=max(minimum, width))
        except tk.TclError:
            pass

    container.bind("<Configure>", update, add="+")
    label.after_idle(update)
    return label


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _event=None):
        if self.tip or not self.text:
            return
        x = self.widget.winfo_rootx() + 18
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self.tip,
            text=self.text,
            bg=CODE_FG,
            fg="white",
            padx=8,
            pady=5,
            wraplength=300,
            justify="left",
            font=("Segoe UI", 9),
        ).pack()

    def hide(self, _event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


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
        maximize_window(self.root)

        self.current_file = None
        self.base_folder = None
        self.concept = {}
        self.image_refs = []
        self.yaml_files = []
        self.file_tree_items = {}
        self.available_languages = []
        self.language_vars = {}
        self.tabs = []
        self.active_tab = None
        self.nav_history = []
        self.find_window = None
        self.find_query = ""
        self.find_scope = "content"
        self.find_matches = []
        self.find_index = -1
        self.find_highlight = None

        self.mode_var = tk.StringVar(value="lesson")
        self.source_var = tk.StringVar()
        self.target_var = tk.StringVar()

        self._setup_style()
        self._build_menu()
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

    def _build_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Open Folder...", accelerator="Ctrl+O", command=self.open_folder)
        file_menu.add_command(label="Reload Current", accelerator="Ctrl+R", command=self.reload_current_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menu.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menu, tearoff=False)
        view_menu.add_command(label="Lesson", accelerator="Ctrl+1", command=lambda: self.set_mode("lesson"))
        view_menu.add_command(label="Revision", accelerator="Ctrl+2", command=lambda: self.set_mode("revision"))
        view_menu.add_command(label="Transition", accelerator="Ctrl+3", command=lambda: self.set_mode("transition"))
        view_menu.add_command(label="Raw Structure", accelerator="Ctrl+4", command=lambda: self.set_mode("raw"))
        view_menu.add_separator()
        view_menu.add_command(label="Find", accelerator="Ctrl+F", command=self.open_find)
        menu.add_cascade(label="View", menu=view_menu)

        navigate_menu = tk.Menu(menu, tearoff=False)
        navigate_menu.add_command(label="Back", accelerator="Alt+Left", command=self.go_back)
        navigate_menu.add_command(label="Close Tab", accelerator="Ctrl+W", command=self.close_active_tab)
        navigate_menu.add_separator()
        navigate_menu.add_command(label="Previous View", accelerator="Ctrl+Up", command=lambda: self.select_relative_mode(-1))
        navigate_menu.add_command(label="Next View", accelerator="Ctrl+Down", command=lambda: self.select_relative_mode(1))
        navigate_menu.add_command(label="Previous Tab", accelerator="Ctrl+Left", command=lambda: self.switch_relative_tab(-1))
        navigate_menu.add_command(label="Next Tab", accelerator="Ctrl+Right", command=lambda: self.switch_relative_tab(1))
        menu.add_cascade(label="Navigate", menu=navigate_menu)

        tools_menu = tk.Menu(menu, tearoff=False)
        tools_menu.add_command(label="Open Builder Vis2", accelerator="Ctrl+B", command=self.open_builder_vis2)
        menu.add_cascade(label="Tools", menu=tools_menu)

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

        self.back_button = tk.Button(
            header,
            text="←",
            command=self.go_back,
            bg="#0f172a",
            fg="white",
            activebackground="#1e293b",
            activeforeground="white",
            relief=tk.FLAT,
            font=("Segoe UI", 16, "bold"),
            width=3,
            cursor="hand2",
        )
        self.back_button.pack(side=tk.RIGHT, padx=18, pady=14)
        Tooltip(self.back_button, "Back")

        body = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.sidebar_shell = ttk.Frame(body, style="Sidebar.TFrame", width=330)
        body.add(self.sidebar_shell, weight=0)
        self.main = ttk.Frame(body)
        body.add(self.main, weight=5)

        self.sidebar = tk.Frame(self.sidebar_shell, bg=SURFACE_ALT)
        self.sidebar.pack(fill=tk.BOTH, expand=True)

        self._build_sidebar()
        self.tab_bar = tk.Frame(self.main, bg=APP_BG)
        self.tab_bar.pack(fill=tk.X, pady=(0, 8))
        self.find_window = tk.Frame(self.main, bg=APP_BG, highlightbackground=LINE, highlightthickness=1)
        tk.Label(self.find_window, text="Find", bg=APP_BG, fg=INK, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(10, 6), pady=8)
        self.find_entry = tk.Entry(self.find_window, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1)
        self.find_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), pady=8)
        ttk.Button(self.find_window, text="Next", command=self.run_find).pack(side=tk.LEFT, padx=(0, 6), pady=6)
        self.find_status = tk.Label(self.find_window, text="", bg=APP_BG, fg=MUTED, font=("Segoe UI", 9), anchor="w")
        self.find_status.pack(side=tk.LEFT, padx=(0, 8), pady=8)
        ttk.Button(self.find_window, text="Close", command=self.close_find).pack(side=tk.RIGHT, padx=8, pady=6)
        self.find_entry.bind("<Return>", lambda _event: self.run_find())
        self.find_entry.bind("<Control-f>", lambda _event: self.run_find())
        self.find_entry.bind("<Control-F>", lambda _event: self.run_find())
        self.find_entry.bind("<Escape>", lambda _event: self.close_find())
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

        view_panel = tk.Frame(self.sidebar, bg=SURFACE_ALT)
        view_panel.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=(0, 12))
        tk.Label(
            view_panel,
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
                view_panel,
                text=label,
                value=value,
                variable=self.mode_var,
                command=self.render,
                style="Mode.TRadiobutton",
            ).pack(anchor="w", padx=14, pady=4)

        file_area = tk.Frame(self.sidebar, bg=SURFACE_ALT)
        file_area.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))

        self.file_tree = ttk.Treeview(
            file_area,
            show="tree",
            height=10,
            selectmode="browse",
        )
        file_scroll = ttk.Scrollbar(file_area, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=file_scroll.set)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.bind("<Button-1>", lambda _event: self.file_tree.focus_set())
        self.file_tree.bind("<Double-Button-1>", self.open_selected_tree_item)
        self.file_tree.bind("<Return>", self.open_selected_tree_item)

    def bind_shortcuts(self):
        self.root.bind("<Control-o>", lambda _event: self.open_folder())
        self.root.bind("<Control-O>", lambda _event: self.open_folder())
        self.root.bind("<Control-b>", lambda _event: self.open_builder_vis2())
        self.root.bind("<Control-B>", lambda _event: self.open_builder_vis2())
        self.root.bind("<Control-r>", lambda _event: self.reload_current_file())
        self.root.bind("<Control-R>", lambda _event: self.reload_current_file())
        self.root.bind("<Control-w>", lambda _event: self.close_active_tab())
        self.root.bind("<Control-W>", lambda _event: self.close_active_tab())
        self.root.bind("<Alt-Left>", lambda _event: self.go_back())
        self.root.bind("<Control-BackSpace>", lambda _event: self.go_back())
        self.root.bind("<Control-bracketleft>", lambda _event: self.go_back())
        self.root.bind("<BackSpace>", self.handle_backspace_shortcut)
        self.root.bind("<Control-f>", lambda _event: self.open_find())
        self.root.bind("<Control-F>", lambda _event: self.open_find())
        self.root.bind("<Button-4>", lambda _event: self.go_back())

        self.root.bind("<Control-Key-1>", lambda _event: self.set_mode("lesson"))
        self.root.bind("<Control-Key-2>", lambda _event: self.set_mode("revision"))
        self.root.bind("<Control-Key-3>", lambda _event: self.set_mode("transition"))
        self.root.bind("<Control-Key-4>", lambda _event: self.set_mode("raw"))

        self.root.bind("<Up>", lambda event: self.handle_arrow_key(event, -1))
        self.root.bind("<Down>", lambda event: self.handle_arrow_key(event, 1))
        self.root.bind("<Control-Up>", lambda _event: self.select_relative_mode(-1))
        self.root.bind("<Control-Down>", lambda _event: self.select_relative_mode(1))
        self.root.bind("<Control-Left>", lambda _event: self.switch_relative_tab(-1))
        self.root.bind("<Control-Right>", lambda _event: self.switch_relative_tab(1))
        self.root.bind("<Control-Return>", lambda _event: self.show_transition())
        self.root.bind("<Control-t>", lambda _event: self.show_transition())
        self.root.bind("<Control-T>", lambda _event: self.show_transition())
        self.root.bind("<Control-Shift-T>", lambda _event: self.swap_transition_languages())

    def open_builder_vis2(self):
        if not LESSON_BUILDER_VIS2.exists():
            messagebox.showerror("Missing Tool", f"Could not find:\n{LESSON_BUILDER_VIS2}")
            return "break"

        try:
            subprocess.Popen([sys.executable, str(LESSON_BUILDER_VIS2)])
        except Exception as error:
            messagebox.showerror("Could Not Open Builder Vis2", str(error))
        return "break"

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
        open_tabs = []
        for tab in self.tabs:
            try:
                open_tabs.append(str(tab["path"].relative_to(self.base_folder)))
            except ValueError:
                continue

        config = {
            "last_yaml_folder": str(self.base_folder),
            "last_yaml_file": last_yaml_file,
            "open_tabs": open_tabs,
            "active_tab": last_yaml_file,
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

        self.load_folder(
            folder_path,
            preferred_file=config.get("last_yaml_file"),
            save_config=False,
            open_tabs=config.get("open_tabs", []),
            active_tab=config.get("active_tab") or config.get("last_yaml_file"),
        )
        return True

    def open_folder(self):
        folder = filedialog.askdirectory(title="Open YAML folder")
        if not folder:
            return

        self.load_folder(Path(folder))

    def load_folder(self, folder, preferred_file=None, save_config=True, open_tabs=None, active_tab=None):
        self.base_folder = Path(folder)
        self.populate_file_list(preferred_file=preferred_file, open_tabs=open_tabs, active_tab=active_tab)
        if save_config:
            self.save_app_config()

    def populate_file_list(self, preferred_file=None, open_tabs=None, active_tab=None):
        self.file_tree.delete(*self.file_tree.get_children())
        self.file_tree_items = {}

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

        folder_nodes = {}
        for path in self.yaml_files:
            relative = path.relative_to(self.base_folder)
            parent = ""
            for part in relative.parts[:-1]:
                key = (parent, part)
                if key not in folder_nodes:
                    folder_nodes[key] = self.file_tree.insert(parent, tk.END, text=f"📁 {part}", open=True)
                parent = folder_nodes[key]
            item_id = self.file_tree.insert(parent, tk.END, text=f"📄 {relative.name}", values=(str(path),))
            self.file_tree_items[path] = item_id

        if not self.yaml_files:
            messagebox.showinfo("No YAML files", "This folder does not contain any .yaml or .yml files.")
            return

        if open_tabs:
            self.restore_tabs(open_tabs, active_tab or preferred_file)
            return

        selected_index = 0
        if preferred_file:
            for index, path in enumerate(self.yaml_files):
                if str(path.relative_to(self.base_folder)) == preferred_file:
                    selected_index = index
                    break

        self.select_file_at(selected_index)

    def restore_tabs(self, open_tabs, active_tab=None):
        self.tabs = []
        self.active_tab = None
        valid_paths = []
        for relative in open_tabs:
            path = self.base_folder / relative
            if path.exists() and path in self.yaml_files:
                valid_paths.append(path)

        if not valid_paths:
            if active_tab:
                path = self.base_folder / active_tab
                if path.exists() and path in self.yaml_files:
                    valid_paths.append(path)
            if not valid_paths:
                self.select_file_at(0)
                return

        active_path = self.base_folder / active_tab if active_tab else valid_paths[0]
        for path in valid_paths:
            try:
                concept = load_yaml(path)
            except Exception:
                continue
            title = concept.get("title") or clean_title(concept.get("id", path.stem))
            self.tabs.append({"path": path, "title": title, "scroll": 0.0})

        if not self.tabs:
            self.select_file_at(0)
            return

        self.active_tab = 0
        for index, tab in enumerate(self.tabs):
            if tab["path"] == active_path:
                self.active_tab = index
                break

        self.load_file(self.tabs[self.active_tab]["path"], record_history=False)

    def on_file_select(self, _event=None):
        if not self.base_folder:
            return

        selection = self.file_tree.selection()
        if not selection:
            return

        path = self.path_from_tree_item(selection[0])
        if path:
            self.load_file(path, new_tab=True)

    def open_selected_tree_item(self, _event=None):
        selection = self.file_tree.selection()
        if not selection:
            return "break"
        item = selection[0]
        path = self.path_from_tree_item(item)
        if path:
            self.load_file(path, new_tab=True)
        else:
            self.file_tree.item(item, open=not self.file_tree.item(item, "open"))
        return "break"

    def path_from_tree_item(self, item):
        values = self.file_tree.item(item, "values")
        if not values:
            return None
        path = Path(values[0])
        return path if path.exists() else None

    def select_file_at(self, index):
        if not self.yaml_files:
            return "break"

        index = max(0, min(index, len(self.yaml_files) - 1))
        path = self.yaml_files[index]
        item_id = self.file_tree_items.get(path)
        if item_id:
            self.file_tree.selection_set(item_id)
            self.file_tree.focus(item_id)
            self.file_tree.see(item_id)
        self.load_file(path, new_tab=True)
        return "break"

    def select_relative_file(self, offset):
        if not self.yaml_files:
            return "break"

        selection = self.file_tree.selection()
        selected_path = self.path_from_tree_item(selection[0]) if selection else None
        try:
            current = self.yaml_files.index(selected_path) if selected_path else 0
        except ValueError:
            current = 0
        self.select_file_at(current + offset)
        return "break"

    def handle_arrow_key(self, event, direction):
        focused = self.root.focus_get()
        if self.is_descendant(focused, self.file_tree):
            return None
        if isinstance(focused, (tk.Entry, tk.Text, ttk.Entry)):
            return None
        self.content.canvas.yview_scroll(direction, "units")
        return "break"

    def is_descendant(self, widget, parent):
        while widget is not None:
            if widget == parent:
                return True
            try:
                widget = widget.master
            except Exception:
                return False
        return False

    def load_file(self, path, new_tab=False, record_history=True):
        path = Path(path)
        try:
            concept = load_yaml(path)
        except Exception as error:
            messagebox.showerror("Could not load YAML", str(error))
            return

        if record_history and self.current_file and self.current_file != path:
            self.nav_history.append(self.current_file)

        self.concept = concept
        self.current_file = path
        if new_tab or (self.active_tab is not None and self.tabs and self.tabs[self.active_tab]["path"] != path):
            self.save_active_scroll()
        self.open_or_update_tab(path, concept, new_tab=new_tab)

        title = self.concept.get("title") or clean_title(self.concept.get("id", "Untitled Concept"))
        self.title_label.config(text=title)
        self.subtitle_label.config(text=str(self.current_file))
        self._populate_languages()
        self.render()
        self.render_tabs()
        self.restore_active_scroll()
        self.save_app_config()

    def reload_current_file(self):
        if self.current_file:
            self.load_file(self.current_file, record_history=False)
        return "break"

    def open_or_update_tab(self, path, concept, new_tab=False):
        title = concept.get("title") or clean_title(concept.get("id", path.stem))
        existing = None
        for index, tab in enumerate(self.tabs):
            if tab["path"] == path:
                existing = index
                break

        if existing is not None:
            old_scroll = self.tabs[existing].get("scroll", 0.0)
            self.tabs[existing] = {"path": path, "title": title, "scroll": old_scroll}
            self.active_tab = existing
        elif new_tab or self.active_tab is None:
            self.tabs.append({"path": path, "title": title, "scroll": 0.0})
            self.active_tab = len(self.tabs) - 1
        else:
            self.tabs[self.active_tab] = {"path": path, "title": title, "scroll": 0.0}

    def save_active_scroll(self):
        if self.active_tab is None or self.active_tab >= len(self.tabs):
            return
        try:
            self.tabs[self.active_tab]["scroll"] = self.content.canvas.yview()[0]
        except Exception:
            pass

    def restore_active_scroll(self):
        if self.active_tab is None or self.active_tab >= len(self.tabs):
            return
        scroll = self.tabs[self.active_tab].get("scroll", 0.0)
        self.root.after(30, lambda value=scroll: self.content.canvas.yview_moveto(value))

    def render_tabs(self):
        for child in self.tab_bar.winfo_children():
            child.destroy()

        if not self.tabs:
            return

        for index, tab in enumerate(self.tabs):
            active = index == self.active_tab
            tab_frame = tk.Frame(self.tab_bar, bg=ACCENT if active else SURFACE, highlightbackground=LINE, highlightthickness=1)
            tab_frame.pack(side=tk.LEFT, padx=(0, 6), pady=2)
            label = tk.Label(
                tab_frame,
                text=tab["title"],
                bg=ACCENT if active else SURFACE,
                fg="white" if active else INK,
                font=("Segoe UI", 9, "bold" if active else "normal"),
                padx=10,
                pady=5,
                cursor="hand2",
            )
            label.pack(side=tk.LEFT)
            label.bind("<Button-1>", lambda _event, i=index: self.switch_tab(i))
            label.bind("<Button-3>", lambda event, i=index: self.show_tab_menu(i, event))
            close = tk.Label(
                tab_frame,
                text="x",
                bg=ACCENT if active else SURFACE,
                fg="white" if active else MUTED,
                font=("Segoe UI", 9, "bold"),
                padx=6,
                pady=5,
                cursor="hand2",
            )
            close.pack(side=tk.LEFT)
            close.bind("<Button-1>", lambda _event, i=index: self.close_tab(i))
            close.bind("<Button-3>", lambda event, i=index: self.show_tab_menu(i, event))

    def show_tab_menu(self, index, event):
        menu = tk.Menu(self.root, tearoff=False)
        menu.add_command(label="Close tab", command=lambda: self.close_tab(index))
        menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def switch_tab(self, index):
        if index < 0 or index >= len(self.tabs):
            return "break"
        self.save_active_scroll()
        if self.current_file:
            self.nav_history.append(self.current_file)
        self.active_tab = index
        self.load_file(self.tabs[index]["path"], record_history=False)
        return "break"

    def switch_relative_tab(self, offset):
        if not self.tabs:
            return "break"
        current = self.active_tab if self.active_tab is not None else 0
        return self.switch_tab((current + offset) % len(self.tabs))

    def close_active_tab(self):
        return self.close_tab(self.active_tab)

    def close_tab(self, index):
        if index is None or index < 0 or index >= len(self.tabs):
            return "break"
        self.save_active_scroll()
        del self.tabs[index]
        if not self.tabs:
            self.active_tab = None
            self.current_file = None
            self.concept = {}
            self.content.clear()
            self.render_tabs()
            self.title_label.config(text="Vis2")
            self.subtitle_label.config(text="Component lesson visualizer")
            return "break"
        self.active_tab = min(index, len(self.tabs) - 1)
        self.load_file(self.tabs[self.active_tab]["path"], record_history=False)
        return "break"

    def go_back(self):
        self.save_active_scroll()
        while self.nav_history:
            path = self.nav_history.pop()
            if path and path.exists() and path != self.current_file:
                self.load_file(path, record_history=False)
                return "break"
        return "break"

    def handle_backspace_shortcut(self, event):
        if isinstance(event.widget, (tk.Entry, tk.Text, ttk.Entry)):
            return None
        return self.go_back()

    def open_find(self):
        if self.find_window.winfo_ismapped():
            self.find_entry.focus_set()
            if self.find_entry.get().strip():
                self.run_find()
            else:
                self.find_entry.select_range(0, tk.END)
            return "break"

        focused = self.root.focus_get()
        self.find_scope = "folders" if self.is_descendant(focused, self.file_tree) else "content"
        self.find_window.pack(fill=tk.X, padx=18, pady=(0, 8), before=self.content)
        self.find_entry.focus_set()
        self.find_entry.select_range(0, tk.END)
        return "break"

    def position_find_window(self):
        return

    def close_find(self):
        self.clear_find_highlight()
        self.find_window.pack_forget()
        self.find_matches = []
        self.find_index = -1
        return "break"

    def run_find(self):
        query = self.find_entry.get().strip()
        if not query:
            self.clear_find_highlight()
            self.find_status.config(text="")
            return "break"

        focused = self.root.focus_get()
        scope = "folders" if self.is_descendant(focused, self.file_tree) else self.find_scope
        if query != self.find_query or scope != self.find_scope or not self.find_matches:
            self.find_query = query
            self.find_scope = scope
            self.find_matches = self.folder_find_matches(query) if scope == "folders" else self.content_find_matches(query)
            self.find_index = -1

        if not self.find_matches:
            self.clear_find_highlight()
            self.find_status.config(text=f"No {self.find_scope} matches")
            return "break"

        self.find_index = (self.find_index + 1) % len(self.find_matches)
        self.show_find_match(self.find_matches[self.find_index])
        self.find_status.config(text=f"{self.find_scope.title()} match {self.find_index + 1} of {len(self.find_matches)}")
        return "break"

    def folder_find_matches(self, query):
        needle = query.lower()
        matches = []

        def visit(item):
            if needle in self.file_tree.item(item, "text").lower():
                matches.append(("folder", item))
            for child in self.file_tree.get_children(item):
                visit(child)

        for item in self.file_tree.get_children(""):
            visit(item)
        return matches

    def content_find_matches(self, query):
        needle = query.lower()
        matches = []

        def visit(widget):
            if isinstance(widget, tk.Label):
                text = widget.cget("text")
                if text and needle in str(text).lower():
                    matches.append(("label", widget))
            elif isinstance(widget, tk.Text):
                text = widget.get("1.0", tk.END)
                haystack = text.lower()
                start = haystack.find(needle)
                while start != -1:
                    matches.append(("text", widget, start, len(query)))
                    start = haystack.find(needle, start + max(1, len(needle)))
            for child in widget.winfo_children():
                visit(child)

        visit(self.content.inner)
        return matches

    def clear_find_highlight(self):
        if not self.find_highlight:
            return
        kind, widget, original_bg = self.find_highlight
        try:
            if kind == "label":
                widget.configure(bg=original_bg)
            elif kind == "text":
                widget.tag_remove("find_match", "1.0", tk.END)
        except tk.TclError:
            pass
        self.find_highlight = None

    def show_find_match(self, match):
        self.clear_find_highlight()
        kind, target, *details = match
        if kind == "folder":
            self.file_tree.selection_set(target)
            self.file_tree.focus(target)
            self.file_tree.see(target)
            self.file_tree.focus_set()
            return
        if kind == "label":
            original_bg = target.cget("bg")
            target.configure(bg="#fef3c7")
            self.find_highlight = ("label", target, original_bg)
            self.scroll_widget_into_view(target)
            return
        if details:
            start = f"1.0+{details[0]}c"
            end = f"{start}+{details[1]}c"
            target.tag_configure("find_match", background="#fef3c7", foreground=INK)
            target.tag_remove("find_match", "1.0", tk.END)
            target.tag_add("find_match", start, end)
            target.see(start)
            self.find_highlight = ("text", target, None)
            self.scroll_widget_into_view(target)

    def scroll_widget_into_view(self, widget):
        self.root.update_idletasks()
        y = 0
        current = widget
        while current is not None and current != self.content.inner:
            y += current.winfo_y()
            current = current.master
        bbox = self.content.canvas.bbox("all")
        if bbox and bbox[3] > 0:
            self.content.canvas.yview_moveto(max(0.0, min(1.0, y / bbox[3])))

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
        self.clear_find_highlight()
        self.find_matches = []
        self.find_index = -1
        self.image_refs = []
        self.content.clear()

        if not self.concept:
            self._empty_state("Open a component-style YAML concept to begin.")
            return

        if is_booklet(self.concept):
            self._render_booklet()
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
            label = tk.Label(
                panel,
                text=body,
                bg=APP_BG,
                fg=MUTED,
                font=("Segoe UI", 11),
                justify="left",
            )
            label.pack(anchor="w", fill=tk.X, pady=(6, 0))
            bind_wrap(label, panel)

    def _card(self, title=None, accent=ACCENT):
        outer = tk.Frame(self.content.inner, bg=APP_BG)
        outer.pack(fill=tk.X, padx=18, pady=8)

        stripe = tk.Frame(outer, bg=accent, width=5)
        stripe.pack(side=tk.LEFT, fill=tk.Y)

        card = tk.Frame(outer, bg=SURFACE, padx=16, pady=14, highlightbackground=LINE, highlightthickness=1)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if title:
            label = tk.Label(
                card,
                text=title,
                bg=SURFACE,
                fg=accent,
                font=("Segoe UI", 14, "bold"),
                anchor="w",
                justify="left",
            )
            label.pack(anchor="w", fill=tk.X, pady=(0, 8))
            bind_wrap(label, card)
        return card

    def _text(self, parent, text, size=10, color=INK, bold=False, mono=False):
        if not text:
            return
        font_family = "Consolas" if mono else "Segoe UI"
        font = (font_family, size, "bold") if bold else (font_family, size)
        label = tk.Label(
            parent,
            text=str(text).strip(),
            bg=parent.cget("bg"),
            fg=color,
            font=font,
            justify="left",
            anchor="w",
        )
        label.pack(anchor="w", fill=tk.X, pady=2)
        bind_wrap(label, parent)

    def _code_box(self, parent, language, code):
        shell = tk.Frame(parent, bg=CODE_BG, padx=8, pady=6)
        shell.pack(fill=tk.X, pady=(6, 0))
        header = tk.Frame(shell, bg=CODE_BG)
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text=language.upper(),
            bg=CODE_BG,
            fg=CODE_ACCENT,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(side=tk.LEFT)
        full_button = tk.Button(
            header,
            text="Expand",
            command=lambda: self.show_code_full(language, code),
            bg="#fed7aa",
            fg=CODE_ACCENT,
            activebackground="#fdba74",
            activeforeground="#7c2d12",
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            cursor="hand2",
        )
        full_button.pack(side=tk.RIGHT)

        box = tk.Text(shell, height=min(16, max(5, len(str(code).splitlines()) + 1)), bg=CODE_BG, fg=CODE_FG, insertbackground=CODE_FG, font=("Consolas", 10), wrap=tk.WORD, relief=tk.FLAT)
        box.pack(fill=tk.X, expand=True, pady=(6, 0))
        box.insert("1.0", str(code).rstrip())
        box.config(state=tk.DISABLED)
        box.bind("<Button-3>", lambda event: self.show_code_menu(event, language, code))
        return box

    def show_code_menu(self, event, language, code):
        menu = tk.Menu(self.root, tearoff=False)
        menu.add_command(label=f"View {clean_title(language)} code in full", command=lambda: self.show_code_full(language, code))
        menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def show_code_full(self, language, code):
        window = tk.Toplevel(self.root)
        window.title(f"{clean_title(language)} Code")
        window.geometry("980x720")
        window.configure(bg=APP_BG)
        header = tk.Frame(window, bg=INK)
        header.pack(fill=tk.X)
        tk.Label(header, text=f"{clean_title(language)} Code", bg=INK, fg="white", font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT, padx=14, pady=10)
        ttk.Button(header, text="Close", command=window.destroy).pack(side=tk.RIGHT, padx=14, pady=10)
        body = tk.Frame(window, bg=APP_BG, padx=12, pady=12)
        body.pack(fill=tk.BOTH, expand=True)
        box = tk.Text(body, bg=CODE_BG, fg=CODE_FG, insertbackground=CODE_FG, font=("Consolas", 11), wrap=tk.WORD)
        y_scroll = ttk.Scrollbar(body, orient="vertical", command=box.yview)
        box.configure(yscrollcommand=y_scroll.set)
        box.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)
        box.insert("1.0", str(code).rstrip())
        box.config(state=tk.DISABLED)
        window.bind("<Escape>", lambda _event: window.destroy())

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

    def _render_booklet(self):
        self._page_title(
            "Booklet",
            self.concept.get("title", "Untitled Booklet"),
            self.concept.get("goal") or self.concept.get("description"),
        )

        chapters = self.concept.get("chapters", [])
        if not chapters:
            self._empty_state("This booklet does not have chapters yet.")
            return

        for chapter_index, chapter in enumerate(chapters, start=1):
            card = self._card(f"{chapter_index}. {chapter.get('title', clean_title(chapter.get('id', 'chapter')))}", ACCENT)
            self._text(card, chapter.get("description"), color=MUTED)

            for section in chapter.get("sections", []):
                self._mini_heading(card, section.get("title", "Section"))
                if section.get("description"):
                    self._text(card, section.get("description"), color=MUTED)

                lessons = section.get("lessons", [])
                if not lessons:
                    self._text(card, "No lessons added yet.", color=MUTED)
                    continue

                for lesson in lessons:
                    self._booklet_lesson_row(card, lesson)

    def _booklet_lesson_row(self, parent, lesson):
        row = tk.Frame(parent, bg=SURFACE)
        row.pack(fill=tk.X, pady=3)

        title = lesson.get("title") or clean_title(lesson.get("id", "Lesson"))
        file_value = lesson.get("file") or lesson.get("path")
        status = lesson.get("status", "")

        label_text = title
        if status:
            label_text = f"{label_text}  [{status}]"
        color = topic_color(file_value or title)

        tk.Frame(row, bg=color, width=4).pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))

        label = tk.Label(
            row,
            text=label_text,
            bg=SURFACE,
            fg=color,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            justify="left",
            cursor="hand2" if file_value else "",
        )
        label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        if lesson.get("description"):
            Tooltip(label, lesson.get("description"))

        if file_value:
            target = self._resolve_lesson_path(file_value)
            label.bind("<Button-1>", lambda _event, path=target: self.open_booklet_lesson(path))
            tk.Label(row, text="No file", bg=SURFACE, fg=MUTED, font=("Segoe UI", 9)).pack(side=tk.RIGHT)

    def _resolve_lesson_path(self, file_value):
        path = Path(str(file_value))
        if path.is_absolute():
            return path

        candidates = []
        if self.current_file:
            candidates.append(self.current_file.parent / path)
        if self.base_folder:
            candidates.append(self.base_folder / path)
        candidates.append(PROJECT_ROOT / path)

        for candidate in candidates:
            if candidate.exists():
                return candidate
        return PROJECT_ROOT / path

    def open_booklet_lesson(self, path):
        path = Path(path)
        if not path.exists():
            messagebox.showerror("Lesson Not Found", f"Could not find:\n{path}")
            return "break"
        self.load_file(path, new_tab=True)
        self._select_file_in_sidebar(path)
        return "break"

    def _select_file_in_sidebar(self, path):
        if not self.base_folder:
            return
        try:
            target = Path(path).resolve()
        except Exception:
            return
        for index, item in enumerate(self.yaml_files):
            try:
                if item.resolve() == target:
                    item_id = self.file_tree_items.get(item)
                    if item_id:
                        self.file_tree.selection_set(item_id)
                        self.file_tree.focus(item_id)
                        self.file_tree.see(item_id)
                    return
            except Exception:
                continue

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
        raw_frame = tk.Frame(card, bg=SURFACE)
        raw_frame.pack(fill=tk.BOTH, expand=True)
        box = tk.Text(raw_frame, height=34, bg=CODE_BG, fg=CODE_FG, insertbackground="white", font=("Consolas", 10), wrap=tk.NONE)
        y_scroll = ttk.Scrollbar(raw_frame, orient="vertical", command=box.yview)
        x_scroll = ttk.Scrollbar(raw_frame, orient="horizontal", command=box.xview)
        box.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        box.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        raw_frame.grid_rowconfigure(0, weight=1)
        raw_frame.grid_columnconfigure(0, weight=1)
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

        languages = [language for language in self.selected_languages() if language_value(data, language)]
        if not languages:
            self._text(card, "No selected languages are available for this example.", color=MUTED)
            return
        for language in languages:
            self._code_box(card, language, language_value(data, language))

        self._text(card, data.get("note"), color=MUTED)

    def _render_table(self, data, accent=ACCENT):
        card = self._card(data.get("title", "Table"), accent)
        columns, rows = self._visible_table_data(data.get("columns", []), data.get("rows", []))

        self._render_wrapped_table(card, columns, rows, accent)

    def _render_stacked_table(self, parent, columns, rows, accent=ACCENT):
        if not columns:
            self._text(parent, "This table has no columns.", color=MUTED)
            return

        header = tk.Frame(parent, bg="#fff7ed", padx=10, pady=8, highlightbackground=LINE, highlightthickness=1)
        header.pack(fill=tk.X, pady=(4, 8))
        label = tk.Label(
            header,
            text=" | ".join(str(column) for column in columns),
            bg="#fff7ed",
            fg=accent,
            font=("Segoe UI", 10, "bold"),
            justify="left",
            anchor="w",
        )
        label.pack(anchor="w", fill=tk.X)
        bind_wrap(label, header)

        for row_index, row in enumerate(rows, start=1):
            row_card = tk.Frame(parent, bg="#fbfdff", padx=12, pady=10, highlightbackground=LINE, highlightthickness=1)
            row_card.pack(fill=tk.X, pady=6)
            tk.Label(
                row_card,
                text=f"Row {row_index}",
                bg="#fbfdff",
                fg=MUTED,
                font=("Segoe UI", 9, "bold"),
                anchor="w",
            ).pack(anchor="w", fill=tk.X, pady=(0, 4))
            for column_index, column in enumerate(columns):
                value = row[column_index] if column_index < len(row) else ""
                item = tk.Frame(row_card, bg="#fbfdff")
                item.pack(fill=tk.X, pady=2)
                tk.Label(
                    item,
                    text=str(column),
                    bg="#fbfdff",
                    fg=accent,
                    font=("Segoe UI", 9, "bold"),
                    anchor="nw",
                    justify="left",
                    width=22,
                ).pack(side=tk.LEFT, anchor="nw")
                value_label = tk.Label(
                    item,
                    text=str(value),
                    bg="#fbfdff",
                    fg=INK,
                    font=("Segoe UI", 10),
                    justify="left",
                    anchor="nw",
                )
                value_label.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor="nw")
                bind_wrap(value_label, item, margin=210, minimum=160)

    def _render_wrapped_table(self, parent, columns, rows, accent=ACCENT):
        if not columns:
            self._text(parent, "This table has no columns.", color=MUTED)
            return

        max_cols = 4
        first_column = columns[:1]
        other_columns = columns[1:]
        bands = [columns] if len(columns) <= max_cols else []
        if len(columns) > max_cols:
            band_size = max_cols - 1
            for start in range(0, len(other_columns), band_size):
                bands.append(first_column + other_columns[start:start + band_size])

        for band_index, band_columns in enumerate(bands):
            if len(bands) > 1:
                tk.Label(
                    parent,
                    text=f"Table view {band_index + 1}",
                    bg=SURFACE,
                    fg=MUTED,
                    font=("Segoe UI", 9, "bold"),
                    anchor="w",
                ).pack(anchor="w", fill=tk.X, pady=(8 if band_index else 4, 2))

            table = tk.Frame(parent, bg=LINE)
            table.pack(fill=tk.X, pady=(2, 8))
            for col_index, column in enumerate(band_columns):
                table.grid_columnconfigure(col_index, weight=1, uniform=f"table_{band_index}")
                self._table_cell(table, column, 0, col_index, header=True)

            source_indexes = [columns.index(column) for column in band_columns]
            for row_index, row in enumerate(rows, start=1):
                for col_index, source_index in enumerate(source_indexes):
                    value = row[source_index] if source_index < len(row) else ""
                    self._table_cell(table, value, row_index, col_index)

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
        label = tk.Label(
            parent,
            text=str(text),
            bg=bg,
            fg=fg,
            font=font,
            padx=10,
            pady=8,
            justify="left",
            anchor="nw",
        )
        label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
        label.bind("<Configure>", lambda event, item=label: item.configure(wraplength=max(120, event.width - 20)), add="+")

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
