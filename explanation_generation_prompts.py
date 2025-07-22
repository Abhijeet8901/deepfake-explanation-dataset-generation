from string import Template

PROMPTS = {
    "gemini_prompt_mark_1": Template("""
        You are an expert image analyst, a "Digital Detective." Your specialty is spotting image manipulations and explaining them in a way a five-year-old can understand, without any technical jargon. You also know how to reverse the editing process.
        Your task is to analyze two images and the instructions used to create the second one from the first. You will then produce a JSON output that critiques the edit and provides instructions to undo it.
        Here are the inputs I will provide:
        [Original Image]: The image before any changes were made.
        [Edited Image]: The image after the edits were applied.
        [Edit Instructions JSON]: The JSON object explaining the edits that were performed.
        Your Goal:
        Based on the inputs, you must generate a single JSON object as your output. This JSON object must strictly follow the structure below.
        Required JSON Output Structure:

        {
          "overall_analysis": {
            "title": "Why the Picture Looks a Bit Funny",
            "explanation": "A simple, overall explanation of why the edited image looks fake, using an analogy. For example, 'The new parts of the picture look like stickers that were placed on top of a drawing, they don't quite blend in.'"
          },
          "manipulated_entities": [
            {
              "entity": "The specific thing that was changed (e.g., 'the person's posture', 'the cat's tail').",
              "reason_it_looks_fake": "A simple, analogy-based explanation for why this specific part looks fake. For example, 'The person is standing too straight, like a toy soldier instead of a real person.' or 'The new shadow doesn't match the other shadows, like a second sun appeared in the sky.'"
            }
          ],
          "reverse_edit_instructions": {
            "Effect": "Describe the effect of reversing the edit. e.g., 'the person appears as they did originally'",
            "Change Target": "The same target from the input instructions. e.g., 'human'",
            "Explanation": [
              "The entity to be changed back. e.g., 'the badminton player'",
              "The specific instruction to revert the change. e.g., 'adjust their posture back to the original slouched stance and remove the confident smile, returning their expression to neutral.'"
            ]
          }
        }

        How to Perform Your Task: Step-by-Step Instructions
        Analyze the Images: Carefully compare the [Original Image] and the [Edited Image]. Use the [Edit Instructions JSON] to understand what was supposed to be changed.
        Find the Flaws: Identify the specific parts of the [Edited Image] that look unnatural, out of place, or fake. Pay attention to shadows, lighting, edges, textures, and natural human poses or expressions.
        Fill the overall_analysis:
        Write a short, simple summary of why the edit isn't perfect.
        Crucially, use an analogy. Think like you're explaining it to a child. Avoid words like "artifacts," "pixels," or "rendering."
        Fill the manipulated_entities list:
        For each major flaw you found, create one object in the list.
        entity: Clearly name the thing that was changed (e.g., "the player's smile," "the shadow on the ground").
        reason_it_looks_fake: Explain why it looks fake with its own simple analogy. Be specific. If a smile is fake, don't just say it's fake. Say, "The smile looks like a sticker because it doesn't make the person's eyes crinkle up like a real smile does."
        Create the reverse_edit_instructions:
        This is the most important logical step. You must invent a new set of instructions that would turn the [Edited Image] back into the [Original Image].
        Look at the input Explanation and create its direct opposite.
        If the original edit was adjust posture to be upright, the reverse instruction should be adjust posture back to its original, more relaxed state.
        If the original edit was add a confident smile, the reverse instruction should be remove the smile and return the mouth to its original neutral expression.
        Ensure the structure (Effect, Change Target, Explanation) exactly matches the format you were given.
        Your final output must be ONLY the JSON object, with no introductory text or conversation.


        Here are my inputs:

        **[Original Image]:**
        The FIRST image I uploaded

        **[Edited Image]:**
        The SECOND image I uploaded

        **[Edit Instructions JSON]:**
        ```json
        $effect_json
        """
    ),

    "gemini_prompt_mark_2": Template("""
        You are an expert image analyst, a "Digital Detective." Your specialty is spotting image manipulations and explaining them in a way a five-year-old can understand, without any technical jargon. You also know how to reverse the editing process.
        Your task is to analyze an edited image and produce a structured JSON output. You will be given an original image, an edited image, and the instructions used for the edit.
        Your analysis must be objective and produce high-quality, self-contained data.
        Here are the inputs I will provide:
        [Original Image]: The image before any changes were made.
        [Edited Image]: The image after the edits were applied.
        [Original Edit Instructions] (JSON format): The JSON object explaining the edits that were performed.

        Your Mission:
        Produce a single, valid JSON object as output. Do not include any text or explanations outside of this JSON.
        Guiding Principles & Rules:
        Master Rule: Trust the Visual Evidence Above All Else
        Your primary source of truth is the visual difference between the [Original Image] and the [Edited Image]. The [Original Edit Instructions] are only a clue and may be inaccurate or misleading. If the text instructions contradict what you see in the images, your entire output—both the analysis and the reverse instructions—MUST be based on the visual evidence alone

        Part 1: Manipulation Analysis (manipulation_analysis)
        Independent Analysis: Your entire explanation must be based on analyzing the [Edited Image] by itself. The [Original Image] serves only as a behind-the-scenes reference for you to identify what was changed. You must never mention, compare to, or allude to the original image in your explanation. Your analysis should read as if you have never seen the original.
        High-Level Entity Identification: Identify the primary subject that was manipulated. Use the first element of the Explanation array in the [Original Edit Instructions] as a clue to find this subject. However, your final manipulated_entity must describe the subject you actually see being manipulated in the images. Your final manipulated_entity should describe the subject at a high level (e.g., "the badminton player," "the red car," "the storefront sign"), not a specific sub-part (e.g., "the player's smile," "the car's front tire").
        Explain Why It Looks Out of Place: Your goal is to explain why the manipulated part doesn't fit with the rest of the picture. Find a simple, common-sense reason it looks fake.
        To do this, look for a mismatch. Here are some types of mismatches to look for:
        Does it follow the rules of the world? (e.g., Do people leave footprints in sand? Do things cast shadows? Do reflections look right?)
        Does it make sense for the situation? (e.g., Are they wearing the right clothes for the weather? Does their expression match the action?)
        Does it look like it belongs? (e.g., Does one part look like a cartoon while the rest looks real? Does one part look brand new while everything else is old and dusty?)
        You only need to find one good reason. Pick the clearest and simplest one.
        Explain your reason simply, as if talking to a child. You can use an analogy (like comparing it to a sticker or a toy) if it helps, but a clear, simple observation is also perfect.
        GOOD EXAMPLE (Rules of the World): "A person is standing on a sandy beach, but their feet aren't sinking into the sand at all and they don't have any footprints behind them. It looks like they are floating on top of the sand, which doesn't happen in real life."
        GOOD EXAMPLE (Situation): "A man is wearing a big, thick winter coat and a wool hat, but he is standing on a sunny beach with palm trees. This doesn't make sense because people wear swimsuits at the beach, not winter clothes."
        GOOD EXAMPLE (Visuals): "There is a fluffy, cartoon-style cat sitting in a field of real grass. The cat looks like it came from a TV show, while the grass looks like a real photograph. The two styles don't match."
        BAD EXAMPLE: "The cat looks fake." (This doesn't explain why it looks fake).

        Part 2: Inverse Instructions (inverse_edit_instructions)
        Goal-Oriented Instructions: Look at the [Edited Image] and the [Original Image]. Your goal is to write a clear, actionable command for another AI model that describes the visual transformation required to make the [Edited Image] look like the [Original Image].
        Visual, Not Textual, Reversal: Do not simply rephrase or invert the text from the [Original Edit Instructions]. Base your new instruction on the actual visual changes you observe between the two images.
        Self-Contained Command: The generated instruction must be standalone. It should not mention the original image file or the original instructions in its text. The command should be understandable on its own.
        Mirror the Format: This new JSON object must follow the exact same structure as the input instructions: {"Effect": "...", "Change Target": "...", "Explanation": ["...", "..."]}.
        Required Output Format:
        Your entire output must be the following JSON structure.

        {
          "manipulation_analysis": [
            {
              "manipulated_entity": "The high-level entity that was changed.",
              "explanation": "Your simple, analogy-based explanation of why the entity looks unnatural in the edited image."
            }
          ],
          "inverse_edit_instructions": {
            "Effect": "A brief description of the result of reverting the edit.",
            "Change Target": "The category of the target (e.g., 'human', 'text', 'object').",
            "Explanation": [
              "The specific entity to be changed back.",
              "The precise, self-contained instruction for an AI to change the edited image back to its original state."
            ]
          }
        }

        Here are my inputs:

        **[Original Image]:**
        The FIRST image I uploaded

        **[Edited Image]:**
        The SECOND image I uploaded

        **[Edit Instructions JSON]:**
        ```json
        $effect_json
        """
    ),
    "gemini_prompt_mark_3": Template("""
        You are an expert image analyst, a "Digital Detective." Your specialty is spotting image manipulations and explaining them in a way a five-year-old can understand, without any technical jargon. You also know how to reverse the editing process.
        Your task is to analyze an edited image and produce a structured JSON output. You will be given an original image, an edited image, and the instructions used for the edit.
        Your analysis must be objective and produce high-quality, self-contained data.
        Here are the inputs I will provide:
        [Original Image]: The image before any changes were made.
        [Edited Image]: The image after the edits were applied.
        [Original Edit Instructions] (JSON format): The JSON object explaining the edits that were performed.

        Your Mission:
        Produce a single, valid JSON object as output. Do not include any text or explanations outside of this JSON.
        Guiding Principles & Rules:
        Master Rule: Trust the Visual Evidence Above All Else
        Your primary source of truth is the visual difference between the [Original Image] and the [Edited Image]. The [Original Edit Instructions] are only a clue and may be inaccurate or misleading. If the text instructions contradict what you see in the images, your entire output—all three parts—MUST be based on the visual evidence alone.

        Part 1: Manipulation Analysis (manipulation_analysis)
        Independent Analysis: Your entire explanation must be based on analyzing the [Edited Image] by itself. The [Original Image] serves only as a behind-the-scenes reference for you to identify what was changed. You must never mention, compare to, or allude to the original image in your explanation. Your analysis should read as if you have never seen the original.
        High-Level Entity Identification: Identify the primary subject that was manipulated. Use the first element of the Explanation array in the [Original Edit Instructions] as a clue to find this subject. However, your final manipulated_entity must describe the subject you actually see being manipulated in the images. Your final manipulated_entity should describe the subject at a high level (e.g., "the badminton player," "the red car," "the storefront sign"), not a specific sub-part (e.g., "the player's smile," "the car's front tire").
        Explain Why It Looks Out of Place: Your goal is to explain why the manipulated part doesn't fit with the rest of the picture. Find a simple, common-sense reason it looks fake.
        To do this, look for a mismatch. Here are some types of mismatches to look for:
        Does it follow the rules of the world? (e.g., Do people leave footprints in sand? Do things cast shadows? Do reflections look right?)
        Does it make sense for the situation? (e.g., Are they wearing the right clothes for the weather? Does their expression match the action?)
        Does it look like it belongs? (e.g., Does one part look like a cartoon while the rest looks real? Does one part look brand new while everything else is old and dusty?)
        You only need to find one good reason. Pick the clearest and simplest one.
        Explain your reason simply, as if talking to a child. You can use an analogy (like comparing it to a sticker or a toy) if it helps, but a clear, simple observation is also perfect.
        GOOD EXAMPLE (Rules of the World): "A person is standing on a sandy beach, but their feet aren't sinking into the sand at all and they don't have any footprints behind them. It looks like they are floating on top of the sand, which doesn't happen in real life."
        GOOD EXAMPLE (Situation): "A man is wearing a big, thick winter coat and a wool hat, but he is standing on a sunny beach with palm trees. This doesn't make sense because people wear swimsuits at the beach, not winter clothes."
        GOOD EXAMPLE (Visuals): "There is a fluffy, cartoon-style cat sitting in a field of real grass. The cat looks like it came from a TV show, while the grass looks like a real photograph. The two styles don't match."
        BAD EXAMPLE: "The cat looks fake." (This doesn't explain why it looks fake).

        Part 2: Inferred Original State (inferred_original_state)
        Describe the "Correct" Version: Based on the mismatch you found in Part 1, now describe what the scene would likely look like if it were natural and believable.
        This is a Description, Not a Command: You are describing a state, not telling someone what to do. Your description should logically "fix" the problem you identified.
        Example: If you found that a person's smiling face didn't match their focused body during a sport, the inferred state would describe a focused face. If you found a winter coat on a beach, the inferred state would describe beach-appropriate clothing.

        Part 3: Inverse Instructions (inverse_edit_instructions)
        Goal-Oriented Instructions: Look at the [Edited Image] and the [Original Image]. Your goal is to write a clear, actionable command for another AI model that describes the visual transformation required to make the [Edited Image] look like the [Original Image].
        Visual, Not Textual, Reversal: Do not simply rephrase or invert the text from the [Original Edit Instructions]. Base your new instruction on the actual visual changes you observe between the two images.
        Self-Contained Command: The generated instruction must be standalone. It should not mention the original image file or the original instructions in its text. The command should be understandable on its own.
        Mirror the Format: This new JSON object must follow the exact same structure as the input instructions: {"Effect": "...", "Change Target": "...", "Explanation": ["...", "..."]}.
        Required Output Format:
        Your entire output must be the following JSON structure.

        {
          "manipulation_analysis": [
            {
              "manipulated_entity": "The high-level entity that was changed.",
              "explanation": "Your simple, analogy-based explanation of why the entity looks unnatural in the edited image."
            }
          ],
          "inferred_original_state": {
            "description": "A simple, common-sense description of what the manipulated entity likely looked like in a natural, unedited state."
          },
          "inverse_edit_instructions": {
            "Effect": "A brief description of the result of reverting the edit.",
            "Change Target": "The category of the target (e.g., 'human', 'text', 'object').",
            "Explanation": [
              "The specific entity to be changed back.",
              "The precise, self-contained instruction for an AI to change the edited image back to its original state."
            ]
          }
        }

        Here are my inputs:

        **[Original Image]:**
        The FIRST image I uploaded

        **[Edited Image]:**
        The SECOND image I uploaded

        **[Edit Instructions JSON]:**
        ```json
        $effect_json
        """
    )

}