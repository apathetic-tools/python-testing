# src/apathetic_testing/constants.py
"""Constants for Apathetic Testing."""

from __future__ import annotations


class ApatheticTest_Internal_Constants:  # noqa: N801  # pyright: ignore[reportUnusedClass]
    """Constants for apathetic testing functionality.

    This class contains all constant values used by apathetic_testing.
    It's kept separate for organizational purposes.
    """

    ROOT_LOGGER_KEY: str = ""
    """Key used to retrieve the root logger via logging.getLogger("").

    The root logger is retrieved using an empty string as the logger name.
    """
