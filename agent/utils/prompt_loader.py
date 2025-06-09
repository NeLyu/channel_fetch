from pathlib import Path

def load_prompt_template(name):
    path = Path(__file__).parent.parent.parent /"prompts" / f"{name}.txt"
    return path.read_text(encoding="utf-8")