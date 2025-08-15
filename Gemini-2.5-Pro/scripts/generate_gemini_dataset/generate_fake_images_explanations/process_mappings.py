import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image

from api_call import get_explanation_async
from logging_utils import Logger, LoggingStats
from wave_scheduler import WaveScheduler, SchedulerConfig, KeyState
from key_config_loader import load_project_keys

def _load_effect_for_entry(entry: Dict[str, Any], prompt_template: str) -> Dict[str, Any]:
    effects_json = json.loads(Path(entry["edit_suggestion_path"]).read_text(encoding="utf-8"))
    # Support both your older "Effects" list or a mapping by index
    if isinstance(effects_json, dict) and "Effects" in effects_json:
        effects = effects_json["Effects"]
    else:
        effects = effects_json
    idx = entry["image_index"]
    effect = effects[idx]
    # Your special handling for prompt >= 4
    try:
        if int(prompt_template.split("_")[-1]) >= 4:
            effect = {"Explanation": effect["Explanation"]}
    except Exception:
        pass
    return effect

def _build_work_items(mappings: List[Dict[str, Any]], prompt_template: str) -> List[Dict[str, Any]]:
    items = []
    for entry in mappings:
        out = Path(entry["output_explanation_path"]) / entry["output_explanation_name"]
        if out.exists():
            # skip already-done
            continue
        items.append({
            "generated_image_path": entry["generated_image_path"],
            "real_image_path": entry["real_image_path"],
            "edit_suggestion_path": entry["edit_suggestion_path"],
            "image_index": entry["image_index"],
            "output_path": str(out),
            "prompt_template": prompt_template,
            "generation_model": entry["generation_model"],
            "edit_suggestion_model": entry["edit_suggestion_model"],
            "dataset": entry["dataset"],
            "image_name": entry["image_name"],
        })
    return items

def _ensure_dir(path_str: str):
    Path(path_str).parent.mkdir(parents=True, exist_ok=True)

def make_worker():
    async def worker(client, item: Dict[str, Any]):
        # load images and effect
        gen_img = Image.open(item["generated_image_path"]).convert("RGB")
        real_img = Image.open(item["real_image_path"]).convert("RGB")
        # Build effect based on your format
        entry = {
            "edit_suggestion_path": item["edit_suggestion_path"],
            "image_index": item["image_index"],
        }
        effect = _load_effect_for_entry(entry, item["prompt_template"])

        # call API
        explanation = await get_explanation_async(
            client=client,
            gen_img=gen_img,
            real_img=real_img,
            effect=effect,
            prompt_name=item["prompt_template"],
        )                

        # save
        out_path = Path(item["output_path"])
        _ensure_dir(str(out_path))
        out_path.write_text(json.dumps(explanation, ensure_ascii=False, indent=2), encoding="utf-8")
    return worker

async def run_pipeline(
    mappings: List[Dict[str, Any]],
    logger: Logger,
    logging_stats: LoggingStats,
    prompt_template: str,
    rpm_per_key: int,
    rpd_per_key: int,
    max_concurrent: int,
    wave_seconds: int = 60,
    align_to_minute: bool = True,
    max_retries_per_item: int = 2,
    keys_config_path: Optional[str] = None,
):
    # Build items
    work_items = _build_work_items(mappings, prompt_template)
    if not work_items:
        logger.log_success("No work to do; all outputs exist.")
        return

    # Load keys (email -> projects -> api_key)
    projs = load_project_keys(keys_config_path)
    key_states = [KeyState(email=p.email, project=p.project, api_key=p.api_key) for p in projs]
    
    # Scheduler config
    cfg = SchedulerConfig(
        rpm_per_key=rpm_per_key,
        rpd_per_key=rpd_per_key,
        max_concurrent=max_concurrent,     # interpreted as keys per batch
        align_to_minute=align_to_minute,
        max_retries_per_item=max_retries_per_item,
        minute_seconds=60,
    )

    # Run
    worker = make_worker()
    sched = WaveScheduler(keys=key_states, cfg=cfg)
    await sched.run(work_items, worker=worker, logger=logger, logging_stats=logging_stats)