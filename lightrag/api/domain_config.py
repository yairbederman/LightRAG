"""
Loader for domain.md — business-domain configuration.

Reads 4 client-facing fields:
  - Summary Language → SUMMARY_LANGUAGE env var
  - Entity Types → ENTITY_TYPES env var
  - Extraction Examples → overrides PROMPTS["entity_extraction_examples"]
  - User Prompt → returned for query injection

If domain.md does not exist, returns defaults (no-op).
"""

import os
import re


def _find_project_root() -> str:
    """Find project root by locating .env, falling back to CWD."""
    d = os.path.abspath(os.getcwd())
    for _ in range(10):
        if os.path.isfile(os.path.join(d, ".env")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return os.getcwd()


def load_domain_config(
    path: str = "domain.md",
) -> tuple[list[str] | None, str | None]:
    """Parse domain.md and set env vars for domain fields.

    Returns:
        (extraction_examples, user_prompt) — either can be None if not present.
    """
    if not os.path.isabs(path):
        path = os.path.join(_find_project_root(), path)
    if not os.path.exists(path):
        return None, None

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None, None

    # Map (Section, Key) → env var for key-value fields
    env_map = {
        ("Language", "Summary Language"): "SUMMARY_LANGUAGE",
        ("Extraction", "Entity Types"): "ENTITY_TYPES",
    }

    extraction_examples = None
    user_prompt = None

    for section in re.split(r"\n## ", content):
        if not section.strip():
            continue
        lines = section.strip().split("\n")
        heading = lines[0].strip().lstrip("#").strip()
        body = "\n".join(lines[1:]).strip()

        # Fenced code blocks (~~~) → list of strings
        if "~~~" in body:
            blocks = []
            in_block = False
            current: list[str] = []
            for line in body.split("\n"):
                if line.strip() == "~~~":
                    if in_block:
                        blocks.append("\n".join(current))
                        current = []
                    in_block = not in_block
                elif in_block:
                    current.append(line)
            if heading == "Extraction Examples" and blocks:
                extraction_examples = blocks
            continue

        # Key-value pairs (- Key: value) → env vars
        kv_found = False
        for line in body.split("\n"):
            m = re.match(r"^-\s+(.+?):\s+(.+)$", line.strip())
            if m:
                kv_found = True
                key_pair = (heading, m.group(1).strip())
                env_var = env_map.get(key_pair)
                if env_var and env_var not in os.environ:
                    os.environ[env_var] = m.group(2).strip()

        # Freeform text (no key-value pairs) → user prompt
        if not kv_found and heading == "User Prompt" and body:
            user_prompt = body

    return extraction_examples, user_prompt
