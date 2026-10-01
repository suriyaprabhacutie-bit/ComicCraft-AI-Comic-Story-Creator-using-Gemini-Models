from app.schemas import ComicPanel, PanelStory


def build_comic_layout(
    stories: list[PanelStory],
    image_paths: list[str],
) -> list[ComicPanel]:

    if len(stories) != len(image_paths):
        raise ValueError(
            "Each story panel must have exactly one image."
        )

    layout = []

    for story, image_path in zip(
        stories,
        image_paths,
    ):
        panel = ComicPanel(
            **story.model_dump(),
            image_path=image_path,
        )

        layout.append(panel)

    return layout