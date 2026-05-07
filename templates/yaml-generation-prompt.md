# AnyLanguageExpressaic YAML Generation Prompts

Use these prompts with GPT, Claude, or another AI tool to create YAML files for
Vis2 and Builder Vis2.

The goal is not syntax translation. The goal is to help learners switch their
thinking between programming languages, especially for interview preparation.

---

## 1. Lesson YAML Prompt

Use this when you want one lesson file, such as `hashmap_dictionary.yaml`,
`sliding_window.yaml`, or `python_dict_to_java_hashmap.yaml`.

```text
You are creating a YAML lesson for AnyLanguageExpressaic.

Return only valid YAML. Do not wrap the answer in Markdown fences. Do not add
explanatory text outside the YAML.

Topic:
[WRITE TOPIC HERE]

Audience:
Students preparing for coding interviews who already know at least one language
and want to think clearly in another language.

Languages:
[WRITE LANGUAGES HERE, for example: python, cpp, java]

Main transitions to support:
[WRITE TRANSITIONS HERE, for example: python_to_java, python_to_cpp, java_to_cpp]

Required top-level YAML structure:
- id
- title
- category
- level
- languages
- tags
- goal
- assets
- lesson
- examples
- transitions
- interview_questions
- revision
- notes
- tlm_hooks

Content requirements:
1. Teach the concept as a lesson for a new reader.
2. Make revision mode compact, table-friendly, and fast to scan.
3. Teach language thinking, not word-for-word syntax translation.
4. Include language_lens blocks for every language.
5. Include practical code-thinking switches:
   - what feels natural in each language
   - what habits should not be carried over
   - what changes in mutability, equality, hashing, references, memory,
     iteration, performance, or library usage
6. Include short comparable code examples in every language.
7. Include at least one example showing a common interview mistake or edge case.
8. Include transition paths for every requested source_to_target pair.
9. In each transition path include:
   - title
   - mindset_shift
   - habit_swaps
   - false_friends
10. In habit_swaps, use actual language names as keys, not old/new.
11. Include interview_questions with direct answers.
12. Include revision.quick_summary, revision.cheat_table, and revision.flashcards.
13. Include image placeholders under assets when a diagram would help.
14. Keep examples short enough to fit in a desktop learning UI.
15. Add useful custom labels such as notes, categories, prerequisites, or
    related_patterns if they improve the lesson. Custom labels are allowed.

YAML style rules:
- Use valid indentation.
- Use block scalars `|` for multi-line code.
- Keep list/table rows clean and consistent.
- Use ids and file-style names in snake_case.
- Use language ids like python, cpp, java.
- Transition keys must use source_to_target format.

Quality bar:
- A beginner should understand the concept.
- A revising student should get value from the tables and short notes.
- A language-switching student should learn what habits to change.
- Interview examples should be practical, not toy-only.

Now generate the YAML.
```

---

## 2. Interview And Practical Switch Enrichment Prompt

Use this when a YAML exists but feels too theoretical.

```text
Improve this AnyLanguageExpressaic YAML lesson.

Return only the improved valid YAML. Do not wrap it in Markdown fences.

Focus on adding:
1. Interview-style questions and direct answers.
2. Practical code-thinking switches between languages.
3. Common mistakes developers make when moving from one language to another.
4. Short comparable code examples.
5. Edge cases that appear in coding interviews.
6. Revision tables with very few words.
7. Flashcards that test mental models, not only syntax.
8. Notes and categories where useful.

Do not remove useful existing content.
Do not turn the lesson into generic theory.
Do not make the YAML rigid; custom labels are allowed if they help.

Here is the YAML to improve:

[PASTE YAML HERE]
```

---

## 3. Booklet YAML Prompt

Use this when you want a navigable table of contents, such as a DSA interview
prep booklet.

