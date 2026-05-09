# AnyLanguageExpressaic

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-green)

**AnyLanguageExpressaic is a high-signal learning and knowledge system for moving between programming languages.**

It is built for people who do not just want syntax translation. The goal is to teach how thinking changes across languages: data structure choices, memory behavior, references, mutability, equality, hashing, iteration costs, standard-library habits, and interview implementation patterns.

The current focus is **DSA interview preparation across Python, C++, and Java**.

## Why It Matters

Most language-comparison material says:

```text
Python list = C++ vector = Java ArrayList
```

That is not enough for real interviews or real code.

AnyLanguageExpressaic explains the actual shift:

```text
Python list stores references and encourages direct expression.
C++ vector stores typed values contiguously and forces you to care about copies, references, and invalidation.
Java separates primitive arrays from collection classes and makes equality, boxing, and interfaces matter.
```

That difference is the project.

## High-Signal YAML Knowledge

The content is stored as structured YAML lessons. These files are designed to be:

- readable by humans
- easy to render in the Vis2 viewer
- easy to revise quickly
- useful for interview preparation
- structured enough for AI-assisted generation, validation, and retrieval
- high signal for the operability of small language models

The YAML format keeps concepts compact and explicit: goals, explanations, language lenses, code comparisons, transition paths, common traps, revision tables, and flashcards.

This makes the knowledge base especially useful for smaller models because the data is not noisy prose. It is organized, predictable, and dense with the exact reasoning a model needs to answer or teach well.

## What The Lessons Teach

Each lesson is meant to explain:

- the core algorithm or data structure strategy
- how Python, C++, and Java think differently about the same concept
- what variables mean while code runs
- why key implementation steps are done
- common interview traps and edge cases
- when a method is appropriate
- how to revise the topic quickly

Examples are not meant to be decorative. Code comments focus on important state changes and language caveats, not obvious syntax.

## Current DSA Coverage

The DSA knowledge base includes:

- language readiness and implementation basics
- complexity and cost models
- language internals for Python, C++, and Java
- core data structures
- algorithmic patterns
- graph and tree foundations
- dynamic-programming planning
- important interview problem tracks
- final revision and cheat-table planning

The strongest current areas are language readiness, foundations, core data structures, and algorithmic patterns.

## How To Read The Content

Start with the DSA booklet:

```text
knowledge/dsa/dsa_interview_booklet.yaml
```

Use it as the table of contents, then open the linked lesson YAML files in Vis2. For a fast path, read in this order:

- quick revision
- foundations
- core data structures
- algorithmic patterns

For details on running the viewer, opening the DSA folder, and using the builder, see `outputter/Outputter_readme.md`.

## Vis2 Viewer

The main viewer is `outputter/src/vis2.py`.

It opens YAML lessons and renders them as:

- lesson view
- revision view
- transition view
- filtered language view
- raw YAML preview

Run with:

```bash
python outputter/src/vis2.py
```

Install the YAML dependency if needed:

```bash
pip install pyyaml
```

For detailed run instructions, builder usage, and troubleshooting, see `outputter/Outputter_readme.md`.

## Authoring

New lessons should follow the project's YAML style:

- valid YAML only
- clear lesson goal
- language-specific thinking blocks
- comparable Python/C++/Java examples
- code comments only for meaningful algorithm state or caveats
- transition paths such as `python_to_cpp` and `python_to_java`
- compact revision tables and flashcards

Useful authoring references:

- `templates/yaml-generation-prompt.md`
- `templates/compare-template.yaml`
- `outputter/src/lesson_builder_vis2.py`

For AI agents and small language models working on this repository, see `AGENTS.md`.

## Contributing

Contributions are welcome. The best way to contribute is to fork the repository, make focused changes in your fork, and open a pull request.

Good contributions include:

- improving YAML lessons
- adding missing interview topics
- improving Python/C++/Java language-thinking sections
- fixing YAML rendering issues
- improving Vis2 or builder usability
- improving documentation

For the full contribution flow and expectations, see `CONTRIBUTING.md`.

## Who It Is For

AnyLanguageExpressaic is for:

- students preparing for DSA interviews
- Python developers learning C++ or Java
- Java developers moving to Python or C++
- C++ developers learning higher-level language habits
- educators creating cross-language lessons
- builders experimenting with structured, high-signal data for small language models

## Project Direction

The project is moving toward a richer structured knowledge base that can support:

- better DSA learning across languages
- stronger revision workflows
- AI-assisted lesson generation and cleanup
- lightweight model-friendly knowledge retrieval
- clearer visual rendering of programming concepts

The north star is simple: **teach language thinking, not just language syntax.**
