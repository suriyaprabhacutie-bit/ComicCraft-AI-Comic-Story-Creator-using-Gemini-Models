import json

from google import genai
from google.genai import types

from app.config import settings
from app.schemas import PanelOutline, PanelStory, PromptRequest


def extract_json(text: str):
    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    start = text.find("[")
    end = text.rfind("]")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    return json.loads(text)


def demo_story(
    outlines: list[PanelOutline],
    request: PromptRequest,
):
    stories = []

    for outline in outlines:
        stories.append(
            PanelStory(
                panel_number=outline.panel_number,
                title=outline.title,
                scene_description=outline.scene_description,
                image_prompt=outline.image_prompt,
                caption=f"{outline.title}: {request.character_name}'s adventure continues.",
                narration=(
                    f"{request.character_name} moves forward through "
                    f"the adventure in {request.setting}."
                ),
            )
        )

    return stories


def generate_story(
    outlines: list[PanelOutline],
    request: PromptRequest,
):
    if not settings.gemini_api_key:
        return demo_story(outlines, request)

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    outline_text = json.dumps(
        [
            outline.model_dump()
            for outline in outlines
        ],
        indent=2,
    )

    prompt = f"""
Create the detailed story for this 5-panel comic.

Original user story:
{request.story_prompt}

Character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Comic outline:
{outline_text}

For every panel return:

panel_number
title
scene_description
image_prompt
caption
narration

Keep the story connected from panel 1 to panel 5.

Return ONLY a valid JSON array.
Do not add markdown.
"""

    response = client.models.generate_content(
        model=settings.gemini_story_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            response_mime_type="application/json",
        ),
    )

    data = extract_json(response.text)

    return [
        PanelStory(**item)
        for item in data
    ]