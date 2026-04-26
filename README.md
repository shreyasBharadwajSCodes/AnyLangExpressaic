# AnyLanguageExpressaic

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-green)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen)

A structured system for learning programming concepts across multiple languages with a focus on thinking, comparison, and depth.

---

## Overview

AnyLanguageExpressaic helps you understand how the same concept is expressed across different programming languages.
Instead of memorizing syntax, it focuses on:

* Mental models
* Cross-language mapping
* Practical operations
* Internal behavior and performance

---

## Features

* Multi-language comparison (Python, C++, Java and more)
* Table View for operations mapping
* Code View for syntax comparison
* Visual View for mental models and depth
* YAML-based structured knowledge
* Built-in YAML editor with shortcuts
* Folder-based navigation for concepts
* Standalone executable support

---

## How It Works

1. Concepts are defined in structured YAML files
2. The renderer interprets YAML into multiple views:

   * Table View (operations comparison)
   * Code View (side-by-side implementation)
   * Visual View (thinking and depth)
   * Text View (full structured explanation)
3. Users can compare multiple languages dynamically

---

## Installation

### Option 1: Run from Source

```bash id="8z2xj3"
pip install pyyaml
python outputter/src/gui.py
```

### Option 2: Use Executable

* Download the latest release from GitHub
* Run the executable file directly

---

## Usage

* Open a base folder containing YAML concept files
* Select a concept from the sidebar
* Add languages for comparison
* Navigate views:

  * Table View for quick mapping
  * Code View for syntax
  * Visual View for understanding
  * YAML View for editing

---

## Repository Structure

```text id="n3gk1q"
knowledge/
  variables.yaml
  loops.yaml

outputter/
  src/
    gui.py

assets/
  icon.ico
```

---

## Contributing

Contributions are welcome.

* Add new concept YAML files
* Improve existing mappings
* Add support for more languages
* Improve GUI or tooling

See CONTRIBUTING.md for full details.

---

## Roadmap

See ROADMAP.md for planned features and direction.

---

## License

This project is licensed under the MIT License.

---

## Keywords

programming concepts
multi-language comparison
python cpp java
learning programming
data structures
algorithms
cross-language translation
software engineering
developer tools
code comparison
programming education

---

## Vision

Learn a concept once and apply it across languages.
