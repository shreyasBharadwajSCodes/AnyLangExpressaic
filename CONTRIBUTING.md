# Contributing to AnyLanguageExpressaic

## Overview

AnyLanguageExpressaic is a structured system for learning programming concepts across multiple languages.
The focus is on **thinking, comparison, and depth**, not just syntax.

This repository is the **source of truth**.
Contributions should be made through pull requests to keep knowledge centralized.

---

## Ways to Contribute

### Concepts (Primary Contribution)

* Add new concept YAML files
* Improve existing concepts
* Add new languages to existing concepts
* Improve depth, clarity, and comparisons

### Tooling

* Improve GUI
* Improve CLI tools
* Add validation or generation utilities

### Documentation

* Improve guides and examples
* Clarify usage and contribution flow

---

## Using the Project

### Run from Source

```bash id="2slm4a"
pip install pyyaml
python outputter/src/gui.py
```

### Use Executable

* Download from releases
* Run the `.exe` file directly
* No setup required

### Planned CLI Usage

```bash id="9vt7wz"
outputter render <concept> <language>
outputter compare <concept> <lang1> <lang2>
```

---

## Concept Structure (YAML)

Each concept must follow a consistent structure.

### Required Top-Level Fields

```yaml id="9j4vbt"
concept:
overview:
languages:
operations_map:
```

---

## Language Section

```yaml id="y8r1f0"
languages:
  <language>:
    mental_model:
    how_to_think:
    what_to_avoid:
    responsibilities:
    syntax:
    operations:
    traps:
    depth:
      internals:
      performance:
      edge_cases:
      advanced_patterns:
```

---

## What to Include

Focus on clarity and usefulness.

### Mental Model

* How should this concept be understood?
* What is the simplest correct intuition?

### How To Think

* What is the natural way to use this concept?
* What habits should be followed?

### What To Avoid

* Common mistakes
* Wrong assumptions from other languages

### Responsibilities

* What the developer must handle explicitly

### Syntax

* Minimal, clear examples
* No unnecessary complexity

### Operations

* Practical use cases
* Comparable across languages

### Traps

* Real mistakes developers make
* Must be practical, not theoretical

### Depth

Answer deeper questions:

* How does this work internally?
* What are the performance implications?
* What edge cases exist?
* What advanced patterns are used?

---

## Operations Map

```yaml id="d63n4k"
operations_map:
  - idea: <operation>
    python: <code>
    cpp: <code>
    java: <code>
```

Guidelines:

* Same idea across all languages
* Keep it comparable
* Avoid unnecessary variations

---

## Questions Every Concept Must Answer

Before submitting, ensure your concept answers:

1. What is this concept?
2. Why does it exist?
3. How should it be thought about?
4. How is it implemented in each language?
5. What are common mistakes?
6. How do languages differ?
7. What happens internally?
8. What are performance implications?
9. Where is it used in practice?

---

## Adding a New Concept

1. Create file:

```text id="0b9z9y"
knowledge/<concept>.yaml
```

2. Follow the defined structure

3. Test in GUI:

* Load file
* Verify Table, Code, Visual views

4. Validate:

* No missing sections
* Consistent mapping across languages

---

## Contribution Flow

1. Fork the repository
2. Create a new branch
3. Add or update concept files
4. Test locally
5. Submit a pull request

Note:
Forks are for experimentation.
All meaningful contributions should be submitted back to this repository
so that it is beneficial for the users.

---

## Style Guidelines

* Keep content concise
* Prefer clarity over completeness
* Avoid repetition
* Use simple language
* Maintain consistent structure

---

## Notes

* One YAML file per concept
* Focus on learning value
* Avoid overengineering
* Ensure consistency across languages

---

## Vision

A system where:

* Concepts are learned once
* Thinking transfers across languages
* Syntax becomes secondary
