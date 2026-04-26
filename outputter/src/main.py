# outputter/src/main.py

import sys
import yaml
from pathlib import Path


def load_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def render_section(title, content):
    if not content:
        return ""

    output = f"\n## {title}\n"

    if isinstance(content, list):
        for item in content:
            output += f"- {item}\n"
    elif isinstance(content, dict):
        for key, value in content.items():
            output += f"\n### {key.replace('_', ' ').title()}\n"
            output += render_content(value)
    else:
        output += f"{content}\n"

    return output


def render_content(content):
    if isinstance(content, list):
        return "".join(f"- {item}\n" for item in content)

    if isinstance(content, dict):
        text = ""
        for key, value in content.items():
            text += f"\n#### {key.replace('_', ' ').title()}\n"
            text += render_content(value)
        return text

    return f"{content}\n"


def render_language_read(concept_data, language):
    if language not in concept_data.get("languages", {}):
        raise ValueError(f"Language '{language}' not found.")

    lang_data = concept_data["languages"][language]

    output = ""

    output += f"# {concept_data.get('concept', 'Unknown Concept').title()} in {language.title()}\n"

    output += render_section("Overview", concept_data.get("overview"))
    output += render_section("Core Idea", concept_data.get("core_idea"))

    output += render_section("Mental Model", lang_data.get("mental_model"))
    output += render_section("How To Think", lang_data.get("how_to_think"))
    output += render_section("What To Avoid", lang_data.get("what_to_avoid"))
    output += render_section("Responsibilities", lang_data.get("responsibilities"))
    output += render_section("Syntax", lang_data.get("syntax"))
    output += render_section("Operations", lang_data.get("operations"))
    output += render_section("Traps", lang_data.get("traps"))
    output += render_section("Depth", lang_data.get("depth"))

    return output


def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python main.py <yaml_file> <language>")
        print()
        print("Example:")
        print("  python main.py knowledge/loops.yaml python")
        sys.exit(1)

    yaml_file = Path(sys.argv[1])
    language = sys.argv[2].lower()

    concept_data = load_yaml(yaml_file)
    output = render_language_read(concept_data, language)

    print(output)


if __name__ == "__main__":
    main()