```text
You are creating a booklet YAML for AnyLanguageExpressaic.

Return only valid YAML. Do not wrap the answer in Markdown fences.

Booklet topic:
[WRITE BOOKLET TOPIC HERE, for example: DSA Interview Prep Across Languages]

Audience:
[WRITE AUDIENCE HERE]

Languages:
[WRITE LANGUAGES HERE, for example: python, cpp, java]

Required top-level YAML structure:
- id
- title
- type: booklet
- category
- languages
- goal
- chapters

The booklet must be chapter-wise and navigable:
- chapters
  - id
  - title
  - description
  - sections
    - title
    - lessons
      - title
      - file
      - description
      - status

Planning requirements:
1. Make the booklet comprehensive enough for interview preparation.
2. Include a positive quick revision chapter.
3. Include foundations, data structures, algorithms, graph/tree algorithms,
   dynamic programming, important problems, language-switch drills, and final
   revision.
4. Include more than five sections across the booklet.
5. Include practical language-switch topics, such as Python dict to Java
   HashMap, Python list to C++ vector, Java HashMap to C++ unordered_map.
6. Include important interview problem YAML links grouped by pattern.
7. Use positive wording such as readiness, confidence, revision, mastery,
   practice, and interview preparation.
8. Avoid negative pressure wording such as crash, panic, last chance, or survival.
9. Mark lessons as:
   - available when the file already exists
   - planned when the lesson is a future file
10. Use file paths under knowledge/dsa or another appropriate knowledge folder.

Now generate the booklet YAML.
```

---

## 4. Validation And Cleanup Prompt

Use this after a YAML draft is generated.

```text
Review this AnyLanguageExpressaic YAML.

Return only the corrected valid YAML. Do not wrap it in Markdown fences.

Check:
1. YAML indentation is valid.
2. Code blocks use `|`.
3. Language ids are consistent.
4. Transition keys follow source_to_target.
5. Every language has useful representation.
6. Revision mode is compact and table-friendly.
7. Interview questions are practical and have direct answers.
8. Practical code-thinking switches are present.
9. False friends and traps are included where useful.
10. Custom labels such as notes, prerequisites, categories, related_patterns,
    and tlm_hooks are useful and do not replace required structure.
11. Wording is positive, clear, and learner-friendly.
12. The result teaches thinking shifts, not word-for-word translation.

Here is the YAML:

[PASTE YAML HERE]
```

---

## 5. Minimal Lesson Skeleton

Use this only as a structure reference.

```yaml
id: example_topic
title: Example Topic
category: dsa
level: beginner_to_intermediate
languages:
  - python
  - cpp
  - java
tags:
  - interview
  - language_transition
goal: Help learners understand this topic across languages.

assets:
  main_diagram:
    type: image
    path: assets/dsa/example_topic/main-diagram.png
    alt: Diagram for the topic.

lesson:
  - explain:
      title: Core Idea
      body: >
        Explain the concept in beginner-friendly language.

  - compare_table:
      title: Quick Comparison
      columns:
        - Idea
        - Python
        - C++
        - Java
      rows:
        - ["Main tool", "Python form", "C++ form", "Java form"]

  - language_lens:
      language: python
      title: How Python Wants You To Think
      body: >
        Explain the Python mental model.
      default_instincts:
        - Use the natural built-in first.
      avoid:
        - Do not carry over habits that make Python awkward.

examples:
  - code_compare:
      title: Interview Example
      idea: Explain the shared task.
      python: |
        # Python code here
      cpp: |
        // C++ code here
      java: |
        // Java code here
      note: >
        Explain the thinking difference.

transitions:
  python_to_java:
    title: Python To Java
    mindset_shift:
      - Explain the thinking shift.
    habit_swaps:
      - python: Python habit.
        java: Java habit.
    false_friends:
      - term: Similar-looking idea
        warning: Explain the difference.

interview_questions:
  - question: Practical interview question?
    answer: Direct answer.

revision:
  quick_summary:
    - Compact reminder.
  cheat_table:
    title: Revision Table
    columns:
      - Situation
      - Python
      - C++
      - Java
    rows:
      - ["Common task", "Python reminder", "C++ reminder", "Java reminder"]
  flashcards:
    - question: Recall question?
      answer: Short answer.

notes:
  author_notes:
    - Add diagrams or more examples later.

tlm_hooks:
  possible_tasks:
    - generate_more_interview_questions
    - create_language_transition_drills
    - check_missing_language_coverage
  context: Interview-focused language transition lesson.
```
