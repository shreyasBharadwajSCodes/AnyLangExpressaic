# Outputter Tools

The `outputter` folder contains the local desktop tools used to view, study, and edit AnyLanguageExpressaic YAML lessons.

For most users, the recommended way to run the app is the packaged executable:

```text
vis2.exe
```

The Python source files are mainly for contributors and developers.

## Run Vis2

Use the packaged executable when available:

```text
vis2.exe
```

If the executable is inside the build output folder, run:

```text
dist/vis2.exe
```

Vis2:

- opens a desktop YAML lesson viewer
- remembers the last opened folder and file
- renders lesson, revision, transition, and raw YAML views
- lets you filter the visible languages
- lets you move through YAML files in a folder

On first launch, Vis2 opens the welcome template if no previous config is available.

## Open The DSA Lessons

After launching Vis2:

1. Choose **Open YAML Folder**.
2. Select `knowledge/dsa`.
3. Pick a lesson from the sidebar.
4. Switch between Lesson, Revision, Transition, and Raw views as needed.

For the DSA booklet, open:

```text
knowledge/dsa/dsa_interview_booklet.yaml
```

## Developer Source Run

Most users should not need this section. Use it only if you are developing the tool or the executable is not available.

Run commands from the repository root:

```bash
cd AnyLangExpressaic
```

Install the YAML dependency:

```bash
pip install pyyaml
```

Run the viewer from source:

```bash
python outputter/src/vis2.py
```

The tools also use Python's built-in Tkinter GUI library. On most Windows Python installs, Tkinter is usually included.

## Developer Builder

Run the combined viewer/editor from source:

```bash
python outputter/src/lesson_builder_vis2.py
```

You can also open the builder from Vis2 with:

```text
Ctrl+B
```

Use the builder when you want to:

- create a new YAML lesson
- edit lesson metadata
- edit cards inline
- add explanations, language lenses, tables, examples, transitions, revision blocks, and flashcards
- duplicate or delete cards
- reorder lesson sections
- edit raw YAML for a card
- save a lesson under `knowledge/`

## Recommended Workflow

1. Run `vis2.exe`.
2. Open `knowledge/dsa`.
3. Read lessons in Lesson, Revision, and Transition views.
4. Use the builder only when you need to edit or create YAML lessons.
5. Save edited YAML under `knowledge/`.
6. Reopen or refresh the lesson in Vis2.

When editing DSA lessons, keep code comments focused on meaningful algorithm state, variable movement, or language-specific caveats. Avoid comments that explain obvious syntax.

## Local Config

The tools may create:

```text
vis2_config.yaml
```

This stores local UI state such as the last opened YAML folder and file. It is not lesson content.

## Common Issues

If `vis2.exe` is not available, use the developer source run:

```bash
python outputter/src/vis2.py
```

If Python is not found:

```bash
py outputter/src/vis2.py
```

If source-mode YAML loading fails, check that `pyyaml` is installed:

```bash
python -m pip install pyyaml
```

If a YAML file does not render:

- check indentation
- avoid fragile inline strings with unquoted `: `
- use `|` for code blocks
- use `>` for longer prose blocks
- avoid unnecessary Markdown characters inside YAML prose

If the UI opens but no lesson appears, use **Open YAML Folder** and choose a folder that contains `.yaml` files.

## What The Viewer Expects

The best YAML lessons usually include:

- `id`
- `title`
- `goal`
- `lesson`
- `examples`
- `transitions`
- `interview_questions`
- `revision`
- `notes`
- `tlm_hooks`

The viewer is intentionally flexible, but consistent lesson structure makes the content easier for humans and small language models to use.
