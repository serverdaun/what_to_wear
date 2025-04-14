import yaml
from pathlib import Path

def load_prompt(path: str, prompt_name: str, **kwargs) -> str:
    """
    Load a specific named prompt from a YAML file and replace placeholders.
    
    Args:
        path (str): Path to YAML file.
        prompt_name (str): Key of the prompt inside the YAML.
        **kwargs: Replacement values for placeholders.
    
    Returns:
        str: Final formatted prompt string.
    """
    with open(path, "r", encoding="utf-8") as f:
        prompts = yaml.safe_load(f)

    prompt_template = prompts[prompt_name]
    return prompt_template.format(**kwargs)
