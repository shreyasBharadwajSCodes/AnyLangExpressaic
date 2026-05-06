# YAML Generation Prompt For Vis2

Use this prompt to generate a useful Vis2 YAML lesson file. Replace the bracketed
parts before sending it to an AI tool.

```text
You are creating a Vis2 YAML concept file for AnyLanguageExpressaic.

Topic:
[write the concept, for example: queues, recursion, hash maps, async programming]

Audience:
[write the audience, for example: beginners moving from Python to C++, Java developers learning Python, interview revision]

Languages:
[list languages, for example: python, cpp, java]

Main transition paths to support:
[for example: python_to_cpp, cpp_to_python, java_to_python]

Requirements:
1. Output only valid YAML. Do not wrap it in Markdown fences.
2. Use this top-level structure exactly:
   id, title, category, level, languages, tags, goal, assets, lesson, examples, transitions, revision, tlm_hooks.
3. The lesson must teach how to think in each language, not only syntax.
4. Include language_lens blocks for every language.
5. Include at least two compare_table or code_compare blocks.
6. Include at least one example that shows a common mistake or edge case.
7. Include transition paths for every requested source_to_target pair.
8. In each transition path include:
   - mindset_shift
   - habit_swaps
   - false_friends
9. In habit_swaps, use language names as keys, not old/new.
   Example:
   - python: Use a list directly for simple ordered data.
     cpp: Start with vector, but understand allocation and invalidation.
10. Include revision.quick_summary with compact language-specific bullets.
11. Include revision.cheat_table with language columns named like "Python instinct", "C++ instinct", and "Java instinct".
12. Include revision.flashcards with recall questions that test mental models and transitions.
13. Keep examples short enough to fit in a learning UI.
14. Prefer practical, accurate teaching over exhaustive detail.
15. Use image asset placeholders under assets when an image would help, even if the file does not exist yet.

Quality bar:
- The YAML should help a new reader learn the concept as a lesson.
- The YAML should help a revising reader use tables and short notes.
- The YAML should help a language-switching reader replace habits from one language with habits from another.
- Do not say two languages are equivalent unless the mental model and tradeoffs are also explained.

Now generate the YAML.
```

## Optional Follow-Up Prompt

Use this after a first draft to improve the result:

```text
Review the YAML you just generated for Vis2.

Improve it using these checks:
1. Is every language represented by a language_lens?
2. Does every transition path teach habit changes, not just syntax translation?
3. Are there false friends where names look similar but behavior differs?
4. Are examples short, runnable-looking, and comparable?
5. Does revision mode contain useful compact reminders?
6. Are image placeholders meaningful?
7. Is the YAML valid and consistently indented?

Return the improved YAML only.
```
