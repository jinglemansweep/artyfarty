import logging
import os
import random
import sys
from pprint import pprint
from .config import settings

from .inputs.openwebif import get_current_programme, FetchProgramException
from .generators.replicate import generate_image
from .utils import (
    build_output_filename,
    get_file_extension,
    download_file,
    write_metadata_file,
)

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

try:
    epg_title, epg_summary = get_current_programme()

    model_name = settings.replicate.model
    model_version = settings.replicate.model_version

    prompt = epg_title
    prefix = (
        random.choice(settings.prompts.prefixes) if settings.prompts.prefixes else ""
    )
    suffix = (
        random.choice(settings.prompts.suffixes) if settings.prompts.suffixes else ""
    )
    negative = settings.prompts.negative or ""
    prompt_full = f"{prefix} {prompt} {suffix}"

    model_inputs = dict(
        prompt=prompt_full,
        negative_prompt=negative,
        width=settings["replicate.output.width"],
        height=settings["replicate.output.height"],
    )

    image_url = generate_image(model_name, model_version, model_inputs)
    file = build_output_filename(
        prompt_full, settings.output.timestamp, settings.output.prefix
    )
    ext = get_file_extension(image_url)
    output_filename = os.path.join(settings.output.path, f"{file}{ext}")
    metadata_filename = os.path.join(settings.output.path, f"{file}.yml")
    metadata = dict(model=model_name, version=model_version, inputs=model_inputs)
    logger.info(
        f"render image_url={image_url} metadata={metadata} output_filename={output_filename} metadata_filename={metadata_filename}"
    )
    download_file(image_url, output_filename)
    write_metadata_file(metadata, metadata_filename)
except Exception as e:
    logger.error("Error", exc_info=e)
    sys.exit(2)
