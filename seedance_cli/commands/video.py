"""Video generation commands."""

import click

from seedance_cli.core.client import get_client
from seedance_cli.core.exceptions import SeedanceError
from seedance_cli.core.output import (
    ASPECT_RATIOS,
    DEFAULT_ASPECT_RATIO,
    DEFAULT_MODEL,
    RESOLUTIONS,
    SEEDANCE_MODELS,
    print_error,
    print_json,
    print_video_result,
)


@click.command()
@click.argument("prompt")
@click.option(
    "-m",
    "--model",
    type=click.Choice(SEEDANCE_MODELS),
    default=DEFAULT_MODEL,
    help="Seedance model version.",
)
@click.option(
    "-a",
    "--aspect-ratio",
    type=click.Choice(ASPECT_RATIOS),
    default=DEFAULT_ASPECT_RATIO,
    help="Aspect ratio of the output.",
)
@click.option(
    "-r",
    "--resolution",
    type=click.Choice(RESOLUTIONS),
    default=None,
    help="Output resolution.",
)
@click.option(
    "--duration",
    type=int,
    default=5,
    help="Duration in seconds.",
)
@click.option("--callback-url", default=None, help="Webhook callback URL.")
@click.option("--json", "output_json", is_flag=True, help="Output raw JSON.")
@click.pass_context
def generate(
    ctx: click.Context,
    prompt: str,
    model: str,
    aspect_ratio: str,
    resolution: str | None,
    duration: int,
    callback_url: str | None,
    output_json: bool,
) -> None:
    """Generate a video from a text prompt.

    PROMPT is a detailed description of what to generate.

    Examples:

      seedance generate "A cinematic scene of a sunset over the ocean"

      seedance generate "A cat playing with yarn" -m doubao-seedance-1-5-pro-251215
    """
    client = get_client(ctx.obj.get("token"))
    try:
        payload: dict[str, object] = {
            "prompt": prompt,
            "model": model,
            "callback_url": callback_url,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
        }
        if resolution:
            payload["resolution"] = resolution

        result = client.generate_video(**payload)  # type: ignore[arg-type]
        if output_json:
            print_json(result)
        else:
            print_video_result(result)
    except SeedanceError as e:
        print_error(e.message)
        raise SystemExit(1) from e


@click.command("image-to-video")
@click.argument("prompt")
@click.option(
    "-i",
    "--image-url",
    "image_urls",
    required=True,
    multiple=True,
    help="Image URL(s) for reference. Can be specified multiple times.",
)
@click.option(
    "-m",
    "--model",
    type=click.Choice(SEEDANCE_MODELS),
    default=DEFAULT_MODEL,
    help="Seedance model version.",
)
@click.option(
    "-a",
    "--aspect-ratio",
    type=click.Choice(ASPECT_RATIOS),
    default=DEFAULT_ASPECT_RATIO,
    help="Aspect ratio of the output.",
)
@click.option(
    "--duration",
    type=int,
    default=5,
    help="Duration in seconds.",
)
@click.option("--callback-url", default=None, help="Webhook callback URL.")
@click.option("--json", "output_json", is_flag=True, help="Output raw JSON.")
@click.pass_context
def image_to_video(
    ctx: click.Context,
    prompt: str,
    image_urls: tuple[str, ...],
    model: str,
    aspect_ratio: str,
    duration: int,
    callback_url: str | None,
    output_json: bool,
) -> None:
    """Generate a video from reference image(s).

    PROMPT describes the desired video. Provide one or more image URLs as reference.

    Examples:

      seedance image-to-video "Animate this scene" -i https://example.com/photo.jpg

      seedance image-to-video "Bring to life" -i img1.jpg -i img2.jpg
    """
    client = get_client(ctx.obj.get("token"))
    try:
        result = client.generate_video(
            prompt=prompt,
            image_urls=list(image_urls),
            model=model,
            aspect_ratio=aspect_ratio,
            duration=duration,
            callback_url=callback_url,
        )
        if output_json:
            print_json(result)
        else:
            print_video_result(result)
    except SeedanceError as e:
        print_error(e.message)
        raise SystemExit(1) from e
