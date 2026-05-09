import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    import yaml
except ModuleNotFoundError:
    yaml = None


APP_BG = "#f3efe7"
SURFACE = "#fffaf0"
INK = "#1f2933"
MUTED = "#667085"
LINE = "#d8cfc0"
ACCENT = "#256f7c"
GREEN = "#2f855a"
AMBER = "#c47f17"
RED = "#b42318"
CAPTION_BG = "#fff4d8"
CAPTION_LINE = "#e7c98d"

DEFAULT_SAMPLE = Path(__file__).resolve().parents[2] / "knowledge" / "dsa" / "dsa_animation_booklet.yaml"


def load_yaml(path):
    text = Path(path).read_text(encoding="utf-8")
    data = yaml.safe_load(text) if yaml else simple_yaml_load(text)
    return data if isinstance(data, dict) else {}


def simple_yaml_load(text):
    """Small fallback parser for the animator's simple YAML subset."""
    lines = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        lines.append((indent, raw.strip()))

    def parse_block(index, indent):
        container = [] if index < len(lines) and lines[index][1].startswith("- ") else {}
        while index < len(lines):
            current_indent, content = lines[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                break
            if isinstance(container, list):
                if not content.startswith("- "):
                    break
                item_text = content[2:].strip()
                index += 1
                if not item_text:
                    item, index = parse_block(index, indent + 2)
                elif ":" in item_text:
                    key, value = split_key_value(item_text)
                    item = {key: parse_scalar(value)} if value else {key: None}
                    if index < len(lines) and lines[index][0] > indent:
                        nested, index = parse_block(index, lines[index][0])
                        if value:
                            if isinstance(nested, dict):
                                item.update(nested)
                        else:
                            item[key] = nested
                else:
                    item = parse_scalar(item_text)
                container.append(item)
            else:
                if content.startswith("- "):
                    break
                key, value = split_key_value(content)
                index += 1
                if value:
                    container[key] = parse_scalar(value)
                elif index < len(lines) and lines[index][0] > indent:
                    container[key], index = parse_block(index, lines[index][0])
                else:
                    container[key] = None
        return container, index

    parsed, _ = parse_block(0, lines[0][0] if lines else 0)
    return parsed


def split_key_value(text):
    key, value = text.split(":", 1)
    return key.strip(), value.strip()


def parse_scalar(value):
    value = value.strip()
    if not value:
        return None
    if value[0:1] in {"'", '"'} and value[-1:] == value[0]:
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inside = value[1:-1].strip()
        if not inside:
            return []
        return [parse_scalar(item.strip()) for item in inside.split(",")]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


class AnimatorRenderer:
    def __init__(self, root, path=None):
        self.root = root
        self.root.title("AnyLanguageExpressaic Animator Prototype")
        self.root.geometry("1180x760")
        self.root.minsize(980, 620)
        self.root.configure(bg=APP_BG)

        self.path = Path(path) if path else DEFAULT_SAMPLE
        self.data = {}
        self.animations = []
        self.playlist = []
        self.current_animation = None
        self.current_animation_index = 0
        self.play_all_enabled = False
        self.objects = {}
        self.object_defs = {}
        self.steps = []
        self.current_step = -1
        self.playing = False
        self.running_step = False
        self.animation_jobs = []
        self.note_text = tk.StringVar(value="")
        self.note_back = None
        self.note_item = None

        self.build_layout()
        self.bind_shortcuts()
        self.load_file(self.path)

    def build_layout(self):
        header = tk.Frame(self.root, bg=INK)
        header.pack(fill=tk.X)
        self.title_label = tk.Label(header, text="Animator Prototype", bg=INK, fg="white", font=("Segoe UI", 18, "bold"), anchor="w")
        self.title_label.pack(side=tk.LEFT, padx=16, pady=12)
        ttk.Button(header, text="Open YAML", command=self.open_yaml).pack(side=tk.RIGHT, padx=16, pady=12)

        stage = tk.Frame(self.root, bg=APP_BG)
        stage.pack(fill=tk.BOTH, expand=True, padx=14, pady=(14, 8))

        self.canvas = tk.Canvas(stage, bg=SURFACE, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda event: self.position_canvas_note())

        self.chapter_bar = tk.Frame(self.root, bg=APP_BG)
        self.chapter_bar.pack(fill=tk.X, padx=14, pady=(0, 8))
        self.chapter_buttons = []

        controls = tk.Frame(self.root, bg=APP_BG)
        controls.pack(fill=tk.X, padx=14, pady=(0, 14))
        self.reset_button = ttk.Button(controls, text="Reset", command=self.reset)
        self.reset_button.pack(side=tk.LEFT)
        self.previous_button = ttk.Button(controls, text="Previous", command=self.previous_step)
        self.previous_button.pack(side=tk.LEFT, padx=(8, 0))
        self.next_button = ttk.Button(controls, text="Next", command=self.next_step)
        self.next_button.pack(side=tk.LEFT, padx=(8, 0))
        self.play_button = ttk.Button(controls, text="Play", command=self.toggle_play)
        self.play_button.pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(controls, text="Replay", command=self.replay).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(controls, text="Play All", command=self.play_all).pack(side=tk.LEFT, padx=(8, 0))
        self.status = tk.Label(controls, text="", bg=APP_BG, fg=MUTED, font=("Segoe UI", 10), anchor="w")
        self.status.pack(side=tk.LEFT, padx=14)

    def bind_shortcuts(self):
        self.root.bind("<Left>", self.handle_previous_shortcut)
        self.root.bind("<Right>", self.handle_next_shortcut)
        self.root.bind("<space>", self.handle_pause_shortcut)

    def handle_previous_shortcut(self, event=None):
        del event
        self.previous_step_or_chapter()
        return "break"

    def handle_next_shortcut(self, event=None):
        del event
        self.next_step_or_chapter()
        return "break"

    def handle_pause_shortcut(self, event=None):
        del event
        self.pause_animation()
        return "break"

    def open_yaml(self):
        self.playing = False
        self.running_step = False
        self.stop_jobs()
        path = filedialog.askopenfilename(
            initialdir=str(self.path.parent if self.path else DEFAULT_SAMPLE.parent),
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")],
        )
        if path:
            self.load_file(Path(path))

    def load_file(self, path):
        try:
            self.path = Path(path)
            self.data = load_yaml(path)
            self.object_defs = {}
            self.configure_loaded_data()
        except Exception as error:
            messagebox.showerror("Could not open animation", str(error))

    def configure_loaded_data(self):
        if self.data.get("type") == "animation_booklet" or isinstance(self.data.get("animations"), list):
            self.animations = self.data.get("animations", [])
            self.playlist = self.data.get("playlist") or [item.get("id") for item in self.animations if item.get("id")]
            self.current_animation_index = 0
            self.render_chapters()
            self.select_animation(0)
            return

        self.animations = []
        self.playlist = []
        self.current_animation = self.data
        self.current_animation_index = 0
        self.render_chapters()
        self.title_label.config(text=self.data.get("title", "Animator Prototype"))
        self.steps = self.data.get("steps") or self.data.get("timeline") or []
        self.reset()

    def render_chapters(self):
        for child in self.chapter_bar.winfo_children():
            child.destroy()
        self.chapter_buttons = []

        if not self.animations:
            tk.Label(self.chapter_bar, text="Single animation", bg=APP_BG, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w")
            return

        button_row = tk.Frame(self.chapter_bar, bg=APP_BG)
        button_row.pack(fill=tk.X)
        tk.Label(button_row, text="Chapters", bg=APP_BG, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 8))
        for index, animation in enumerate(self.animations):
            button = tk.Button(
                button_row,
                text=animation.get("title", animation.get("id", f"Chapter {index + 1}")),
                command=lambda i=index: self.select_animation(i),
                bg=ACCENT if index == self.current_animation_index else SURFACE,
                fg="white" if index == self.current_animation_index else INK,
                activebackground="#dbeafe",
                activeforeground=INK,
                relief=tk.SOLID,
                borderwidth=1,
                padx=10,
                pady=4,
                cursor="hand2",
                font=("Segoe UI", 9, "bold" if index == self.current_animation_index else "normal"),
            )
            button.pack(side=tk.LEFT, padx=(0, 4))
            self.chapter_buttons.append(button)

    def select_animation(self, index, keep_play_all=False):
        if not self.animations:
            return
        self.stop_jobs()
        resume_playing = self.playing if keep_play_all else False
        self.playing = False
        self.running_step = False
        self.play_all_enabled = self.play_all_enabled if keep_play_all else False
        self.current_animation_index = max(0, min(index, len(self.animations) - 1))
        self.current_animation = self.animations[self.current_animation_index]
        self.steps = self.current_animation.get("steps") or self.current_animation.get("timeline") or []
        self.title_label.config(text=f"{self.data.get('title', 'Animation Booklet')} - {self.current_animation.get('title', '')}")
        self.render_chapters()
        self.reset()
        if keep_play_all:
            self.playing = resume_playing
            self.play_all_enabled = True
            self.update_status()

    def reset(self):
        self.stop_jobs()
        self.playing = False
        self.running_step = False
        self.current_step = -1
        self.note_text.set("")
        self.canvas.delete("all")
        self.objects = {}
        source = self.current_animation or self.data
        scene = source.get("scene", source)
        for spec in scene.get("objects", []):
            self.create_object(spec)
        self.create_canvas_note()
        self.update_status()

    def replay(self):
        self.reset()
        self.playing = True
        self.update_status()
        self.play_next()

    def play_all(self):
        if self.animations:
            self.select_animation(0)
        self.play_all_enabled = True
        self.playing = True
        self.update_status()
        self.play_next()

    def create_object(self, spec):
        kind = spec.get("type", "box")
        if kind == "array":
            self.create_array(spec)
            return

        object_id = spec.get("id")
        if not object_id:
            return
        self.object_defs[object_id] = dict(spec)
        if kind == "box":
            self.create_box(spec)
        elif kind == "node":
            self.create_node(spec)
        elif kind == "edge":
            self.create_edge(spec)
        elif kind == "label":
            self.create_label(spec)
        elif kind == "arrow":
            self.create_arrow(spec)
        elif kind == "pointer":
            self.create_pointer(spec)
        elif kind == "note":
            self.create_note(spec)

    def create_array(self, spec):
        values = spec.get("values", [])
        x = spec.get("x", 80)
        y = spec.get("y", 150)
        w = spec.get("cell_width", 58)
        h = spec.get("cell_height", 48)
        gap = spec.get("gap", 8)
        prefix = spec.get("id", "array")
        for index, value in enumerate(values):
            self.create_box({
                "id": f"{prefix}_{index}",
                "type": "box",
                "text": str(value),
                "x": x + index * (w + gap),
                "y": y,
                "width": w,
                "height": h,
                "fill": spec.get("fill", "#ffffff"),
            })

    def create_box(self, spec):
        x, y = spec.get("x", 80), spec.get("y", 80)
        w, h = spec.get("width", 64), spec.get("height", 48)
        fill = spec.get("fill", "#ffffff")
        outline = spec.get("outline", LINE)
        rect = self.canvas.create_rectangle(x, y, x + w, y + h, fill=fill, outline=outline, width=2)
        text = self.canvas.create_text(x + w / 2, y + h / 2, text=spec.get("text", ""), fill=spec.get("text_fill", INK), font=("Segoe UI", 12, "bold"))
        self.objects[spec["id"]] = {"kind": "box", "items": [rect, text], "x": x, "y": y, "width": w, "height": h, "text_item": text}
        if spec.get("hidden"):
            self.hide(spec["id"])

    def create_node(self, spec):
        x, y = spec.get("x", 80), spec.get("y", 80)
        radius = spec.get("radius", 26)
        fill = spec.get("fill", "#ffffff")
        outline = spec.get("outline", LINE)
        oval = self.canvas.create_oval(x, y, x + radius * 2, y + radius * 2, fill=fill, outline=outline, width=2)
        text = self.canvas.create_text(x + radius, y + radius, text=spec.get("text", spec["id"]), fill=spec.get("text_fill", INK), font=("Segoe UI", 12, "bold"))
        self.objects[spec["id"]] = {
            "kind": "node",
            "items": [oval, text],
            "x": x,
            "y": y,
            "width": radius * 2,
            "height": radius * 2,
            "text_item": text,
        }
        if spec.get("hidden"):
            self.hide(spec["id"])

    def create_label(self, spec):
        item = self.canvas.create_text(spec.get("x", 80), spec.get("y", 80), text=spec.get("text", ""), fill=spec.get("fill", INK), font=("Segoe UI", spec.get("size", 12)), anchor=spec.get("anchor", "nw"), width=spec.get("width", 360))
        self.objects[spec["id"]] = {"kind": "label", "items": [item], "x": spec.get("x", 80), "y": spec.get("y", 80), "width": 0, "height": 0, "text_item": item}
        if spec.get("hidden"):
            self.hide(spec["id"])

    def create_note(self, spec):
        self.create_label(spec)

    def create_arrow(self, spec):
        coords = self.arrow_coords(spec)
        item = self.canvas.create_line(*coords, arrow=tk.LAST, fill=spec.get("fill", AMBER), width=spec.get("width", 3), smooth=True)
        self.objects[spec["id"]] = {"kind": "arrow", "items": [item], "from": spec.get("from"), "to": spec.get("to"), "x": 0, "y": 0, "width": 0, "height": 0}
        if spec.get("hidden"):
            self.hide(spec["id"])

    def create_edge(self, spec):
        coords = self.arrow_coords(spec)
        arrow = tk.LAST if spec.get("directed") else tk.NONE
        item = self.canvas.create_line(*coords, arrow=arrow, fill=spec.get("fill", LINE), width=spec.get("width", 3), smooth=True)
        self.canvas.tag_lower(item)
        label_item = None
        if spec.get("text") is not None:
            sx, sy, tx, ty = coords
            label_item = self.canvas.create_text((sx + tx) / 2, (sy + ty) / 2 - 10, text=str(spec.get("text")), fill=MUTED, font=("Segoe UI", 10, "bold"))
        items = [item] + ([label_item] if label_item else [])
        self.objects[spec["id"]] = {
            "kind": "edge",
            "items": items,
            "line_item": item,
            "label_item": label_item,
            "from": spec.get("from"),
            "to": spec.get("to"),
            "x": 0,
            "y": 0,
            "width": 0,
            "height": 0,
        }
        if spec.get("hidden"):
            self.hide(spec["id"])

    def create_pointer(self, spec):
        target = spec.get("target")
        x, y = self.point_above(target) if target else (spec.get("x", 80), spec.get("y", 80))
        label = spec.get("text") or spec.get("id", "ptr")
        arrow = self.canvas.create_line(x, y, x, y + 34, arrow=tk.LAST, fill=spec.get("fill", ACCENT), width=3)
        text = self.canvas.create_text(x, y - 14, text=label, fill=spec.get("fill", ACCENT), font=("Segoe UI", 11, "bold"))
        self.objects[spec["id"]] = {"kind": "pointer", "items": [arrow, text], "x": x, "y": y, "width": 0, "height": 34, "target": target}
        if spec.get("hidden"):
            self.hide(spec["id"])

    def arrow_coords(self, spec):
        if spec.get("from") and spec.get("to"):
            sx, sy = self.center(spec["from"])
            tx, ty = self.center(spec["to"])
            return sx, sy, tx, ty
        return spec.get("x1", 80), spec.get("y1", 80), spec.get("x2", 160), spec.get("y2", 80)

    def center(self, object_id):
        obj = self.objects.get(object_id, {})
        return obj.get("x", 0) + obj.get("width", 0) / 2, obj.get("y", 0) + obj.get("height", 0) / 2

    def point_above(self, object_id):
        obj = self.objects.get(object_id, {})
        return obj.get("x", 0) + obj.get("width", 0) / 2, obj.get("y", 0) - 38

    def next_step(self):
        if self.running_step:
            return
        self.stop_jobs()
        self.playing = False
        if self.current_step + 1 >= len(self.steps):
            self.current_step = -1
            self.reset()
            return
        self.current_step += 1
        self.run_step(self.steps[self.current_step])
        self.update_status()

    def next_step_or_chapter(self):
        if self.running_step:
            return
        if self.current_step + 1 < len(self.steps):
            self.next_step()
        elif self.animations and self.current_animation_index + 1 < len(self.animations):
            self.select_animation(self.current_animation_index + 1)
        else:
            self.next_step()

    def previous_step(self):
        self.playing = False
        self.running_step = False
        self.stop_jobs()
        target = max(-1, self.current_step - 1)
        self.reset()
        for _ in range(target + 1):
            self.current_step += 1
            self.run_step(self.steps[self.current_step], animate=False)
        self.update_status()

    def previous_step_or_chapter(self):
        if self.running_step:
            return
        if self.current_step >= 0:
            self.previous_step()
        elif self.animations and self.current_animation_index > 0:
            self.select_animation(self.current_animation_index - 1)
            target_step = len(self.steps) - 1
            self.reset()
            for step_index in range(target_step + 1):
                self.current_step = step_index
                self.run_step(self.steps[step_index], animate=False)
            self.update_status()

    def toggle_play(self):
        self.playing = not self.playing
        self.update_status()
        if self.playing:
            self.play_next()
        else:
            self.stop_playback_timer()

    def pause_animation(self):
        self.playing = False
        self.play_all_enabled = False
        self.stop_playback_timer()

    def play_next(self):
        if not self.playing or self.running_step:
            return
        if self.current_step + 1 >= len(self.steps):
            if self.play_all_enabled and self.animations and self.current_animation_index + 1 < len(self.animations):
                self.select_animation(self.current_animation_index + 1, keep_play_all=True)
                self.animation_jobs.append(self.root.after(350, self.play_next))
                return
            self.playing = False
            self.play_all_enabled = False
            self.update_status()
            return
        self.current_step += 1
        duration = self.run_step(self.steps[self.current_step])
        self.update_status()
        wait = self.steps[self.current_step].get("wait", 1700)
        self.running_step = True
        self.animation_jobs.append(self.root.after(duration + wait, self.finish_play_step))

    def finish_play_step(self):
        self.running_step = False
        self.update_status()
        self.play_next()

    def run_step(self, step, animate=True):
        self.note_text.set(step.get("note", ""))
        self.update_canvas_note()
        max_duration = 0
        for action in step.get("actions", []):
            max_duration = max(max_duration, self.run_action(action, animate=animate))
        return max_duration

    def create_canvas_note(self):
        self.note_back = self.canvas.create_rectangle(0, 0, 0, 0, fill=CAPTION_BG, outline=CAPTION_LINE, width=2)
        self.note_item = self.canvas.create_text(
            0,
            0,
            text="",
            fill=INK,
            font=("Segoe UI", 12),
            anchor="nw",
            justify="left",
        )
        self.update_canvas_note()

    def update_canvas_note(self):
        if not self.note_item:
            return
        note = self.note_text.get()
        if not note:
            note = "Tip: resize wider if a dense animation overlaps the explanation."
        self.canvas.itemconfigure(self.note_item, text=note)
        self.position_canvas_note()

    def position_canvas_note(self):
        if not self.note_item or not self.note_back:
            return
        width = max(1, self.canvas.winfo_width())
        note_width = min(360, max(230, int(width * 0.32)))
        x = max(24, width - note_width - 28)
        y = 24
        self.canvas.itemconfigure(self.note_item, width=note_width - 28)
        self.canvas.coords(self.note_item, x + 14, y + 12)
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox(self.note_item)
        if not bbox:
            bbox = (x + 14, y + 12, x + note_width - 14, y + 64)
        self.canvas.coords(self.note_back, x, y, x + note_width, bbox[3] + 14)
        self.canvas.tag_raise(self.note_back)
        self.canvas.tag_raise(self.note_item)

    def run_action(self, action, animate=True):
        if "show" in action:
            for target in self.as_targets(action["show"]):
                self.show(target)
            return 0
        elif "hide" in action:
            for target in self.as_targets(action["hide"]):
                self.hide(target)
            return 0
        elif "highlight" in action or "compare" in action:
            for target in self.as_targets(action.get("highlight", action.get("compare"))):
                self.set_outline(target, AMBER, width=4)
            return 0
        elif "clear_highlight" in action:
            for target in self.as_targets(action["clear_highlight"]):
                self.set_outline(target, LINE, width=2)
            return 0
        elif "mark_done" in action:
            for target in self.as_targets(action["mark_done"]):
                self.set_outline(target, GREEN, width=4)
            return 0
        elif "set_text" in action:
            data = action["set_text"]
            self.set_text(data.get("target"), data.get("text", ""))
            return 0
        elif "set_color" in action:
            data = action["set_color"]
            self.set_fill(data.get("target"), data.get("fill"))
            return 0
        elif "move" in action:
            data = action["move"]
            return self.move_to(data.get("target"), data.get("x"), data.get("y"), animate=animate, duration=data.get("duration", 900))
        elif "move_by" in action:
            data = action["move_by"]
            obj = self.objects.get(data.get("target"))
            if obj:
                return self.move_to(data.get("target"), obj["x"] + data.get("dx", 0), obj["y"] + data.get("dy", 0), animate=animate, duration=data.get("duration", 900))
            return 0
        elif "swap_position" in action:
            a, b = action["swap_position"]
            return self.swap_position(a, b, animate=animate, duration=action.get("duration", 1050))
        elif "swap_text" in action:
            a, b = action["swap_text"]
            self.swap_text(a, b)
            return 0
        elif "point_to" in action:
            data = action["point_to"]
            return self.point_to(data.get("pointer"), data.get("target"), animate=animate, duration=data.get("duration", 900))
        elif "say" in action:
            self.note_text.set(str(action["say"]))
            self.update_canvas_note()
            return 0
        elif "reset" in action:
            self.reset()
            return 0
        return 0

    def as_targets(self, value):
        return value if isinstance(value, list) else [value]

    def set_outline(self, target, color, width=3):
        obj = self.objects.get(target)
        if obj and obj["kind"] in {"box", "node"}:
            self.canvas.itemconfigure(obj["items"][0], outline=color, width=width)
        elif obj and obj["kind"] in {"edge", "arrow"}:
            self.canvas.itemconfigure(obj["items"][0], fill=color, width=width)

    def set_fill(self, target, fill):
        obj = self.objects.get(target)
        if obj and fill and obj["kind"] in {"box", "node"}:
            self.canvas.itemconfigure(obj["items"][0], fill=fill)

    def set_text(self, target, text):
        obj = self.objects.get(target)
        if obj and obj.get("text_item"):
            self.canvas.itemconfigure(obj["text_item"], text=str(text))

    def show(self, target):
        obj = self.objects.get(target)
        if obj:
            for item in obj["items"]:
                self.canvas.itemconfigure(item, state="normal")

    def hide(self, target):
        obj = self.objects.get(target)
        if obj:
            for item in obj["items"]:
                self.canvas.itemconfigure(item, state="hidden")

    def move_to(self, target, x, y, animate=True, duration=320):
        obj = self.objects.get(target)
        if not obj or x is None or y is None:
            return 0
        if not animate:
            self.move_object_by(target, x - obj["x"], y - obj["y"])
            return 0
        frames = max(1, int(duration / 16))
        dx = (x - obj["x"]) / frames
        dy = (y - obj["y"]) / frames

        def tick(remaining):
            if remaining <= 0:
                self.move_object_by(target, x - obj["x"], y - obj["y"])
                return
            self.move_object_by(target, dx, dy)
            self.animation_jobs.append(self.root.after(16, lambda: tick(remaining - 1)))

        tick(frames)
        return duration

    def move_object_by(self, target, dx, dy):
        obj = self.objects.get(target)
        if not obj:
            return
        for item in obj["items"]:
            self.canvas.move(item, dx, dy)
        obj["x"] += dx
        obj["y"] += dy
        self.refresh_arrows()

    def swap_position(self, a, b, animate=True, duration=420):
        first = self.objects.get(a)
        second = self.objects.get(b)
        if not first or not second:
            return 0
        ax, ay = first["x"], first["y"]
        bx, by = second["x"], second["y"]
        first_duration = self.move_to(a, bx, by, animate=animate, duration=duration)
        second_duration = self.move_to(b, ax, ay, animate=animate, duration=duration)
        return max(first_duration, second_duration)

    def swap_text(self, a, b):
        first = self.objects.get(a)
        second = self.objects.get(b)
        if not first or not second or not first.get("text_item") or not second.get("text_item"):
            return
        first_text = self.canvas.itemcget(first["text_item"], "text")
        second_text = self.canvas.itemcget(second["text_item"], "text")
        self.set_text(a, second_text)
        self.set_text(b, first_text)

    def point_to(self, pointer, target, animate=True, duration=320):
        obj = self.objects.get(pointer)
        if not obj:
            return 0
        x, y = self.point_above(target)
        move_duration = self.move_to(pointer, x, y, animate=animate, duration=duration)
        obj["target"] = target
        return move_duration

    def refresh_arrows(self):
        for object_id, obj in self.objects.items():
            if obj["kind"] in {"arrow", "edge"} and obj.get("from") and obj.get("to"):
                spec = {"from": obj["from"], "to": obj["to"]}
                self.canvas.coords(obj["items"][0], *self.arrow_coords(spec))
                if obj["kind"] == "edge" and obj.get("label_item"):
                    sx, sy, tx, ty = self.arrow_coords(spec)
                    self.canvas.coords(obj["label_item"], (sx + tx) / 2, (sy + ty) / 2 - 10)

    def stop_jobs(self):
        for job in self.animation_jobs:
            try:
                self.root.after_cancel(job)
            except tk.TclError:
                pass
        self.animation_jobs = []

    def stop_playback_timer(self):
        self.running_step = False
        self.stop_jobs()
        self.update_status()

    def update_status(self):
        total = len(self.steps)
        current = self.current_step + 1 if self.current_step >= 0 else 0
        mode = "Playing" if self.playing else "Paused"
        if self.running_step:
            mode = "Animating"
        chapter = ""
        if self.animations:
            chapter = f" - Chapter {self.current_animation_index + 1} of {len(self.animations)}"
        self.status.config(text=f"{mode}{chapter} - Step {current} of {total}")
        if hasattr(self, "play_button"):
            self.play_button.config(text="Pause" if self.playing else "Play")


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SAMPLE
    root = tk.Tk()
    AnimatorRenderer(root, path)
    root.mainloop()


if __name__ == "__main__":
    main()
