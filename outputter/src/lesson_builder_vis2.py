import copy
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONCEPT = PROJECT_ROOT / "templates" / "vis2_welcome_template.yaml"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "knowledge"

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


BLOCKS = {
    "explain": {
        "icon": "📝",
        "title": "Explanation",
        "section": "lesson",
        "hint": "Add a plain-language explanation card.",
        "data": {"title": "What this means", "body": "Explain the concept in plain language."},
    },
    "image": {
        "icon": "🖼",
        "title": "Image",
        "section": "lesson",
        "hint": "Add an image placeholder that Vis2 can render later.",
        "data": {"asset": "main_diagram", "caption": "Describe what this image helps the learner notice."},
    },
    "compare_table": {
        "icon": "📊",
        "title": "Comparison Table",
        "section": "lesson",
        "hint": "Add a comparison table. Use | between columns.",
        "data": {
            "title": "Quick comparison",
            "columns": "Idea | Python | C++ | Java",
            "rows": "Common operation | Python form | C++ form | Java form",
        },
    },
    "language_lens": {
        "icon": "🧠",
        "title": "Language Lens",
        "section": "lesson",
        "hint": "Explain how one language wants the learner to think.",
        "data": {
            "language": "python",
            "title": "How Python wants you to think",
            "body": "Describe the language-specific mental model.",
            "default_instincts": "Use the natural standard-library tool first.",
            "avoid": "Do not carry over habits that make this language unnatural.",
        },
    },
    "code_compare": {
        "icon": "💻",
        "title": "Code Comparison",
        "section": "examples",
        "hint": "Add side-by-side interview-style code examples.",
        "data": {
            "title": "Example operation",
            "idea": "Explain the shared operation in one sentence.",
            "python": "# Python code here",
            "cpp": "// C++ code here",
            "java": "// Java code here",
            "note": "Explain the thinking difference.",
        },
    },
    "transition_path": {
        "icon": "↔",
        "title": "Transition Path",
        "section": "transitions",
        "hint": "Add source-to-target language habit shifts.",
        "data": {
            "source": "python",
            "target": "cpp",
            "title": "Moving from Python to C++",
            "mindset_shift": "From runtime flexibility to explicit types.\nFrom convenience to guarantees and costs.",
            "habit_swaps": "python: Use a flexible built-in quickly. | cpp: Choose by access pattern and cost.",
            "false_friends": "list | C++ list is a linked list, not Python list.",
        },
    },
    "revision_summary": {
        "icon": "⚡",
        "title": "Revision Summary",
        "section": "revision",
        "hint": "Add quick summary bullets for revision mode.",
        "data": {
            "points": "One compact all-language reminder.\nPython: one useful instinct.\nC++: one useful instinct.\nJava: one useful instinct.",
        },
    },
    "revision_table": {
        "icon": "🗺",
        "title": "Revision Table",
        "section": "revision",
        "hint": "Add a revision cheat table.",
        "data": {
            "title": "Revision map",
            "columns": "Need | Python instinct | C++ instinct | Java instinct",
            "rows": "Common task | Python answer | C++ answer | Java answer",
        },
    },
    "flashcard": {
        "icon": "?",
        "title": "Flashcard",
        "section": "revision",
        "hint": "Add a recall question and short answer.",
        "data": {"question": "What should the learner remember?", "answer": "Short answer."},
    },
}


FIELD_TYPES = {
    "body": "long",
    "python": "code",
    "cpp": "code",
    "java": "code",
    "note": "long",
    "mindset_shift": "list",
    "habit_swaps": "long",
    "false_friends": "long",
    "default_instincts": "list",
    "avoid": "list",
    "rows": "long",
    "points": "list",
}

DISPLAY_ICONS = {
    "explain": "[T]",
    "image": "[IMG]",
    "compare_table": "[TABLE]",
    "language_lens": "[LENS]",
    "code_compare": "[CODE]",
    "transition_path": "[->]",
    "revision_summary": "[REV]",
    "revision_table": "[GRID]",
    "flashcard": "[?]",
}


def clean_id(text):
    value = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text).strip())
    while "__" in value:
        value = value.replace("__", "_")
    return value.strip("_") or "new_concept"


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


def lines(value):
    return [line.strip() for line in str(value).splitlines() if line.strip()]


def split_cells(value):
    return [cell.strip() for cell in str(value).split("|")]


def load_yaml(path):
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def block_name(block):
    if not isinstance(block, dict) or not block:
        return "text", block
    key = next(iter(block))
    return key, block.get(key)


def block_icon(kind):
    return DISPLAY_ICONS.get(kind, BLOCKS.get(kind, {}).get("icon", "[+]"))


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


def parse_table(data):
    return {
        "title": data.get("title", "Table"),
        "columns": split_cells(data.get("columns", "")),
        "rows": [split_cells(row) for row in lines(data.get("rows", ""))],
    }


def parse_transition(data):
    source = clean_id(data.get("source", "python"))
    target = clean_id(data.get("target", "cpp"))
    swaps = []
    for row in lines(data.get("habit_swaps", "")):
        item = {}
        for part in split_cells(row):
            if ":" in part:
                key, value = part.split(":", 1)
                item[clean_id(key)] = value.strip()
        if item:
            swaps.append(item)

    false_friends = []
    for row in lines(data.get("false_friends", "")):
        term, *rest = split_cells(row)
        false_friends.append({"term": term, "warning": rest[0] if rest else ""})

    return f"{source}_to_{target}", {
        "title": data.get("title", f"Moving from {source} to {target}"),
        "mindset_shift": lines(data.get("mindset_shift", "")),
        "habit_swaps": swaps,
        "false_friends": false_friends,
    }


