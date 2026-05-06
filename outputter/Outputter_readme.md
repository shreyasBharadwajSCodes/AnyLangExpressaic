# Outputter Tools

This folder contains the current local tools for reading, creating, and studying
AnyLanguageExpressaic lesson YAML files.

The main tools are:

```text
outputter/src/vis2.py
outputter/src/lesson_builder.py
outputter/src/lesson_builder_vis2.py
```

---

## Vis2

`vis2.py` is the main lesson viewer.

It renders Vis2 YAML lessons into study modes:

* Lesson mode for guided learning
* Revision mode for quick interview prep
* Transition mode for moving from one language to another
* Raw Structure mode for inspecting filtered YAML

Run:

```bash
python outputter/src/vis2.py
```

Vis2 opens `templates/vis2_welcome_template.yaml` by default when no usable
local config is present.

---

## Lesson Builder

`lesson_builder.py` is the visual authoring tool for Vis2 YAML files.

`lesson_builder_vis2.py` is the newer combined tool. It keeps the Vis2-like
study surface as the main experience, while edit options appear only when users
right-click or double-click a card.

Run:

```bash
python outputter/src/lesson_builder.py
python outputter/src/lesson_builder_vis2.py
```

You can also open it from Vis2 using:

```text
Ctrl+B
```

or the **Builder Vis2** button.

The builder supports:

* adding lesson components
* editing metadata
* Vis2-style Lesson, Revision, Transition, and Raw Structure modes
* right-click editing without leaving the reading view
* adding custom YAML labels such as notes, categories, and future metadata
  without disturbing the UI structure
* creating explanations
* creating language lenses
* creating comparison tables
* creating code comparisons
* creating transition paths
* creating revision summaries
* creating revision tables
* creating flashcards
* adding components before or after cards from the right-click menu
* dragging cards to reorder components
* inline edit controls that appear only when needed
* undo and redo
* opening existing YAML
* saving new YAML lessons

---

## Suggested Workflow

1. Open the Lesson Builder.
2. Prefer `lesson_builder_vis2.py` for a UI-first workflow.
3. Start in Lesson mode to see how the lesson reads.
4. Right-click a card to edit, add before/after, duplicate, delete, or edit YAML directly.
5. Double-click a card for inline editing.
6. Drag cards to reposition components.
7. Right-click the page title area to edit lesson-level details.
8. Save the lesson under `knowledge/`.
9. Open the lesson folder in Vis2.
10. Test Lesson, Revision, Transition, and Raw Structure modes.

---

## YAML Lesson Focus

Lessons should be interview-prep friendly and language-transition focused.

Good lessons should include:

* the shared concept
* how each language wants the learner to think
* short interview-style examples
* language-specific traps
* source-to-target transition paths
* habit swaps
* false friends
* quick revision tables
* flashcards

The goal is not word-for-word syntax translation. The goal is to help students
switch thinking between languages for coding interviews.

---

## Dependencies

Required:

```bash
pip install pyyaml
```

Both tools use Python's built-in Tkinter GUI library.

---

## Local Config

Vis2 may create a local ignored file:

```text
vis2_config.yaml
```

This stores the last opened lesson folder and file. It is ignored by Git and is
not part of the lesson content.
