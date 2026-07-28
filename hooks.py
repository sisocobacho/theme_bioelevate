import logging
import os

from odoo.tools.image import image_process

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    module_path = os.path.dirname(os.path.abspath(__file__))
    favicon_path = os.path.join(module_path, "static", "src", "img", "favicon.ico")

    if os.path.exists(favicon_path):
        return

    for name in ("icon.svg", "logo.svg", "logo.png"):
        source_path = os.path.join(module_path, "static", "src", "img", name)
        if not os.path.exists(source_path):
            continue

        with open(source_path, "rb") as source_file:
            source_data = source_file.read()

        if name.endswith(".svg"):
            try:
                import cairosvg
            except ImportError:
                _logger.warning(
                    "cairosvg is not installed. Favicon generation from SVG requires it. "
                    "Install with: pip install cairosvg"
                )
                continue
            source_data = cairosvg.svg2png(source_data, output_width=256, output_height=256)

        ico_data = image_process(source_data, size=(256, 256), crop="center", output_format="ICO")
        with open(favicon_path, "wb") as favicon_file:
            favicon_file.write(ico_data)
        break
