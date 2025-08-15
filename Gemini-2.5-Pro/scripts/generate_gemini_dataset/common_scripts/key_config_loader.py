from __future__ import annotations
import os
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass(frozen=True)
class ProjectKey:
    email: str
    project: str
    api_key: str

    @property
    def name(self) -> str:
        return f"{self.email}:{self.project}"

def load_project_keys(config_path: str | Path | None = None) -> List[ProjectKey]:
    """
    Loads keys from config/keys.json with structure:
    {
      "keys": [
        {
          "email": "alice@example.com",
          "projects": [
            {"name": "proj-1", "api_key": "..."},
            {"name": "proj-2", "api_key": "..."}
          ]
        },
        ...
      ]
    }
    Fallback: GOOGLE_GENAI_API_KEYS="k1,k2,..." (email="env", project="key-i").
    """
    if config_path is None:
        config_path = Path(__file__).resolve().parent / "config" / "keys.json"
    else:
        config_path = Path(config_path)

    if config_path.exists():
        data = json.loads(config_path.read_text(encoding="utf-8"))
        out: List[ProjectKey] = []
        for entry in data.get("keys", []):
            email = (entry.get("email") or "").strip()
            for proj in entry.get("projects", []):
                name = (proj.get("name") or "").strip()
                api_key = (proj.get("api_key") or "").strip()
                if email and name and api_key:
                    out.append(ProjectKey(email=email, project=name, api_key=api_key))
        if not out:
            raise ValueError("keys.json present but no valid keys found.")
        return out

    # env_list = [k.strip() for k in os.getenv("GOOGLE_GENAI_API_KEYS", "").split(",") if k.strip()]
    # if env_list:
    #     return [ProjectKey(email="env", project=f"key-{i+1}", api_key=k) for i, k in enumerate(env_list)]

    raise FileNotFoundError("No keys found. Provide config/keys.json or set GOOGLE_GENAI_API_KEYS.")