def table_to_editor(table):
    return {
        "title": table.get("title", ""),
        "columns": " | ".join(str(item) for item in table.get("columns", [])),
        "rows": "\n".join(" | ".join(str(cell) for cell in row) for row in table.get("rows", [])),
    }


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
        label = tk.Label(
            self.tip,
            text=self.text,
            bg="#111827",
            fg="white",
            padx=8,
            pady=5,
            wraplength=260,
            justify="left",
            font=("Segoe UI", 9),
        )
        label.pack()

    def hide(self, _event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


class ScrollFrame(ttk.Frame):
    def __init__(self, parent, bg=APP_BG):
        super().__init__(parent)
        self.mouse_active = False
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.inner.bind("<Configure>", lambda _event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda event: self.canvas.itemconfigure(self.window_id, width=event.width))
        self.canvas.bind("<Enter>", lambda _event: self.activate_mouse())
        self.canvas.bind("<Leave>", lambda _event: self.deactivate_mouse())
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def clear(self):
        for child in self.inner.winfo_children():
            child.destroy()

    def activate_mouse(self):
        self.mouse_active = True

    def deactivate_mouse(self):
        self.mouse_active = False

    def on_mousewheel(self, event):
        if self.mouse_active:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class LessonBuilderVis2:
    def __init__(self, root):
        self.root = root
        self.root.title("AnyLanguageExpressaic Builder Vis2")
        self.root.geometry("1420x860")
        self.root.minsize(1120, 720)
        self.root.configure(bg=APP_BG)
        maximize_window(self.root)

        self.current_file = None
        self.current_folder = DEFAULT_OUTPUT_DIR
        self.yaml_files = []
        self.file_tree_items = {}
        self.tabs = []
        self.active_tab = None
        self.nav_history = []
        self.find_window = None
        self.find_query = ""
        self.find_scope = "content"
        self.find_matches = []
        self.find_index = -1
        self.find_highlight = None
        self.image_refs = []
        self.available_languages = []
        self.language_vars = {}
        self.mode_var = tk.StringVar(value="lesson")
        self.source_var = tk.StringVar()
        self.target_var = tk.StringVar()
        self.concept = self.default_concept()
        self.components = []
        self.selected_index = None
        self.editing_index = None
        self.drag_component_index = None
        self.drag_preview = None
        self.drag_started = False
        self.drag_scroll_job = None
        self.drag_scroll_direction = 0
        self.drop_indicator = None
        self.undo_stack = []
        self.redo_stack = []
        self.field_widgets = {}
        self.meta_widgets = {}
        self.goal_text = None

        self.setup_style()
        self.build_menu()
        self.build_layout()
        self.bind_shortcuts()

        if DEFAULT_CONCEPT.exists():
            self.load_concept(load_yaml(DEFAULT_CONCEPT), push_undo=False)
        else:
            self.load_concept(self.default_concept(), push_undo=False)

    def default_concept(self):
        return {
            "id": "new_concept",
            "title": "New Concept",
            "category": "dsa",
            "level": "beginner_to_intermediate",
            "languages": ["python", "cpp", "java"],
            "tags": ["interview", "language_transition"],
            "goal": "Explain this concept for quick interview prep across languages.",
            "assets": {
                "main_diagram": {
                    "type": "image",
                    "path": "assets/dsa/new_concept/main-diagram.png",
                    "alt": "Diagram for this concept.",
                }
            },
            "lesson": [],
            "examples": [],
            "transitions": {},
            "revision": {"quick_summary": [], "cheat_table": {"title": "Revision map", "columns": ["Need", "Reminder"], "rows": []}, "flashcards": []},
            "tlm_hooks": {"possible_tasks": ["generate_interview_revision"], "context": "Interview-focused language transition lesson."},
        }

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=APP_BG)
        style.configure("TButton", font=("Segoe UI", 10), padding=(10, 6))
        style.configure("Primary.TButton", background=ACCENT, foreground="white")
        style.map("Primary.TButton", background=[("active", ACCENT_DARK)])
        style.configure("Danger.TButton", background=RED, foreground="white")
        style.configure("Mode.TRadiobutton", background=SURFACE_ALT, foreground=INK, font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", background="white", foreground=INK, fieldbackground="white", rowheight=26, font=("Segoe UI", 10))
        style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "white")])

    def build_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_lesson)
        file_menu.add_command(label="Open Folder...", accelerator="Ctrl+O", command=self.open_folder)
        file_menu.add_command(label="Open YAML...", accelerator="Ctrl+Shift+O", command=self.open_yaml)
        file_menu.add_separator()
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_yaml)
        file_menu.add_command(label="Save As...", command=self.save_yaml_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menu, tearoff=False)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Edit Selected", accelerator="Enter", command=self.edit_selected)
        edit_menu.add_command(label="Edit Selected YAML", accelerator="Ctrl+E", command=self.edit_selected_yaml)
        edit_menu.add_command(label="Move Selected Up", accelerator="Alt+Up", command=lambda: self.move_selected(-1))
        edit_menu.add_command(label="Move Selected Down", accelerator="Alt+Down", command=lambda: self.move_selected(1))
        edit_menu.add_command(label="Duplicate Selected", accelerator="Ctrl+D", command=self.duplicate_selected)
        edit_menu.add_command(label="Delete Selected", accelerator="Del", command=self.delete_selected)
        menu.add_cascade(label="Edit", menu=edit_menu)

        add_menu = tk.Menu(menu, tearoff=False)
        for index, (kind, spec) in enumerate(BLOCKS.items(), start=1):
            add_menu.add_command(label=f"{index}. {spec['title']}", command=lambda block_kind=kind: self.add_component(block_kind))
        menu.add_cascade(label="Add", menu=add_menu)

        view_menu = tk.Menu(menu, tearoff=False)
        view_menu.add_command(label="Back", accelerator="Alt+Left", command=self.go_back)
        view_menu.add_command(label="Find", accelerator="Ctrl+F", command=self.open_find)
        view_menu.add_separator()
        view_menu.add_command(label="Unselect Card", accelerator="Esc", command=self.stop_editing)
        view_menu.add_command(label="Open Card YAML", accelerator="Ctrl+E", command=self.edit_selected_yaml)
        menu.add_cascade(label="View", menu=view_menu)

    def build_layout(self):
        header = tk.Frame(self.root, bg=INK)
        header.pack(fill=tk.X)
        title_area = tk.Frame(header, bg=INK)
        title_area.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=18, pady=14)
        self.title_label = tk.Label(title_area, text="Builder Vis2", bg=INK, fg="white", font=("Segoe UI", 20, "bold"), anchor="w")
        self.title_label.pack(anchor="w", fill=tk.X)
        self.subtitle_label = tk.Label(title_area, text="Right-click any card to edit the lesson.", bg=INK, fg="#cbd5e1", font=("Segoe UI", 10), anchor="w")
        self.subtitle_label.pack(anchor="w", fill=tk.X, pady=(2, 0))
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
        ttk.Button(header, text="Save", command=self.save_yaml, style="Primary.TButton").pack(side=tk.RIGHT, padx=18, pady=14)

        body = tk.Frame(self.root, bg=APP_BG)
        body.pack(fill=tk.BOTH, expand=True)

        self.sidebar = tk.Frame(body, bg=SURFACE_ALT, width=260)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        self.build_folder_panel()

        builder_shell = tk.Frame(body, bg=APP_BG)
        builder_shell.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tab_bar = tk.Frame(builder_shell, bg=APP_BG)
        self.tab_bar.pack(fill=tk.X, padx=18, pady=(8, 0))
        self.find_window = tk.Frame(builder_shell, bg=APP_BG, highlightbackground=LINE, highlightthickness=1)
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
        self.builder_scroll = ScrollFrame(builder_shell)
        self.builder_scroll.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self.content = self.builder_scroll
        self.populate_file_list()

    def build_folder_panel(self):
        tk.Label(self.sidebar, text="YAML Folder", bg=SURFACE_ALT, fg=INK, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=14, pady=(16, 8))
        ttk.Button(self.sidebar, text="Open Folder", command=self.open_folder, style="Primary.TButton").pack(fill=tk.X, padx=14, pady=(0, 8))
        ttk.Button(self.sidebar, text="Open YAML", command=self.open_yaml).pack(fill=tk.X, padx=14, pady=(0, 12))

        view_panel = tk.Frame(self.sidebar, bg=SURFACE_ALT)
        view_panel.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=(0, 12))
        tk.Label(view_panel, text="View", bg=SURFACE_ALT, fg=INK, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=14, pady=(0, 8))
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
            selectmode="browse",
            height=10,
        )
        file_scroll = ttk.Scrollbar(file_area, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=file_scroll.set)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.bind("<Button-1>", lambda _event: self.file_tree.focus_set())
        self.file_tree.bind("<Double-Button-1>", self.open_selected_tree_item)
        self.file_tree.bind("<Return>", self.open_selected_tree_item)
        self.file_tree.bind("<Prior>", lambda _event: self.select_relative_file(-8))
        self.file_tree.bind("<Next>", lambda _event: self.select_relative_file(8))
        self.file_tree.bind("<Home>", lambda _event: self.select_file_at(0))
        self.file_tree.bind("<End>", lambda _event: self.select_file_at(len(self.yaml_files) - 1))

    def build_metadata_tab(self):
        return

    def bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda _event: self.new_lesson())
        self.root.bind("<Control-N>", lambda _event: self.new_lesson())
        self.root.bind("<Control-o>", lambda _event: self.open_folder())
        self.root.bind("<Control-O>", lambda _event: self.open_folder())
        self.root.bind("<Control-Shift-o>", lambda _event: self.open_yaml())
        self.root.bind("<Control-Shift-O>", lambda _event: self.open_yaml())
        self.root.bind("<Control-s>", lambda _event: self.save_yaml())
        self.root.bind("<Control-S>", lambda _event: self.save_yaml())
        self.root.bind("<Control-w>", lambda _event: self.close_active_tab())
        self.root.bind("<Control-W>", lambda _event: self.close_active_tab())
        self.root.bind("<Alt-Left>", lambda _event: self.go_back())
        self.root.bind("<Control-BackSpace>", lambda _event: self.go_back())
        self.root.bind("<Control-bracketleft>", lambda _event: self.go_back())
        self.root.bind("<Button-4>", lambda _event: self.go_back())
        self.root.bind("<BackSpace>", self.handle_backspace_shortcut)
        self.root.bind("<Control-f>", lambda _event: self.open_find())
        self.root.bind("<Control-F>", lambda _event: self.open_find())
        self.root.bind("<Control-z>", lambda _event: self.undo())
        self.root.bind("<Control-Z>", lambda _event: self.undo())
        self.root.bind("<Control-y>", lambda _event: self.redo())
        self.root.bind("<Control-Y>", lambda _event: self.redo())
        self.root.bind("<Control-d>", lambda _event: self.duplicate_selected())
        self.root.bind("<Control-D>", lambda _event: self.duplicate_selected())
        self.root.bind("<Delete>", lambda _event: self.delete_selected())
        self.root.bind("<Return>", self.handle_return_shortcut)
        self.root.bind("<Escape>", lambda _event: self.stop_editing())
        self.root.bind("<Control-e>", lambda _event: self.edit_selected_yaml())
        self.root.bind("<Control-E>", lambda _event: self.edit_selected_yaml())
        self.root.bind("<Alt-Up>", lambda _event: self.move_selected(-1))
        self.root.bind("<Alt-Down>", lambda _event: self.move_selected(1))
        self.root.bind("<Control-r>", lambda _event: self.reload_current_file())
        self.root.bind("<Control-R>", lambda _event: self.reload_current_file())
        self.root.bind("<Control-Key-1>", lambda _event: self.set_mode("lesson"))
        self.root.bind("<Control-Key-2>", lambda _event: self.set_mode("revision"))
        self.root.bind("<Control-Key-3>", lambda _event: self.set_mode("transition"))
        self.root.bind("<Control-Key-4>", lambda _event: self.set_mode("raw"))
        self.root.bind("<Control-Up>", lambda _event: self.select_relative_mode(-1))
        self.root.bind("<Control-Down>", lambda _event: self.select_relative_mode(1))
        self.root.bind("<Control-Left>", lambda _event: self.switch_relative_tab(-1))
        self.root.bind("<Control-Right>", lambda _event: self.switch_relative_tab(1))
        self.root.bind("<Up>", lambda event: self.handle_arrow_key(event, -3))
        self.root.bind("<Down>", lambda event: self.handle_arrow_key(event, 3))
        self.root.bind("<Prior>", lambda event: self.handle_arrow_key(event, -9))
        self.root.bind("<Next>", lambda event: self.handle_arrow_key(event, 9))
        self.root.bind("<Control-Return>", lambda _event: self.show_transition())
        self.root.bind("<Control-t>", lambda _event: self.show_transition())
        self.root.bind("<Control-T>", lambda _event: self.show_transition())
        self.root.bind("<Control-Shift-T>", lambda _event: self.swap_transition_languages())
        for index, kind in enumerate(BLOCKS, start=1):
            self.root.bind(f"<Control-Alt-Key-{index}>", lambda _event, block_kind=kind: self.add_component(block_kind))

    def push_undo(self):
        self.undo_stack.append(copy.deepcopy((self.concept, self.components)))
        self.redo_stack.clear()
        if len(self.undo_stack) > 80:
            self.undo_stack.pop(0)

    def undo(self):
        if not self.undo_stack:
            return "break"
        self.redo_stack.append(copy.deepcopy((self.concept, self.components)))
        self.concept, self.components = self.undo_stack.pop()
        self.selected_index = None
        self.editing_index = None
        self.render_all()
        return "break"

    def redo(self):
        if not self.redo_stack:
            return "break"
        self.undo_stack.append(copy.deepcopy((self.concept, self.components)))
        self.concept, self.components = self.redo_stack.pop()
        self.selected_index = None
        self.editing_index = None
        self.render_all()
        return "break"

    def show_add_menu(self, insert_index, event=None):
        menu = tk.Menu(self.root, tearoff=False)
        for index, (kind, spec) in enumerate(BLOCKS.items(), start=1):
            label = f"{block_icon(kind)}  {spec['title']}    Ctrl+Alt+{index}"
            menu.add_command(label=label, command=lambda block_kind=kind: self.add_component(block_kind, insert_index))

        if event:
            x = event.x_root
            y = event.y_root
        else:
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
        menu.tk_popup(x, y)

    def add_component(self, kind, insert_index=None):
        self.push_undo()
        spec = BLOCKS[kind]
        component = {"kind": kind, "section": spec["section"], "data": copy.deepcopy(spec["data"])}
        if insert_index is None:
            insert_index = self.selected_index + 1 if self.selected_index is not None else len(self.components)
        insert_index = max(0, min(insert_index, len(self.components)))
        self.components.insert(insert_index, component)
        self.selected_index = insert_index
        self.editing_index = None
        self.render_all()
        return "break"

    def select_component(self, index):
        self.selected_index = index
        self.editing_index = None
        self.render()

    def edit_component(self, index):
        self.selected_index = index
        self.editing_index = index
        self.render()

    def edit_selected(self):
        if self.selected_index is not None:
            self.edit_component(self.selected_index)
        return "break"

    def handle_return_shortcut(self, event):
        if isinstance(event.widget, (tk.Text, tk.Entry)):
            return None
        if hasattr(self, "file_tree") and self.is_descendant(event.widget, self.file_tree):
            return self.open_selected_tree_item()
        return self.edit_selected()

    def stop_editing(self):
        self.selected_index = None
        self.editing_index = None
        self.render()
        return "break"

    def duplicate_selected(self):
        if self.selected_index is None:
            return "break"
        self.push_undo()
        self.components.insert(self.selected_index + 1, copy.deepcopy(self.components[self.selected_index]))
        self.selected_index += 1
        self.editing_index = None
        self.render_all()
        return "break"

    def delete_selected(self):
        if self.selected_index is None:
            return "break"
        self.push_undo()
        del self.components[self.selected_index]
        self.selected_index = min(self.selected_index, len(self.components) - 1) if self.components else None
        self.editing_index = None
        self.render_all()
        return "break"

    def begin_component_drag(self, index, event=None):
        self.drag_component_index = index
        self.drag_started = False
        self.root.configure(cursor="fleur")

    def create_drag_preview(self, index, event=None):
        self.destroy_drag_preview()
        if index is None or index < 0 or index >= len(self.components):
            return
        component = self.components[index]
        self.drag_preview = tk.Toplevel(self.root)
        self.drag_preview.overrideredirect(True)
        self.drag_preview.attributes("-alpha", 0.86)
        frame = tk.Frame(self.drag_preview, bg=SURFACE, padx=12, pady=8, highlightbackground=ACCENT, highlightthickness=2)
        frame.pack()
        tk.Label(frame, text=f"{block_icon(component['kind'])} {BLOCKS[component['kind']]['title']}", bg=SURFACE, fg=INK, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(frame, text=self.component_summary(component), bg=SURFACE, fg=MUTED, font=("Segoe UI", 9), wraplength=360, justify="left").pack(anchor="w")
        self.move_drag_preview(event)

    def move_drag_preview(self, event=None):
        if not self.drag_preview:
            return
        x = event.x_root + 14 if event else self.root.winfo_pointerx() + 14
        y = event.y_root + 14 if event else self.root.winfo_pointery() + 14
        self.drag_preview.geometry(f"+{x}+{y}")

    def destroy_drag_preview(self):
        if self.drag_preview:
            self.drag_preview.destroy()
            self.drag_preview = None

    def drag_component_motion(self, event):
        if self.drag_component_index is None:
            return
        self.drag_started = True
        if not self.drag_preview:
            self.create_drag_preview(self.drag_component_index, event)
        self.move_drag_preview(event)
        self.auto_scroll_during_drag(event)

    def auto_scroll_during_drag(self, event):
        canvas = self.builder_scroll.canvas
        top = canvas.winfo_rooty()
        bottom = top + canvas.winfo_height()
        margin = 56
        direction = 0
        if event.y_root < top + margin:
            direction = -1
        elif event.y_root > bottom - margin:
            direction = 1
        self.drag_scroll_direction = direction
        if direction:
            canvas.yview_scroll(direction * 2, "units")
            self.refresh_card_positions()
            if self.drag_scroll_job is None:
                self.drag_scroll_job = self.root.after(70, self.continue_drag_scroll)
        elif self.drag_scroll_job is not None:
            self.root.after_cancel(self.drag_scroll_job)
            self.drag_scroll_job = None

    def continue_drag_scroll(self):
        self.drag_scroll_job = None
        if not self.drag_started or self.drag_component_index is None or not self.drag_scroll_direction:
            return
        pointer_y = self.root.winfo_pointery()
        canvas = self.builder_scroll.canvas
        top = canvas.winfo_rooty()
        bottom = top + canvas.winfo_height()
        margin = 56
        if self.drag_scroll_direction < 0 and pointer_y < top + margin:
            canvas.yview_scroll(-2, "units")
        elif self.drag_scroll_direction > 0 and pointer_y > bottom - margin:
            canvas.yview_scroll(2, "units")
        else:
            self.drag_scroll_direction = 0
            return
        self.refresh_card_positions()
        self.drag_scroll_job = self.root.after(70, self.continue_drag_scroll)

    def stop_drag_scroll(self):
        self.drag_scroll_direction = 0
        if self.drag_scroll_job is not None:
            self.root.after_cancel(self.drag_scroll_job)
            self.drag_scroll_job = None

    def refresh_card_positions(self):
        self.card_positions = []
        self.root.update_idletasks()
        for child in self.builder_scroll.inner.winfo_children():
            index = getattr(child, "card_index", None)
            if index is not None:
                self.record_card_position(child, index)

    def complete_component_drag(self, target_slot):
        self.root.configure(cursor="")
        self.stop_drag_scroll()
        self.destroy_drag_preview()
        if self.drag_component_index is None:
            self.drag_component_index = None
            self.drag_started = False
            return
        source_index = self.drag_component_index
        target_slot = max(0, min(target_slot, len(self.components)))
        target_index = target_slot - 1 if target_slot > source_index else target_slot
        target_index = max(0, min(target_index, len(self.components) - 1))
        if target_index == source_index:
            self.drag_component_index = None
            self.drag_started = False
            return
        self.push_undo()
        item = self.components.pop(source_index)
        self.components.insert(target_index, item)
        self.selected_index = target_index
        self.drag_component_index = None
        self.drag_started = False
        self.render_all()

    def complete_component_drag_at_pointer(self, event):
        if self.drag_component_index is None:
            return
        if not self.drag_started or not self.drag_preview:
            self.root.configure(cursor="")
            self.stop_drag_scroll()
            self.drag_component_index = None
            self.drag_started = False
            return

        pointer_y = event.y_root
        self.refresh_card_positions()
        positions = sorted(getattr(self, "card_positions", []), key=lambda item: item[1])
        target_slot = len(self.components)
        for index, _top, midpoint, _bottom in positions:
            if pointer_y < midpoint:
                target_slot = index
                break

        self.complete_component_drag(target_slot)

    def metadata_changed(self):
        self.concept["id"] = clean_id(self.meta_widgets["id"].get())
        self.concept["title"] = self.meta_widgets["title"].get().strip() or "Untitled"
        self.concept["category"] = clean_id(self.meta_widgets["category"].get())
        self.concept["level"] = clean_id(self.meta_widgets["level"].get())
        self.concept["languages"] = [clean_id(item) for item in self.meta_widgets["languages"].get().split(",") if item.strip()]
        self.concept["tags"] = [clean_id(item) for item in self.meta_widgets["tags"].get().split(",") if item.strip()]
        self.concept["goal"] = self.goal_text.get("1.0", tk.END).strip()

    def load_concept(self, concept, push_undo=True):
        if push_undo:
            self.push_undo()
        self.concept = copy.deepcopy(concept)
        self.components = [] if is_booklet(self.concept) else self.concept_to_components(concept)
        self.selected_index = None
        self.editing_index = None
        self.render_all()
        self.populate_metadata()

    def populate_metadata(self):
        values = {
            "id": self.concept.get("id", ""),
            "title": self.concept.get("title", ""),
            "category": self.concept.get("category", ""),
            "level": self.concept.get("level", ""),
            "languages": ", ".join(self.concept.get("languages", [])),
            "tags": ", ".join(self.concept.get("tags", [])),
        }
        for key, value in values.items():
            if key not in self.meta_widgets:
                continue
            self.meta_widgets[key].delete(0, tk.END)
            self.meta_widgets[key].insert(0, value)
        if self.goal_text:
            self.goal_text.delete("1.0", tk.END)
            self.goal_text.insert("1.0", self.concept.get("goal", ""))

    def render_all(self):
        self.render()

    def render_study(self):
        self.render()

    def current_concept_snapshot(self):
        if is_booklet(self.concept):
            return copy.deepcopy(self.concept)
        return copy.deepcopy(self.build_concept())

    def save_active_tab_state(self):
        if self.active_tab is None or self.active_tab >= len(self.tabs):
            return
        tab = self.tabs[self.active_tab]
        try:
            tab["scroll"] = self.content.canvas.yview()[0]
        except Exception:
            tab["scroll"] = tab.get("scroll", 0.0)
        tab["concept"] = self.current_concept_snapshot()
        tab["title"] = tab["concept"].get("title") or clean_title(tab["concept"].get("id", Path(tab.get("path", "lesson")).stem))

    def restore_active_scroll(self):
        if self.active_tab is None or self.active_tab >= len(self.tabs):
            return
        scroll = self.tabs[self.active_tab].get("scroll", 0.0)
        self.root.after(30, lambda value=scroll: self.content.canvas.yview_moveto(value))

    def open_or_update_tab(self, path, concept, new_tab=False):
        path = Path(path)
        title = concept.get("title") or clean_title(concept.get("id", path.stem))
        existing = None
        for index, tab in enumerate(self.tabs):
            if tab["path"] == path:
                existing = index
                break

        if existing is not None:
            old_scroll = self.tabs[existing].get("scroll", 0.0)
            self.tabs[existing] = {"path": path, "title": title, "scroll": old_scroll, "concept": copy.deepcopy(concept)}
            self.active_tab = existing
        elif new_tab or self.active_tab is None:
            self.tabs.append({"path": path, "title": title, "scroll": 0.0, "concept": copy.deepcopy(concept)})
            self.active_tab = len(self.tabs) - 1
        else:
            self.tabs[self.active_tab] = {"path": path, "title": title, "scroll": 0.0, "concept": copy.deepcopy(concept)}

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

    def switch_tab(self, index, record_history=True):
        if index < 0 or index >= len(self.tabs):
            return "break"
        if index == self.active_tab:
            return "break"
        self.save_active_tab_state()
        if record_history and self.current_file:
            self.nav_history.append(self.current_file)
        self.active_tab = index
        tab = self.tabs[index]
        self.current_file = tab["path"]
        self.adopt_file_folder(self.current_file)
        self.load_concept(copy.deepcopy(tab["concept"]), push_undo=False)
        self.update_file_title()
        self.render_tabs()
        self.restore_active_scroll()
        self.select_open_file_in_sidebar(self.current_file)
        return "break"

    def close_active_tab(self):
        return self.close_tab(self.active_tab)

    def switch_relative_tab(self, offset):
        if not self.tabs:
            return "break"
        current = self.active_tab if self.active_tab is not None else 0
        return self.switch_tab((current + offset) % len(self.tabs))

    def close_tab(self, index):
        if index is None or index < 0 or index >= len(self.tabs):
            return "break"
        if index == self.active_tab:
            self.save_active_tab_state()
        del self.tabs[index]
        if not self.tabs:
            self.active_tab = None
            self.current_file = None
            self.concept = self.default_concept()
            self.components = []
            self.builder_scroll.clear()
            self.render_tabs()
            self.title_label.config(text="Builder Vis2")
            self.subtitle_label.config(text="Right-click any card to edit the lesson.")
            return "break"
        self.active_tab = min(index, len(self.tabs) - 1)
        tab = self.tabs[self.active_tab]
        self.current_file = tab["path"]
        self.adopt_file_folder(self.current_file)
        self.load_concept(copy.deepcopy(tab["concept"]), push_undo=False)
        self.update_file_title()
        self.render_tabs()
        self.restore_active_scroll()
        self.select_open_file_in_sidebar(self.current_file)
        return "break"

    def go_back(self):
        self.save_active_tab_state()
        while self.nav_history:
            path = self.nav_history.pop()
            if path and path.exists() and path != self.current_file:
                self.load_file(path, new_tab=False, record_history=False)
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
        self.find_scope = "folders" if hasattr(self, "file_tree") and self.is_descendant(focused, self.file_tree) else "content"
        self.find_window.pack(fill=tk.X, padx=18, pady=(8, 0), before=self.builder_scroll)
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
        scope = "folders" if hasattr(self, "file_tree") and self.is_descendant(focused, self.file_tree) else self.find_scope
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

    def handle_arrow_key(self, event, direction):
        focused = self.root.focus_get()
        if hasattr(self, "file_tree") and self.is_descendant(focused, self.file_tree):
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

    def update_file_title(self):
        title = self.concept.get("title") or clean_title(self.concept.get("id", "Untitled Concept"))
        self.title_label.config(text=title)
        self.subtitle_label.config(text=str(self.current_file) if self.current_file else "Unsaved lesson")

    def adopt_file_folder(self, path):
        path = Path(path)
        folder = Path(self.current_folder or DEFAULT_OUTPUT_DIR)
        try:
            if path.is_relative_to(folder):
                return
        except Exception:
            pass
        self.current_folder = path.parent
        self.populate_file_list()

    def render(self):
        self.clear_find_highlight()
        self.find_matches = []
        self.find_index = -1
        self.image_refs = []
        self.builder_scroll.clear()
        self.card_positions = []
        if not is_booklet(self.concept):
            self.concept = self.build_concept()
        self._populate_languages()

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
        if self.available_languages:
            if self.source_var.get() not in self.available_languages:
                self.source_var.set(self.available_languages[0])
            if self.target_var.get() not in self.available_languages:
                self.target_var.set(self.available_languages[1] if len(self.available_languages) > 1 else self.available_languages[0])

    def selected_languages(self):
        return [
            language
            for language in self.available_languages
            if self.language_vars.get(language) and self.language_vars[language].get()
        ]

    def set_mode(self, mode):
        self.mode_var.set(mode)
        self.render()
        return "break"

    def select_relative_mode(self, offset):
        modes = ["lesson", "revision", "transition", "raw"]
        current = self.mode_var.get()
        index = modes.index(current) if current in modes else 0
        return self.set_mode(modes[(index + offset) % len(modes)])

    def show_transition(self):
        return self.set_mode("transition")

    def swap_transition_languages(self):
        source = self.source_var.get()
        target = self.target_var.get()
        self.source_var.set(target)
        self.target_var.set(source)
        return self.set_mode("transition")

    def _page_title(self, eyebrow, title, body=None):
        frame = tk.Frame(self.builder_scroll.inner, bg=APP_BG)
        frame.pack(fill=tk.X, padx=18, pady=(10, 14))
        tk.Label(frame, text=eyebrow.upper(), bg=APP_BG, fg=ACCENT, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(frame, text=title, bg=APP_BG, fg=INK, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        if body:
            label = tk.Label(frame, text=body, bg=APP_BG, fg=MUTED, font=("Segoe UI", 11), justify="left")
            label.pack(anchor="w", fill=tk.X, pady=(6, 0))
            bind_wrap(label, frame)
        frame.bind("<Button-3>", self.show_page_menu)

    def _language_filter(self):
        if not self.available_languages:
            return
        bar = tk.Frame(self.builder_scroll.inner, bg=APP_BG)
        bar.pack(fill=tk.X, padx=18, pady=(0, 8))
        tk.Label(bar, text="Visible languages", bg=APP_BG, fg=MUTED, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 8))
        selected = self.selected_languages()
        if not selected:
            label = "No languages selected"
        elif len(selected) <= 3:
            label = ", ".join(clean_title(language) for language in selected)
        else:
            label = f"{', '.join(clean_title(language) for language in selected[:2])} +{len(selected) - 2}"
        menu_button = tk.Menubutton(
            bar,
            text=label,
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
            menu.add_checkbutton(label=clean_title(language), variable=self.language_vars[language], command=self.render)
        menu.add_separator()
        menu.add_command(label="Show all", command=self.show_all_languages)
        menu_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def show_all_languages(self):
        for variable in self.language_vars.values():
            variable.set(True)
        self.render()

    def _render_lesson(self):
        self._page_title("Lesson Mode", self.concept.get("title", "Untitled Concept"), self.concept.get("goal"))
        self._language_filter()
        for index, component in enumerate(self.components):
            if component["section"] == "lesson":
                self.render_read_component(component, index)
        if any(component["section"] == "examples" for component in self.components):
            self._section_heading("Examples")
            for index, component in enumerate(self.components):
                if component["section"] == "examples":
                    self.render_read_component(component, index)

    def _render_booklet(self):
        self._page_title(
            "Booklet",
            self.concept.get("title", "Untitled Booklet"),
            self.concept.get("goal") or self.concept.get("description"),
        )

        chapters = self.concept.setdefault("chapters", [])
        if not chapters:
            card = self.editable_card("No Chapters", RED, None)
            self.text(card, "Right-click the page title area and choose Add chapter.")
            return

        for chapter_index, chapter in enumerate(chapters):
            title = f"{chapter_index + 1}. {chapter.get('title', clean_title(chapter.get('id', 'chapter')))}"
            card = self.booklet_card(title, ACCENT, lambda event, i=chapter_index: self.show_chapter_menu(i, event))
            self.text(card, chapter.get("description", ""), MUTED)

            sections = chapter.setdefault("sections", [])
            if not sections:
                self.text(card, "No sections yet. Right-click this chapter to add one.", MUTED)
                continue

            for section_index, section in enumerate(sections):
                section_label = tk.Label(card, text=section.get("title", "Section"), bg=SURFACE, fg=INK, font=("Segoe UI", 11, "bold"), anchor="w")
                section_label.pack(anchor="w", fill=tk.X, pady=(10, 2))
                section_label.bind("<Button-3>", lambda event, ci=chapter_index, si=section_index: self.show_section_menu(ci, si, event))
                if section.get("description"):
                    self.text(card, section.get("description"), MUTED)

                lessons = section.setdefault("lessons", [])
                if not lessons:
                    self.text(card, "No lessons added yet.", MUTED)
                    continue

                for lesson_index, lesson in enumerate(lessons):
                    self.booklet_lesson_row(card, chapter_index, section_index, lesson_index, lesson)

    def booklet_card(self, title, accent, menu_callback):
        outer = tk.Frame(self.builder_scroll.inner, bg=APP_BG)
        outer.pack(fill=tk.X, padx=18, pady=8)
        tk.Frame(outer, bg=accent, width=5).pack(side=tk.LEFT, fill=tk.Y)
        card = tk.Frame(outer, bg=SURFACE, padx=16, pady=14, highlightbackground=LINE, highlightthickness=1)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        label = tk.Label(card, text=title, bg=SURFACE, fg=accent, font=("Segoe UI", 14, "bold"), anchor="w")
        label.pack(anchor="w", fill=tk.X, pady=(0, 8))
        for widget in (outer, card, label):
            widget.bind("<Button-3>", menu_callback)
        return card

    def booklet_lesson_row(self, parent, chapter_index, section_index, lesson_index, lesson):
        row = tk.Frame(parent, bg=SURFACE)
        row.pack(fill=tk.X, pady=3)
        title = lesson.get("title") or clean_title(lesson.get("id", "Lesson"))
        file_value = lesson.get("file") or lesson.get("path")
        status = lesson.get("status", "")
        label_text = f"{title}  [{status}]" if status else title
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
        label.bind("<Button-3>", lambda event, ci=chapter_index, si=section_index, li=lesson_index: self.show_lesson_link_menu(ci, si, li, event))

        if file_value:
            target = self.resolve_lesson_path(file_value)
            label.bind("<Button-1>", lambda _event, path=target: self.open_booklet_lesson(path))
            ttk.Button(row, text="Open", command=lambda path=target: self.open_booklet_lesson(path)).pack(side=tk.RIGHT, padx=(8, 0))
        else:
            tk.Label(row, text="No file", bg=SURFACE, fg=MUTED, font=("Segoe UI", 9)).pack(side=tk.RIGHT)

    def _render_revision(self):
        self._page_title("Revision Mode", self.concept.get("title", "Untitled Concept"), "Fast review material.")
        self._language_filter()
        for index, component in enumerate(self.components):
            if component["section"] == "revision":
                self.render_read_component(component, index)

    def _render_transition(self):
        selected = self.selected_languages()
        if selected and self.source_var.get() not in selected:
            self.source_var.set(selected[0])
        if selected and self.target_var.get() not in selected:
            self.target_var.set(selected[1] if len(selected) > 1 else selected[0])

        source = self.source_var.get()
        target = self.target_var.get()
        key = f"{source}_to_{target}"
        self._page_title("Transition Mode", clean_title(key), "How to change habits when moving from one language to another.")
        self._language_filter()
        self._transition_controls()
        if len(selected) < 2:
            self._empty_state("Select at least two visible languages to compare a transition path.")
            return
        for index, component in enumerate(self.components):
            data = component["data"]
            if component["kind"] == "transition_path" and clean_id(data.get("source", "")) == source and clean_id(data.get("target", "")) == target:
                self.render_read_component(component, index)
                return
        self._empty_state(f"No transition path found for '{key}'.")

    def _transition_controls(self):
        visible_languages = self.selected_languages()
        if not visible_languages:
            return
        card = self.editable_card("Transition Path", ACCENT, None)
        row = tk.Frame(card, bg=SURFACE)
        row.pack(fill=tk.X)
        tk.Label(row, text="From", bg=SURFACE, fg=MUTED, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 8))
        source_combo = ttk.Combobox(row, textvariable=self.source_var, state="readonly", values=visible_languages)
        source_combo.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        source_combo.bind("<<ComboboxSelected>>", lambda _event: self.show_transition())
        tk.Label(row, text="To", bg=SURFACE, fg=MUTED, font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w", padx=(0, 8))
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
        card = self.editable_card("Filtered YAML Preview", ACCENT, None)
        raw_area = tk.Frame(card, bg=CODE_BG)
        raw_area.pack(fill=tk.BOTH, expand=True)
        box = tk.Text(raw_area, height=34, bg=CODE_BG, fg=CODE_FG, insertbackground=CODE_FG, font=("Consolas", 10), wrap=tk.NONE)
        y_scroll = ttk.Scrollbar(raw_area, orient="vertical", command=box.yview)
        x_scroll = ttk.Scrollbar(raw_area, orient="horizontal", command=box.xview)
        box.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        box.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        raw_area.grid_rowconfigure(0, weight=1)
        raw_area.grid_columnconfigure(0, weight=1)
        box.insert("1.0", yaml.safe_dump(self._filtered_raw_concept(), sort_keys=False, allow_unicode=True))
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
        filtered["languages"] = [language for language in self.concept.get("languages", []) if language_key(language) in selected]
        filtered["lesson"] = self._filter_blocks(self.concept.get("lesson", []), selected)
        filtered["examples"] = self._filter_blocks(self.concept.get("examples", []), selected)
        filtered["transitions"] = {
            key: value
            for key, value in self.concept.get("transitions", {}).items()
            if len(key.split("_to_")) == 2 and key.split("_to_")[0] in selected and key.split("_to_")[1] in selected
        }
        revision = dict(self.concept.get("revision", {}))
        if revision.get("cheat_table"):
            columns, rows = self.visible_table_data(revision["cheat_table"].get("columns", []), revision["cheat_table"].get("rows", []))
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
                columns, rows = self.visible_table_data(data.get("columns", []), data.get("rows", []))
                next_data = dict(data)
                next_data["columns"] = columns
                next_data["rows"] = rows
                filtered.append({kind: next_data})
                continue
            filtered.append(block)
        return filtered

    def render_read_component(self, component, index):
        kind = component["kind"]
        data = component["data"]
        if kind == "language_lens" and language_key(data.get("language", "")) not in self.selected_languages():
            return
        if kind == "explain":
            card = self.editable_card(data.get("title", "Explanation"), ACCENT, index)
            self.text(card, data.get("body", ""))
        elif kind == "language_lens":
            card = self.editable_card(data.get("title", "Language Lens"), GREEN, index)
            self.text(card, data.get("body", ""))
            if data.get("default_instincts"):
                self.mini_heading(card, "Default Instincts")
                self.bullet_list(card, lines(data.get("default_instincts", "")))
            if data.get("avoid"):
                self.mini_heading(card, "Avoid")
                self.bullet_list(card, lines(data.get("avoid", "")))
        elif kind == "code_compare":
            card = self.editable_card(data.get("title", "Code Comparison"), AMBER, index)
            self.text(card, data.get("idea", ""), MUTED)
            languages = [language for language in self.selected_languages() if language_value(data, language)]
            if not languages:
                self.text(card, "No selected languages are available for this example.", MUTED)
            else:
                for language in languages:
                    self._code_box(card, language, language_value(data, language), index=index)
            self.text(card, data.get("note", ""), MUTED)
        elif kind in {"compare_table", "revision_table"}:
            table = parse_table(data)
            card = self.editable_card(table.get("title", "Table"), PURPLE, index)
            columns, rows = self.visible_table_data(table.get("columns", []), table.get("rows", []))
            self.render_table(card, columns, rows)
        elif kind == "image":
            card = self.editable_card(data.get("caption", "Image"), PURPLE, index)
            path = self.resolve_asset(data.get("path") or self.concept.get("assets", {}).get(data.get("asset"), {}).get("path"))
            if path and path.exists():
                try:
                    image = tk.PhotoImage(file=str(path))
                    self.image_refs.append(image)
                    label = tk.Label(card, image=image, bg=SURFACE)
                    label.pack(anchor="w", pady=(2, 8))
                    self.bind_to_component(label, index)
                except tk.TclError:
                    self.text(card, f"Image placeholder: {path}", MUTED)
            else:
                self.text(card, f"Image placeholder: {data.get('asset', '')}", MUTED)
        elif kind == "transition_path":
            card = self.editable_card(data.get("title", "Transition Path"), PURPLE, index)
            if data.get("mindset_shift"):
                self.mini_heading(card, "Mindset Shift")
                self.bullet_list(card, lines(data.get("mindset_shift", "")))
            if data.get("habit_swaps"):
                self.mini_heading(card, "Habit Swaps")
                self.bullet_list(card, lines(data.get("habit_swaps", "")))
            if data.get("false_friends"):
                self.mini_heading(card, "False Friends")
                for row in lines(data.get("false_friends", "")):
                    term, *rest = split_cells(row)
                    self.text(card, term, RED)
                    self.text(card, rest[0] if rest else "", INK)
        elif kind == "revision_summary":
            card = self.editable_card("Quick Summary", GREEN, index)
            self.bullet_list(card, lines(data.get("points", "")))
        elif kind == "flashcard":
            card = self.editable_card(data.get("question", "Flashcard"), AMBER, index)
            self.text(card, data.get("answer", ""), MUTED)

    def visible_table_data(self, columns, rows):
        selected = set(self.selected_languages())
        if not self.available_languages or not selected:
            return columns, rows
        visible_indexes = []
        for index, column in enumerate(columns):
            key = column_language_key(column, self.available_languages)
            if key is None or key in selected:
                visible_indexes.append(index)
        return [columns[index] for index in visible_indexes], [[row[index] if index < len(row) else "" for index in visible_indexes] for row in rows]

    def bullet_list(self, parent, items):
        for item in as_list(items):
            self.text(parent, f"- {item}")

    def mini_heading(self, parent, value):
        label = tk.Label(parent, text=value, bg=parent.cget("bg"), fg=INK, font=("Segoe UI", 11, "bold"), anchor="w")
        label.pack(anchor="w", fill=tk.X, pady=(10, 2))
        self.bind_to_component(label, getattr(parent, "edit_index", None))

    def _section_heading(self, value):
        tk.Label(self.builder_scroll.inner, text=value, bg=APP_BG, fg=INK, font=("Segoe UI", 18, "bold"), anchor="w").pack(anchor="w", fill=tk.X, padx=18, pady=(18, 4))

    def _empty_state(self, message):
        card = self.editable_card("Nothing to show", RED, None)
        self.text(card, message, MUTED)

    def resolve_asset(self, path_value):
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

    def editable_card(self, title=None, accent=ACCENT, index=None):
        outer = tk.Frame(self.builder_scroll.inner, bg=APP_BG)
        if index is not None:
            outer.card_index = index
        outer.pack(fill=tk.X, padx=18, pady=8)
        if index is not None:
            self.root.after(10, lambda frame=outer, i=index: self.record_card_position(frame, i))
        tk.Frame(outer, bg=accent, width=5).pack(side=tk.LEFT, fill=tk.Y)
        card = tk.Frame(outer, bg=SURFACE, padx=16, pady=14, highlightbackground=ACCENT if index == self.selected_index else LINE, highlightthickness=1)
        card.edit_index = index
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        if title:
            label = tk.Label(card, text=title, bg=SURFACE, fg=accent, font=("Segoe UI", 14, "bold"), anchor="w", justify="left")
            label.pack(anchor="w", fill=tk.X, pady=(0, 8))
            bind_wrap(label, card)
            if index is not None:
                self.bind_to_component(label, index)
        if index is not None:
            for widget in (outer, card):
                widget.bind("<ButtonPress-1>", lambda event, i=index: self.begin_component_drag(i, event))
                widget.bind("<B1-Motion>", self.drag_component_motion)
                widget.bind("<ButtonRelease-1>", lambda event: self.complete_component_drag_at_pointer(event))
                widget.bind("<Double-Button-1>", lambda _event, i=index: self.edit_component(i))
                widget.bind("<Button-3>", lambda event, i=index: self.show_card_menu(i, event))
            if self.editing_index == index:
                self.render_edit_panel(card, self.components[index])
        return card

    def bind_to_component(self, widget, index):
        if index is None:
            return
        widget.bind("<ButtonPress-1>", lambda event, i=index: self.begin_component_drag(i, event))
        widget.bind("<B1-Motion>", self.drag_component_motion)
        widget.bind("<ButtonRelease-1>", lambda event: self.complete_component_drag_at_pointer(event))
        widget.bind("<Double-Button-1>", lambda _event, i=index: self.edit_component(i))
        widget.bind("<Button-3>", lambda event, i=index: self.show_card_menu(i, event))

    def select_component_no_rerender(self, index):
        self.selected_index = index
        self.editing_index = None

    def render_builder(self):
        self.builder_scroll.clear()
        self.card_positions = []
        self.page_title(self.builder_scroll.inner, "Lesson Canvas", self.concept.get("title", "Untitled"), "Double-click a card to edit it inline. Right-click cards for add, YAML, duplicate, delete, and move actions.")
        self.render_metadata_card()
        self.render_insert_control(0)
        if not self.components:
            card = self.card(self.builder_scroll.inner, "No Components", RED)
            self.text(card, "Choose a + button to add the first component.")
            return
        for index, component in enumerate(self.components):
            self.render_builder_card(index, component)
            self.render_insert_control(index + 1)

    def render_metadata_card(self):
        outer = tk.Frame(self.builder_scroll.inner, bg=APP_BG)
        outer.pack(fill=tk.X, padx=18, pady=(0, 8))
        tk.Frame(outer, bg=GREEN, width=5).pack(side=tk.LEFT, fill=tk.Y)
        card = tk.Frame(outer, bg=SURFACE, padx=16, pady=14, highlightbackground=LINE, highlightthickness=1)
        card.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(card, text="Lesson Details", bg=SURFACE, fg=GREEN, font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 8))

        grid = tk.Frame(card, bg=SURFACE)
        grid.pack(fill=tk.X)
        self.meta_widgets = {}
        fields = [("id", "Concept ID"), ("title", "Title"), ("category", "Category"), ("level", "Level"), ("languages", "Languages"), ("tags", "Tags")]
        for index, (key, label) in enumerate(fields):
            row = index // 2
            col = (index % 2) * 2
            tk.Label(grid, text=label, bg=SURFACE, fg=MUTED, font=("Segoe UI", 9, "bold")).grid(row=row, column=col, sticky="w", padx=(0, 6), pady=4)
            entry = tk.Entry(grid, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1)
            entry.grid(row=row, column=col + 1, sticky="ew", padx=(0, 16), pady=4)
            entry.insert(0, ", ".join(self.concept.get(key, [])) if key in {"languages", "tags"} else self.concept.get(key, ""))
            entry.bind("<FocusIn>", lambda _event: self.push_undo())
            entry.bind("<KeyRelease>", lambda _event: self.metadata_changed())
            self.meta_widgets[key] = entry
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(3, weight=1)

        tk.Label(card, text="Goal", bg=SURFACE, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(8, 2))
        self.goal_text = tk.Text(card, height=4, font=("Segoe UI", 10), wrap=tk.WORD, relief=tk.SOLID, borderwidth=1)
        self.goal_text.pack(fill=tk.X)
        self.goal_text.insert("1.0", self.concept.get("goal", ""))
        self.goal_text.bind("<FocusIn>", lambda _event: self.push_undo())
        self.goal_text.bind("<KeyRelease>", lambda _event: self.metadata_changed())

    def render_insert_control(self, insert_index):
        row = tk.Frame(self.builder_scroll.inner, bg=APP_BG)
        row.pack(fill=tk.X, padx=18, pady=2)

        line_left = tk.Frame(row, bg=LINE, height=1)
        line_left.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=12)

        button = tk.Button(
            row,
            text="+",
            bg=SURFACE,
            fg=ACCENT,
            activebackground="#dbeafe",
            activeforeground=ACCENT_DARK,
            relief=tk.SOLID,
            borderwidth=1,
            font=("Segoe UI", 11, "bold"),
            width=3,
            command=lambda index=insert_index: self.show_add_menu(index),
        )
        button.pack(side=tk.LEFT, padx=8)
        Tooltip(button, f"Add component at position {insert_index + 1}")

        line_right = tk.Frame(row, bg=LINE, height=1)
        line_right.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=12)

    def page_title(self, parent, eyebrow, title, body):
        frame = tk.Frame(parent, bg=APP_BG)
        frame.pack(fill=tk.X, padx=18, pady=(10, 14))
        tk.Label(frame, text=eyebrow.upper(), bg=APP_BG, fg=ACCENT, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(frame, text=title, bg=APP_BG, fg=INK, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        if body:
            label = tk.Label(frame, text=body, bg=APP_BG, fg=MUTED, font=("Segoe UI", 11), justify="left")
            label.pack(anchor="w", fill=tk.X, pady=(6, 0))
            bind_wrap(label, frame)

    def card(self, parent, title, accent=ACCENT):
        outer = tk.Frame(parent, bg=APP_BG)
        outer.pack(fill=tk.X, padx=18, pady=8)
        tk.Frame(outer, bg=accent, width=5).pack(side=tk.LEFT, fill=tk.Y)
        card = tk.Frame(outer, bg=SURFACE, padx=16, pady=14, highlightbackground=LINE, highlightthickness=1)
        card.pack(side=tk.LEFT, fill=tk.X, expand=True)
        label = tk.Label(card, text=title, bg=SURFACE, fg=accent, font=("Segoe UI", 14, "bold"), justify="left", anchor="w")
        label.pack(anchor="w", fill=tk.X, pady=(0, 8))
        bind_wrap(label, card)
        return card

    def text(self, parent, value, color=INK, mono=False):
        if not value:
            return
        label = tk.Label(
            parent,
            text=str(value).strip(),
            bg=parent.cget("bg"),
            fg=color,
            font=("Consolas", 10) if mono else ("Segoe UI", 10),
            justify="left",
            anchor="w",
        )
        label.pack(anchor="w", fill=tk.X, pady=2)
        bind_wrap(label, parent)
        self.bind_to_component(label, getattr(parent, "edit_index", None))

    def _code_box(self, parent, language, code, index=None):
        shell = tk.Frame(parent, bg=CODE_BG, padx=8, pady=6)
        shell.pack(fill=tk.X, pady=(6, 0))
        shell.edit_index = index
        header = tk.Frame(shell, bg=CODE_BG)
        header.pack(fill=tk.X)
        lang_label = tk.Label(
            header,
            text=language.upper(),
            bg=CODE_BG,
            fg=CODE_ACCENT,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        )
        lang_label.pack(side=tk.LEFT)
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

        box = tk.Text(
            shell,
            height=min(16, max(5, len(str(code).splitlines()) + 1)),
            bg=CODE_BG,
            fg=CODE_FG,
            insertbackground=CODE_FG,
            font=("Consolas", 10),
            wrap=tk.WORD,
            relief=tk.FLAT,
        )
        box.pack(fill=tk.X, expand=True, pady=(6, 0))
        box.insert("1.0", str(code).rstrip())
        box.config(state=tk.DISABLED)
        box.bind("<Button-3>", lambda event: self.show_code_menu(event, language, code))
        self.bind_to_component(shell, index)
        self.bind_to_component(lang_label, index)
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

    def render_study_component(self, parent, component):
        kind = component["kind"]
        data = component["data"]
        if kind == "explain":
            card = self.card(parent, data.get("title", "Explanation"), ACCENT)
            self.text(card, data.get("body", ""))
        elif kind == "language_lens":
            card = self.card(parent, data.get("title", "Language Lens"), GREEN)
            self.text(card, data.get("body", ""))
            for item in lines(data.get("default_instincts", "")):
                self.text(card, f"- {item}", MUTED)
        elif kind == "code_compare":
            card = self.card(parent, data.get("title", "Code Comparison"), AMBER)
            self.text(card, data.get("idea", ""), MUTED)
            for lang in self.concept.get("languages", []):
                if data.get(lang):
                    self.text(card, f"[{clean_title(lang)}]", ACCENT)
                    self.text(card, data.get(lang, ""), CODE_FG, mono=True)
        elif kind in {"compare_table", "revision_table"}:
            table = parse_table(data)
            card = self.card(parent, table.get("title", "Table"), PURPLE)
            self.render_table(card, table.get("columns", []), table.get("rows", []))
        elif kind == "image":
            card = self.card(parent, data.get("caption", "Image"), PURPLE)
            self.text(card, f"Image placeholder: {data.get('asset', '')}", MUTED)

    def render_table(self, parent, columns, rows):
        if not columns:
            return
        max_columns = 4
        for start in range(0, len(columns), max_columns):
            band_columns = columns[start:start + max_columns]
            band_rows = []
            for row in rows:
                band_rows.append([row[index] if index < len(row) else "" for index in range(start, start + len(band_columns))])
            if start:
                tk.Label(
                    parent,
                    text=f"More columns: {', '.join(str(item) for item in band_columns)}",
                    bg=parent.cget("bg"),
                    fg=MUTED,
                    font=("Segoe UI", 9, "bold"),
                    anchor="w",
                ).pack(anchor="w", fill=tk.X, pady=(10, 4))
            table = tk.Frame(parent, bg=LINE)
            table.edit_index = getattr(parent, "edit_index", None)
            table.pack(fill=tk.X, pady=(2, 8))
            for col, name in enumerate(band_columns):
                table.grid_columnconfigure(col, weight=1, uniform=f"table_{start}")
                self.table_cell(table, name, 0, col, True)
            for row_index, row in enumerate(band_rows, start=1):
                for col, value in enumerate(row):
                    self.table_cell(table, value, row_index, col, False)

    def table_cell(self, parent, value, row, col, header):
        label = tk.Label(
            parent,
            text=str(value),
            bg=INK if header else SURFACE,
            fg="white" if header else INK,
            font=("Segoe UI", 10, "bold") if header else ("Segoe UI", 10),
            padx=10,
            pady=8,
            justify="left",
            anchor="nw",
        )
        label.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
        label.bind("<Configure>", lambda event, item=label: item.configure(wraplength=max(120, event.width - 20)), add="+")
        self.bind_to_component(label, getattr(parent, "edit_index", None))

    def render_builder_card(self, index, component):
        selected = index == self.selected_index
        editing = index == self.editing_index
        accent = ACCENT if selected else LINE
        outer = tk.Frame(self.builder_scroll.inner, bg=APP_BG)
        outer.card_index = index
        outer.pack(fill=tk.X, padx=18, pady=8)
        self.root.after(10, lambda frame=outer, i=index: self.record_card_position(frame, i))
        tk.Frame(outer, bg=accent, width=5).pack(side=tk.LEFT, fill=tk.Y)
        card = tk.Frame(outer, bg=SURFACE, padx=16, pady=14, highlightbackground=LINE, highlightthickness=1)
        card.pack(side=tk.LEFT, fill=tk.X, expand=True)

        header = tk.Frame(card, bg=SURFACE)
        header.pack(fill=tk.X)
        icon = block_icon(component["kind"])
        handle = tk.Label(header, text="DRAG", bg="#f1f5f9", fg=MUTED, font=("Segoe UI", 9, "bold"), padx=6, pady=3)
        handle.pack(side=tk.LEFT)
        handle.configure(cursor="fleur")
        handle.bind("<ButtonPress-1>", lambda event, i=index: self.begin_component_drag(i, event))
        handle.bind("<B1-Motion>", self.drag_component_motion)
        handle.bind("<ButtonRelease-1>", lambda event: self.complete_component_drag_at_pointer(event))
        handle.bind("<Button-3>", lambda event, i=index: self.show_card_menu(i, event))
        Tooltip(handle, "Drag to reorder. Alt+Up and Alt+Down also move the selected card.")

        icon_label = tk.Label(header, text=icon, bg="#e0e7ff", fg=ACCENT, font=("Segoe UI", 10, "bold"), padx=8, pady=3)
        icon_label.pack(side=tk.LEFT, padx=(6, 0))
        title_label = tk.Label(header, text=f"{index + 1}. {BLOCKS[component['kind']]['title']}", bg=SURFACE, fg=ACCENT if selected else INK, font=("Segoe UI", 13, "bold"))
        title_label.pack(side=tk.LEFT, padx=8)
        section_label = tk.Label(header, text=component["section"], bg=SURFACE, fg=MUTED, font=("Segoe UI", 9, "bold"))
        section_label.pack(side=tk.RIGHT)

        summary = tk.Label(
            card,
            text=self.component_summary(component),
            bg=SURFACE,
            fg=MUTED,
            font=("Segoe UI", 10),
            justify="left",
            anchor="w",
        )
        summary.pack(anchor="w", fill=tk.X, pady=2)
        bind_wrap(summary, card)

        for widget in (outer, card, header, icon_label, title_label, section_label, summary):
            widget.bind("<ButtonPress-1>", lambda event, i=index: self.begin_component_drag(i, event))
            widget.bind("<B1-Motion>", self.drag_component_motion)
            widget.bind("<ButtonRelease-1>", lambda event: self.complete_component_drag_at_pointer(event))
            widget.bind("<Double-Button-1>", lambda _event, i=index: self.edit_component(i))
            widget.bind("<Button-3>", lambda event, i=index: self.show_card_menu(i, event))

        if editing:
            self.render_edit_panel(card, component)

    def record_card_position(self, frame, index):
        top = frame.winfo_rooty()
        bottom = top + frame.winfo_height()
        midpoint = top + frame.winfo_height() / 2
        self.card_positions.append((index, top, midpoint, bottom))

    def render_edit_panel(self, parent, component):
        panel = tk.Frame(parent, bg="#f8fafc", padx=12, pady=10, highlightbackground=LINE, highlightthickness=1)
        panel.pack(fill=tk.X, pady=(12, 0))
        tk.Label(panel, text="Editing", bg="#f8fafc", fg=INK, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.field_widgets = {}
        for key, value in component["data"].items():
            tk.Label(panel, text=clean_title(key), bg="#f8fafc", fg=MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 2))
            field_type = FIELD_TYPES.get(key, "short")
            if field_type == "short":
                widget = tk.Entry(panel, font=("Segoe UI", 10))
                widget.insert(0, str(value))
                widget.pack(fill=tk.X)
            else:
                widget = tk.Text(panel, height=8 if field_type == "code" else 5, font=("Consolas", 10) if field_type == "code" else ("Segoe UI", 10), wrap=tk.NONE if field_type == "code" else tk.WORD)
                widget.insert("1.0", str(value))
                widget.pack(fill=tk.X)
            widget.bind("<FocusIn>", lambda _event: self.push_undo())
            widget.bind("<KeyRelease>", lambda _event, field=key: self.field_changed(field))
            self.field_widgets[key] = widget
        ttk.Button(panel, text="Done", command=self.stop_editing, style="Primary.TButton").pack(anchor="e", pady=(10, 0))

    def field_changed(self, field):
        if self.editing_index is None:
            return
        widget = self.field_widgets[field]
        value = widget.get("1.0", tk.END).rstrip() if isinstance(widget, tk.Text) else widget.get()
        self.components[self.editing_index]["data"][field] = value

    def component_summary(self, component):
        data = component["data"]
        if data.get("title"):
            return data.get("title")
        if component["kind"] == "transition_path":
            return f"{data.get('source', '')} -> {data.get('target', '')}"
        if component["kind"] == "flashcard":
            return data.get("question", "")
        return BLOCKS[component["kind"]]["hint"]

    def duplicate_at(self, index):
        self.selected_index = index
        return self.duplicate_selected()

    def delete_at(self, index):
        self.selected_index = index
        return self.delete_selected()

    def show_card_menu(self, index, event):
        self.selected_index = index
        menu = tk.Menu(self.root, tearoff=False)
        menu.add_command(label="Edit card inline", command=lambda: self.edit_component(index))
        menu.add_command(label="Edit card YAML", command=lambda: self.edit_component_yaml(index))
        menu.add_command(label="Unselect card", command=self.stop_editing)
        menu.add_separator()
        menu.add_command(label="Add card before", command=lambda: self.show_add_menu(index, event))
        menu.add_command(label="Add card after", command=lambda: self.show_add_menu(index + 1, event))
        menu.add_separator()
        menu.add_command(label="Move up", command=lambda: self.move_selected(-1))
        menu.add_command(label="Move down", command=lambda: self.move_selected(1))
        menu.add_command(label="Duplicate", command=lambda: self.duplicate_at(index))
        menu.add_command(label="Delete", command=lambda: self.delete_at(index))
        menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def show_page_menu(self, event):
        menu = tk.Menu(self.root, tearoff=False)
        if is_booklet(self.concept):
            menu.add_command(label="Edit booklet details", command=self.edit_lesson_details)
            menu.add_command(label="Edit booklet YAML", command=lambda: self.edit_yaml_node("Booklet YAML", self.concept, self.render))
            menu.add_command(label="Add chapter", command=self.add_booklet_chapter)
        else:
            menu.add_command(label="Edit lesson details", command=self.edit_lesson_details)
            menu.add_command(label="Add card at end", command=lambda: self.show_add_menu(len(self.components), event))
        menu.add_command(label="Save", command=self.save_yaml)
        menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def show_chapter_menu(self, chapter_index, event):
        menu = tk.Menu(self.root, tearoff=False)
        menu.add_command(label="Edit chapter YAML", command=lambda: self.edit_booklet_chapter(chapter_index))
        menu.add_command(label="Add section", command=lambda: self.add_booklet_section(chapter_index))
        menu.add_command(label="Add chapter after", command=lambda: self.add_booklet_chapter(chapter_index + 1))
        menu.add_separator()
        menu.add_command(label="Move chapter up", command=lambda: self.move_booklet_item(self.concept["chapters"], chapter_index, -1))
        menu.add_command(label="Move chapter down", command=lambda: self.move_booklet_item(self.concept["chapters"], chapter_index, 1))
        menu.add_command(label="Delete chapter", command=lambda: self.delete_booklet_item(self.concept["chapters"], chapter_index, "chapter"))
        menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def show_section_menu(self, chapter_index, section_index, event):
        sections = self.concept["chapters"][chapter_index].setdefault("sections", [])
        menu = tk.Menu(self.root, tearoff=False)
        menu.add_command(label="Edit section YAML", command=lambda: self.edit_booklet_section(chapter_index, section_index))
        menu.add_command(label="Add lesson", command=lambda: self.add_booklet_lesson(chapter_index, section_index))
        menu.add_command(label="Add section after", command=lambda: self.add_booklet_section(chapter_index, section_index + 1))
        menu.add_separator()
        menu.add_command(label="Move section up", command=lambda: self.move_booklet_item(sections, section_index, -1))
        menu.add_command(label="Move section down", command=lambda: self.move_booklet_item(sections, section_index, 1))
        menu.add_command(label="Delete section", command=lambda: self.delete_booklet_item(sections, section_index, "section"))
        menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def show_lesson_link_menu(self, chapter_index, section_index, lesson_index, event):
        lesson = self.concept["chapters"][chapter_index]["sections"][section_index]["lessons"][lesson_index]
        lessons = self.concept["chapters"][chapter_index]["sections"][section_index]["lessons"]
        menu = tk.Menu(self.root, tearoff=False)
        menu.add_command(label="Open lesson", command=lambda: self.open_booklet_lesson(self.resolve_lesson_path(lesson.get("file") or lesson.get("path", ""))))
        menu.add_command(label="Edit lesson link YAML", command=lambda: self.edit_booklet_lesson(chapter_index, section_index, lesson_index))
        menu.add_command(label="Add lesson after", command=lambda: self.add_booklet_lesson(chapter_index, section_index, lesson_index + 1))
        menu.add_separator()
        menu.add_command(label="Move lesson up", command=lambda: self.move_booklet_item(lessons, lesson_index, -1))
        menu.add_command(label="Move lesson down", command=lambda: self.move_booklet_item(lessons, lesson_index, 1))
        menu.add_command(label="Delete lesson link", command=lambda: self.delete_booklet_item(lessons, lesson_index, "lesson link"))
        menu.tk_popup(event.x_root, event.y_root)
        return "break"

    def edit_lesson_details(self):
        window = tk.Toplevel(self.root)
        window.title("Edit Booklet Details" if is_booklet(self.concept) else "Edit Lesson Details")
        window.geometry("760x420")
        window.configure(bg=APP_BG)
        shell = tk.Frame(window, bg=APP_BG, padx=16, pady=16)
        shell.pack(fill=tk.BOTH, expand=True)
        widgets = {}
        fields = [("id", "Concept ID"), ("title", "Title"), ("category", "Category"), ("level", "Level"), ("languages", "Languages"), ("tags", "Tags")]
        if is_booklet(self.concept):
            fields = [("id", "Booklet ID"), ("title", "Title"), ("type", "Type"), ("category", "Category"), ("languages", "Languages"), ("tags", "Tags")]
        for index, (key, label) in enumerate(fields):
            row = index // 2
            col = (index % 2) * 2
            tk.Label(shell, text=label, bg=APP_BG, fg=MUTED, font=("Segoe UI", 9, "bold")).grid(row=row, column=col, sticky="w", padx=(0, 6), pady=5)
            entry = tk.Entry(shell, font=("Segoe UI", 10))
            entry.grid(row=row, column=col + 1, sticky="ew", padx=(0, 16), pady=5)
            entry.insert(0, ", ".join(self.concept.get(key, [])) if key in {"languages", "tags"} else self.concept.get(key, ""))
            widgets[key] = entry
        tk.Label(shell, text="Goal", bg=APP_BG, fg=MUTED, font=("Segoe UI", 9, "bold")).grid(row=3, column=0, sticky="nw", padx=(0, 6), pady=(12, 5))
        goal = tk.Text(shell, height=7, font=("Segoe UI", 10), wrap=tk.WORD)
        goal.grid(row=3, column=1, columnspan=3, sticky="nsew", padx=(0, 16), pady=(12, 5))
        goal.insert("1.0", self.concept.get("goal", ""))
        shell.grid_columnconfigure(1, weight=1)
        shell.grid_columnconfigure(3, weight=1)
        shell.grid_rowconfigure(3, weight=1)

        def apply_details():
            self.push_undo()
            self.concept["id"] = clean_id(widgets["id"].get())
            self.concept["title"] = widgets["title"].get().strip() or "Untitled"
            if "type" in widgets:
                self.concept["type"] = clean_id(widgets["type"].get()) or "booklet"
            self.concept["category"] = clean_id(widgets["category"].get())
            if "level" in widgets:
                self.concept["level"] = clean_id(widgets["level"].get())
            self.concept["languages"] = [clean_id(item) for item in widgets["languages"].get().split(",") if item.strip()]
            self.concept["tags"] = [clean_id(item) for item in widgets["tags"].get().split(",") if item.strip()]
            self.concept["goal"] = goal.get("1.0", tk.END).strip()
            self.title_label.config(text=self.concept.get("title", "Untitled"))
            self.render()
            window.destroy()

        actions = tk.Frame(shell, bg=APP_BG)
        actions.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(12, 0))
        ttk.Button(actions, text="Apply", command=apply_details, style="Primary.TButton").pack(side=tk.RIGHT)
        ttk.Button(actions, text="Cancel", command=window.destroy).pack(side=tk.RIGHT, padx=8)

    def edit_yaml_node(self, title, node, after_apply=None):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("820x620")
        window.configure(bg=APP_BG)
        tk.Label(window, text=title, bg=APP_BG, fg=INK, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=14, pady=(14, 6))
        text = tk.Text(window, font=("Consolas", 10), wrap=tk.NONE, bg=CODE_BG, fg=CODE_FG, insertbackground=CODE_FG)
        text.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 10))
        text.insert("1.0", yaml.safe_dump(node, sort_keys=False, allow_unicode=True))
        buttons = tk.Frame(window, bg=APP_BG)
        buttons.pack(fill=tk.X, padx=14, pady=(0, 14))

        def apply_node():
            try:
                parsed = yaml.safe_load(text.get("1.0", tk.END)) or {}
                if not isinstance(parsed, dict):
                    raise ValueError("This editor expects a YAML mapping.")
                self.push_undo()
                node.clear()
                node.update(parsed)
                if after_apply:
                    after_apply()
                else:
                    self.render()
                window.destroy()
            except Exception as error:
                messagebox.showerror("Invalid YAML", str(error), parent=window)

        ttk.Button(buttons, text="Apply", command=apply_node, style="Primary.TButton").pack(side=tk.RIGHT)
        ttk.Button(buttons, text="Cancel", command=window.destroy).pack(side=tk.RIGHT, padx=8)

    def edit_booklet_chapter(self, chapter_index):
        self.edit_yaml_node("Chapter YAML", self.concept["chapters"][chapter_index])

    def edit_booklet_section(self, chapter_index, section_index):
        section = self.concept["chapters"][chapter_index]["sections"][section_index]
        self.edit_yaml_node("Section YAML", section)

    def edit_booklet_lesson(self, chapter_index, section_index, lesson_index):
        lesson = self.concept["chapters"][chapter_index]["sections"][section_index]["lessons"][lesson_index]
        self.edit_yaml_node("Lesson Link YAML", lesson)

    def add_booklet_chapter(self, insert_index=None):
        self.push_undo()
        chapter = {
            "id": "new_chapter",
            "title": "New Chapter",
            "description": "Describe this chapter.",
            "sections": [],
        }
        chapters = self.concept.setdefault("chapters", [])
        if insert_index is None:
            insert_index = len(chapters)
        chapters.insert(max(0, min(insert_index, len(chapters))), chapter)
        self.render()
        return "break"

    def add_booklet_section(self, chapter_index, insert_index=None):
        self.push_undo()
        sections = self.concept["chapters"][chapter_index].setdefault("sections", [])
        section = {"title": "New Section", "description": "Describe this section.", "lessons": []}
        if insert_index is None:
            insert_index = len(sections)
        sections.insert(max(0, min(insert_index, len(sections))), section)
        self.render()
        return "break"

    def add_booklet_lesson(self, chapter_index, section_index, insert_index=None):
        self.push_undo()
        lessons = self.concept["chapters"][chapter_index]["sections"][section_index].setdefault("lessons", [])
        lesson = {
            "title": "New Lesson",
            "file": "knowledge/dsa/new_lesson.yaml",
            "description": "Describe what this lesson covers.",
            "status": "planned",
        }
        if insert_index is None:
            insert_index = len(lessons)
        lessons.insert(max(0, min(insert_index, len(lessons))), lesson)
        self.render()
        return "break"

    def move_booklet_item(self, items, index, direction):
        target = index + direction
        if target < 0 or target >= len(items):
            return "break"
        self.push_undo()
        items[index], items[target] = items[target], items[index]
        self.render()
        return "break"

    def delete_booklet_item(self, items, index, label):
        if index < 0 or index >= len(items):
            return "break"
        if not messagebox.askyesno("Delete", f"Delete this {label}?"):
            return "break"
        self.push_undo()
        del items[index]
        self.render()
        return "break"

    def resolve_lesson_path(self, file_value):
        path = Path(str(file_value))
        if path.is_absolute():
            return path
        candidates = []
        if self.current_file:
            candidates.append(self.current_file.parent / path)
        if self.current_folder:
            candidates.append(Path(self.current_folder) / path)
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
        self.select_open_file_in_sidebar(path)
        return "break"

    def select_open_file_in_sidebar(self, path):
        if not hasattr(self, "file_tree"):
            return
        try:
            target = Path(path).resolve()
        except Exception:
            return
        for item_path, item_id in self.file_tree_items.items():
            try:
                if item_path.resolve() == target:
                    self.file_tree.selection_set(item_id)
                    self.file_tree.focus(item_id)
                    self.file_tree.see(item_id)
                    return
            except Exception:
                continue

    def edit_selected_yaml(self):
        if self.selected_index is not None:
            self.edit_component_yaml(self.selected_index)
        return "break"

    def edit_component_yaml(self, index):
        if index < 0 or index >= len(self.components):
            return "break"
        component = self.components[index]
        window = tk.Toplevel(self.root)
        window.title(f"Edit YAML - {BLOCKS[component['kind']]['title']}")
        window.geometry("760x560")
        window.configure(bg=APP_BG)

        tk.Label(window, text="Card YAML", bg=APP_BG, fg=INK, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=14, pady=(14, 4))
        tk.Label(window, text="Edit this card as a YAML mapping. Keep one top-level component key.", bg=APP_BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=14, pady=(0, 8))

        text = tk.Text(window, font=("Consolas", 10), wrap=tk.NONE, bg=CODE_BG, fg=CODE_FG, insertbackground="white")
        text.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 10))
        text.insert("1.0", yaml.safe_dump({component["kind"]: component["data"]}, sort_keys=False, allow_unicode=True))

        buttons = tk.Frame(window, bg=APP_BG)
        buttons.pack(fill=tk.X, padx=14, pady=(0, 14))

        def apply_yaml():
            try:
                parsed = yaml.safe_load(text.get("1.0", tk.END)) or {}
                if not isinstance(parsed, dict) or len(parsed) != 1:
                    raise ValueError("Use exactly one top-level component key.")
                kind, data = next(iter(parsed.items()))
                if kind not in BLOCKS:
                    raise ValueError(f"Unsupported component type: {kind}")
                if not isinstance(data, dict):
                    raise ValueError("Component value must be a mapping.")
                self.push_undo()
                self.components[index] = {"kind": kind, "section": BLOCKS[kind]["section"], "data": data}
                self.selected_index = index
                self.editing_index = None
                self.render_all()
                window.destroy()
            except Exception as error:
                messagebox.showerror("Invalid YAML", str(error), parent=window)

        ttk.Button(buttons, text="Apply", command=apply_yaml, style="Primary.TButton").pack(side=tk.RIGHT)
        ttk.Button(buttons, text="Cancel", command=window.destroy).pack(side=tk.RIGHT, padx=8)
        return "break"

    def move_selected(self, direction):
        if self.selected_index is None:
            return "break"
        target = self.selected_index + direction
        if target < 0 or target >= len(self.components):
            return "break"
        self.push_undo()
        self.components[self.selected_index], self.components[target] = self.components[target], self.components[self.selected_index]
        self.selected_index = target
        self.editing_index = None
        self.render_all()
        return "break"

    def build_concept(self):
        if is_booklet(self.concept):
            return copy.deepcopy(self.concept)

        concept = copy.deepcopy(self.concept)
        concept["lesson"] = []
        concept["examples"] = []
        concept["transitions"] = {}
        revision_points = []
        revision_table = None
        flashcards = []
        for component in self.components:
            kind = component["kind"]
            data = component["data"]
            section = component["section"]
            if section == "lesson":
                if kind == "compare_table":
                    concept["lesson"].append({kind: parse_table(data)})
                elif kind == "language_lens":
                    concept["lesson"].append({kind: {
                        "language": clean_id(data.get("language", "")),
                        "title": data.get("title", ""),
                        "body": data.get("body", ""),
                        "default_instincts": lines(data.get("default_instincts", "")),
                        "avoid": lines(data.get("avoid", "")),
                    }})
                else:
                    concept["lesson"].append({kind: copy.deepcopy(data)})
            elif section == "examples":
                concept["examples"].append({kind: copy.deepcopy(data)})
            elif kind == "transition_path":
                key, value = parse_transition(data)
                concept["transitions"][key] = value
            elif kind == "revision_summary":
                revision_points.extend(lines(data.get("points", "")))
            elif kind == "revision_table":
                revision_table = parse_table(data)
            elif kind == "flashcard":
                flashcards.append({"question": data.get("question", ""), "answer": data.get("answer", "")})
        concept["revision"] = {
            "quick_summary": revision_points,
            "cheat_table": revision_table or {"title": "Revision map", "columns": ["Need", "Reminder"], "rows": []},
            "flashcards": flashcards,
        }
        return concept

    def concept_to_components(self, concept):
        components = []
        for block in concept.get("lesson", []):
            kind, data = block_name(block)
            if kind not in BLOCKS:
                continue
            if kind == "compare_table":
                data = table_to_editor(data)
            elif kind == "language_lens":
                data = {
                    "language": data.get("language", ""),
                    "title": data.get("title", ""),
                    "body": data.get("body", ""),
                    "default_instincts": "\n".join(data.get("default_instincts", [])),
                    "avoid": "\n".join(data.get("avoid", [])),
                }
            components.append({"kind": kind, "section": BLOCKS[kind]["section"], "data": copy.deepcopy(data)})
        for block in concept.get("examples", []):
            kind, data = block_name(block)
            if kind in BLOCKS:
                merged = copy.deepcopy(BLOCKS[kind]["data"])
                if isinstance(data, dict):
                    merged.update(data)
                components.append({"kind": kind, "section": "examples", "data": merged})
        for key, transition in concept.get("transitions", {}).items():
            source, _, target = key.partition("_to_")
            components.append({"kind": "transition_path", "section": "transitions", "data": {
                "source": source,
                "target": target,
                "title": transition.get("title", ""),
                "mindset_shift": "\n".join(transition.get("mindset_shift", [])),
                "habit_swaps": "\n".join(" | ".join(f"{k}: {v}" for k, v in item.items()) for item in transition.get("habit_swaps", [])),
                "false_friends": "\n".join(f"{item.get('term', '')} | {item.get('warning', '')}" for item in transition.get("false_friends", [])),
            }})
        revision = concept.get("revision", {})
        if revision.get("quick_summary"):
            components.append({"kind": "revision_summary", "section": "revision", "data": {"points": "\n".join(revision["quick_summary"])}})
        if revision.get("cheat_table"):
            components.append({"kind": "revision_table", "section": "revision", "data": table_to_editor(revision["cheat_table"])})
        for item in revision.get("flashcards", []):
            components.append({"kind": "flashcard", "section": "revision", "data": {"question": item.get("question", ""), "answer": item.get("answer", "")}})
        return components

    def new_lesson(self):
        self.push_undo()
        self.current_file = None
        self.load_concept(self.default_concept(), push_undo=False)
        return "break"

    def open_folder(self):
        path = filedialog.askdirectory(initialdir=str(self.current_folder or DEFAULT_OUTPUT_DIR))
        if not path:
            return "break"
        self.current_folder = Path(path)
        self.populate_file_list()
        return "break"

    def populate_file_list(self):
        if not hasattr(self, "file_tree"):
            return
        self.file_tree.delete(*self.file_tree.get_children())
        self.file_tree_items = {}
        folder = Path(self.current_folder or DEFAULT_OUTPUT_DIR)
        if not folder.exists():
            self.yaml_files = []
            return
        self.yaml_files = sorted([path for path in folder.rglob("*") if path.is_file() and path.suffix.lower() in {".yaml", ".yml"}], key=lambda item: str(item.relative_to(folder)).lower())
        folder_nodes = {}
        for path in self.yaml_files:
            relative = path.relative_to(folder)
            parent = ""
            for part in relative.parts[:-1]:
                key = (parent, part)
                if key not in folder_nodes:
                    folder_nodes[key] = self.file_tree.insert(parent, tk.END, text=f"📁 {part}", open=True)
                parent = folder_nodes[key]
            item_id = self.file_tree.insert(parent, tk.END, text=f"📄 {relative.name}", values=(str(path),))
            self.file_tree_items[path] = item_id
        if self.current_file in self.yaml_files:
            self.select_open_file_in_sidebar(self.current_file)

    def on_file_select(self, _event=None):
        return self.open_selected_tree_item()

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
        return self.select_file_at(current + offset)

    def load_file(self, path, new_tab=False, record_history=True):
        path = Path(path)
        for index, tab in enumerate(self.tabs):
            if tab["path"] == path and (new_tab or path != self.current_file):
                return self.switch_tab(index, record_history=record_history)
        try:
            concept = load_yaml(path)
            if record_history and self.current_file and self.current_file != path:
                self.nav_history.append(self.current_file)
            self.save_active_tab_state()
            self.current_file = path
            self.adopt_file_folder(path)
            self.open_or_update_tab(path, concept, new_tab=new_tab)
            self.load_concept(concept, push_undo=False)
            self.update_file_title()
            self.render_tabs()
            self.restore_active_scroll()
            self.select_open_file_in_sidebar(path)
        except Exception as error:
            messagebox.showerror("Open Failed", str(error))
        return "break"

    def reload_current_file(self):
        if self.current_file:
            self.load_file(self.current_file, record_history=False)
        return "break"

    def open_yaml(self):
        path = filedialog.askopenfilename(initialdir=str(self.current_folder or DEFAULT_OUTPUT_DIR), filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")])
        if not path:
            return "break"
        self.load_file(Path(path), new_tab=True)
        self.populate_file_list()
        return "break"

    def save_yaml(self):
        if self.current_file:
            self.write_yaml(self.current_file)
        else:
            self.save_yaml_as()
        return "break"

    def save_yaml_as(self):
        concept = self.build_concept()
        path = filedialog.asksaveasfilename(
            initialdir=str(self.current_folder or DEFAULT_OUTPUT_DIR),
            initialfile=f"{concept.get('id', 'lesson')}.yaml",
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")],
        )
        if path:
            self.current_file = Path(path)
            self.current_folder = self.current_file.parent
            self.write_yaml(self.current_file)
            self.populate_file_list()
            self.open_or_update_tab(self.current_file, self.current_concept_snapshot(), new_tab=True)
            self.render_tabs()
        return "break"

    def write_yaml(self, path):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            concept = self.current_concept_snapshot()
            path.write_text(yaml.safe_dump(concept, sort_keys=False, allow_unicode=True), encoding="utf-8")
            if self.current_file and Path(path) == self.current_file:
                self.open_or_update_tab(Path(path), concept, new_tab=self.active_tab is None)
                self.render_tabs()
            messagebox.showinfo("Saved", f"Saved lesson:\n{path}")
        except Exception as error:
            messagebox.showerror("Save Failed", str(error))


def main():
    root = tk.Tk()
    LessonBuilderVis2(root)
    root.mainloop()


if __name__ == "__main__":
    main()
