# AGENTS.md

This file is for AI coding agents and small language models working on AnyLanguageExpressaic.

## Project Purpose

AnyLanguageExpressaic is a structured YAML knowledge base and local viewer for learning programming concepts across languages.

The current priority is DSA interview preparation across Python, C++, and Java. The content should teach language thinking, not only syntax translation.

## Important Files

- `README.md`: public project overview.
- `outputter/Outputter_readme.md`: how to run the viewer and builder.
- `CONTRIBUTING.md`: contribution flow and contributor expectations.
- `templates/yaml-generation-prompt.md`: preferred prompt and content expectations for lesson YAML.
- `knowledge/dsa/dsa_interview_booklet.yaml`: DSA table of contents.
- `knowledge/dsa/**`: lesson YAML files.
- `outputter/src/vis2.py`: main YAML viewer.
- `outputter/src/lesson_builder_vis2.py`: viewer plus builder/editor.

## Working Rules For Agents

- Prefer YAML/content changes unless the user explicitly asks for tool code changes.
- Keep `knowledge/dsa/dsa_interview_booklet.yaml` directly under `knowledge/dsa`.
- Organize DSA lesson files into section folders under `knowledge/dsa`.
- Do not add `status: planned` to completed lesson entries.
- Do not create separate variable tracker sections.
- Explain important variables and algorithm state inside code examples with concise comments.
- Do not comment obvious syntax.
- Use `|` for code blocks.
- Use `>` for longer prose blocks.
- Avoid backticks inside YAML prose because they have caused rendering issues.
- Quote list strings that contain `: ` if they are plain prose.
- Keep language ids as `python`, `cpp`, and `java`.

## YAML Lesson Quality Bar

Each strong lesson should include:

- clear goal
- beginner-friendly concept explanation
- method or algorithm strategy
- Python/C++/Java language lenses
- behind-the-scenes language differences
- comparable code examples
- practical interview traps
- transitions such as `python_to_cpp` and `python_to_java`
- revision summary, cheat table, and flashcards
- notes and `tlm_hooks` when useful

The content should be high signal for humans and small language models: compact, explicit, structured, and low-noise.

## DSA Content Style

When writing DSA lessons:

- Start with the method: what the structure or algorithm is doing.
- Explain when to use it.
- Explain how state changes while the code runs.
- Highlight internal differences across Python, C++, and Java.
- Mention caveats such as overflow, references, mutability, equality, hashing, heap direction, iterator invalidation, null checks, and copying behavior.
- Keep examples interview-relevant.

Code comments should explain:

- why a pointer moves
- what a window contains
- why a prefix or count is updated
- why a null check, cast, copy, or erase is needed
- what invariant is restored after a loop or branch

Code comments should not explain:

- basic assignment
- basic loop syntax
- obvious function calls
- generic language syntax that does not affect the algorithm

## Validation Checklist

Before finishing YAML work, check:

- no `variable_tracker` or `variable_walkthrough`
- no stray backticks in YAML prose
- no tabs or trailing whitespace
- no fragile unquoted prose list items containing `: `
- code examples use block scalars
- `git diff --check` passes for touched files

Useful command:

```bash
git diff --check -- README.md outputter/Outputter_readme.md knowledge/dsa
```

## Running The Tools

For full run instructions, see:

```text
outputter/Outputter_readme.md
```

Quick start:

```bash
pip install pyyaml
python outputter/src/vis2.py
```

Builder:

```bash
python outputter/src/lesson_builder_vis2.py
```

## Contribution Guidance

Encourage users to fork the repository, make changes in their fork, and open a pull request.

For contributor-facing details, point them to:

```text
CONTRIBUTING.md
```

