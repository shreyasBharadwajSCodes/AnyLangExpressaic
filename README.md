# AnyLanguageExpressaic

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-green)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen)

AnyLanguageExpressaic is a learning tool for programmers moving from one language to another.

It helps you learn the same programming concept through the thinking style of different languages. Instead of only showing syntax translations, it focuses on mental models, habits, traps, examples, revision tables, and language-to-language transition paths.

If you know Python and want to learn C++, or you know Java and want to write natural Python, this project is built for that shift.

---

## Why This Exists

Most programming comparison tools answer:

> What is the syntax for this in another language?

AnyLanguageExpressaic tries to answer:

> How should I change the way I think when moving from one language to another?

For example, moving from Python collections to C++ STL is not just:

```text
list = vector
dict = unordered_map
```

The real lesson is:

```text
Python encourages direct built-in expression.
C++ asks you to choose containers by guarantees, memory behavior, and cost.
Java encourages interface-first design with implementation choices.
```

That is the kind of learning this software is designed to support.

---

## Key Features

* Language-transition learning for Python, C++, Java, and future languages
* Lesson mode for new readers
* Revision mode for quick review with tables and flashcards
* Transition mode for source-language to target-language thinking
* Global language filter to show only the languages the learner wants
* YAML-based lesson files that are easy to generate, edit, and share
* Image placeholders and asset support for diagrams and examples
* Folder-based YAML browsing with persistence
* Keyboard shortcuts for fast navigation
* Authoring template and AI prompt for generating new lesson files

---

## Vis2

The current main experience is `vis2.py`.

Vis2 reads component-style YAML lessons and renders them as:

* beginner-friendly lessons
* compact revision material
* language-to-language transition guides
* filtered views for selected languages
* raw filtered YAML previews

Run it with:

```bash
python outputter/src/vis2.py
```

Install the required dependency first:

```bash
pip install pyyaml
```

---

## How It Works

Each concept file is a structured YAML lesson.

A good lesson contains:

* the shared concept
* how each language wants you to think
* examples across languages
* transition paths such as `python_to_cpp` or `java_to_python`
* habit swaps using language names
* false friends where similar terms behave differently
* revision summaries, cheat tables, and flashcards
* optional image placeholders for diagrams

Example transition block:

```yaml
transitions:
  python_to_cpp:
    title: Moving from Python to C++
    mindset_shift:
      - From runtime flexibility to explicit types and compile-time checks.
      - From convenience first to guarantees, costs, and ownership.
    habit_swaps:
      - python: Use list for most ordered data.
        cpp: Start with vector, but understand allocation and invalidation.
    false_friends:
      - term: list
        warning: C++ list is a linked list, not the equivalent of Python list.
```

---

## Authoring New Lessons

Use these files:

* `templates/compare-template.yaml` - a full reusable Vis2 lesson template
* `templates/yaml-generation-prompt.md` - a prompt for generating useful YAML lessons with AI

The prompt is designed to produce lessons that are actually useful:

* not just syntax
* not just tables
* not rigid textbook notes
* but mental models, examples, traps, revision material, and transition guidance

Suggested workflow:

1. Copy the prompt from `templates/yaml-generation-prompt.md`
2. Fill in the topic, audience, languages, and transition paths
3. Generate the YAML
4. Save it under `knowledge/`
5. Open the folder in Vis2
6. Review the lesson, revision, and transition tabs
7. Improve the YAML as needed

---

## Example Knowledge File

The sample file:

```text
knowledge/dsa/stl_vs_collections.yaml
```

demonstrates how to compare:

* Python collections
* C++ STL containers
* Java Collections

It includes lesson blocks, code comparisons, revision tables, flashcards, and transition paths like:

* `python_to_cpp`
* `cpp_to_python`
* `java_to_cpp`
* `cpp_to_java`

---

## Keyboard Shortcuts

Vis2 includes shortcuts for faster study:

* `Ctrl+O` - open YAML folder
* `Ctrl+R` - reload current YAML
* `Up` / `Down` - previous or next YAML file
* `PageUp` / `PageDown` - jump through YAML files
* `Home` / `End` - first or last YAML file
* `Ctrl+1` - lesson mode
* `Ctrl+2` - revision mode
* `Ctrl+3` - transition mode
* `Ctrl+4` - raw structure mode
* `Ctrl+Left` / `Ctrl+Right` - cycle views
* `Ctrl+T` or `Ctrl+Enter` - show transition mode
* `Ctrl+Shift+T` - swap transition languages

---

## Repository Structure

```text
knowledge/
  dsa/
    stl_vs_collections.yaml

templates/
  compare-template.yaml
  yaml-generation-prompt.md

outputter/
  src/
    vis2.py

assets/
  icon.ico
```

---

## Who This Is For

AnyLanguageExpressaic is useful for:

* Python developers learning C++
* Java developers learning Python
* C++ developers learning Java
* students revising data structures and algorithms
* interview preparation across multiple programming languages
* educators creating programming language comparison lessons
* learners who want to understand mental models, not memorize syntax

---

## Search Keywords

programming language comparison,
Python to C++,
C++ STL vs Python collections,
Java Collections vs C++ STL,
Python Java C++ data structures,
learn programming languages,
language transition learning,
mental models for programming,
data structures across languages,
algorithms across languages,
coding interview revision,
programming education tool,
YAML learning content,
multi-language programming lessons,
cross-language programming concepts

---

## Roadmap

Planned directions:

* More concept files for core programming and DSA topics
* More language support
* Better image and diagram rendering
* YAML validation tools
* Export to Markdown or HTML
* TLM/AI-assisted lesson generation and review
* Web version
* VS Code extension

---

## Contributing

Contributions are welcome.

Good contributions include:

* new Vis2 YAML lessons
* improved transition paths
* better examples and false friends
* image assets and diagrams
* YAML validation tooling
* UI improvements to Vis2
* support for more languages

See `CONTRIBUTING.md` for more details.

---

## License

This project is licensed under the MIT License.

---

## Vision

Learn a concept once.

Then learn how each language wants you to think about it.
