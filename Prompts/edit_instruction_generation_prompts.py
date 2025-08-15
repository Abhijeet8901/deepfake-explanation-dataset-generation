GEMINI_PROMPTS = {
    "gemini_prompt_mark_1": """
You are a photo-manipulation planner.
Given one real image, propose 5 varied manipulations that are visually obvious (not subtle), photorealistic, and different from these excluded categories:
1) ❌ Changing human facial expressions or emotions
2) ❌ Minor pose tweaks to humans
3) ❌ Rewriting/adding any text, signage, posters, labels

Use distinct categories across the five (do not repeat): object/animal insertion or removal, background/scene swap, weather/season/time change, reflections/shadows trick, duplication/scale, occluder addition, camera/framing/DoF, physics event (smoke/fire/sparks/water), style/material change (non-text).
Ground each edit to specific regions/objects visible in the image. Keep it SFW and non-targeting.

Output contract (must follow exactly):
1) Return only a valid JSON object with a single key "manipulations" whose value is an array of exactly five strings.
2) No extra text, explanations, labels, or markdown code fences.
3) The first character of your reply must be { and the last must be }.
4) Each string is one sentence ≤ 30 words, mentions realism cues when relevant (e.g., “cast soft shadow”, “match window reflections”), and comes from a different category.

Image: [attach the real image here]

Required JSON shape:
{
  "manipulations": [
    "…one sentence (≤30 words) describing a grounded, photorealistic manipulation…",
    "…one sentence (≤30 words) from a different category…",
    "…",
    "…",
    "…"
  ]
}

Mention realism cues when relevant (e.g., “cast soft shadow on wall,” “match window reflections,” “respect depth of field”
""",
  "gemini_prompt_mark_2": """
You are a photo-manipulation planner.
Given one real image, propose 5 varied manipulations that are visually obvious and pronounced(not subtle), photorealistic, and different from these excluded categories:
1) ❌ Changing human facial expressions or emotions
2) ❌ Pose tweaks to humans
3) ❌ Rewriting/adding any text, signage, posters, labels

Choose five distinct manipulation types (no repeats) from this whitelist exactly as written for keys:
1) insert_object
2) remove_object
3) replace_background
4) weather_time_change
5) reflection_shadow_edit
6) duplication_scale
7) occluder_addition
8) camera_composition
9) physics_event
10) style_material_change (non-text)

Each value must be one sentence (≤ 30 words) that:
1) grounds the edit to concrete regions/objects in the image (use words like “left window,” “front shelf,” “ceiling corner”),
2) mentions realism cues when relevant (e.g., “cast soft shadow,” “match window reflections,” “respect depth of field”),
3) corresponds to an OBVIOUS and PRONOUNCED edit. 
3) is SFW and non-targeting.

Output contract (must follow exactly):
1) Return only a valid JSON object with a single top-level key "manipulations" whose value is another object containing exactly five key–value pairs as defined above.
2) No extra text, explanations, or markdown code fences.
3) The first character must be { and the last must be }.
4) Each string is one sentence ≤ 30 words, mentions realism cues when relevant (e.g., “cast soft shadow”, “match window reflections”), and comes from a different category.

Image: [attach the real image here]

Required JSON shape (schema, not an example):
{
"manipulations": {
"<one of the allowed types>": "<one sentence instruction>",
"<another allowed type>": "<one sentence instruction>",
"<another allowed type>": "<one sentence instruction>",
"<another allowed type>": "<one sentence instruction>",
"<another allowed type>": "<one sentence instruction>"
}
}
"""
}