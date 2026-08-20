from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


@dataclass
class ImageProcessingResult:

    valid: bool

    image_url: Optional[str]

    error: Optional[str] = None


class ImageProcessor:
    """
    Validates optional image input.

    Image failure must not stop text-based classification.
    """

    def validate(
        self,
        image_url: Optional[str],
    ) -> ImageProcessingResult:

        if not image_url:

            return ImageProcessingResult(
                valid=False,
                image_url=None,
                error="No image supplied.",
            )

        try:

            parsed = urlparse(
                image_url
            )

            if parsed.scheme not in {
                "http",
                "https",
            }:

                return ImageProcessingResult(
                    valid=False,
                    image_url=image_url,
                    error=(
                        "Unsupported image "
                        "URL scheme."
                    ),
                )

            return ImageProcessingResult(
                valid=True,
                image_url=image_url,
            )

        except Exception as exc:

            return ImageProcessingResult(
                valid=False,
                image_url=image_url,
                error=str(exc),
            )