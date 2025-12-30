# src/apathetic_testing/namespace.py
"""Shared Apathetic Testing namespace implementation.

This namespace class provides a structure to minimize global namespace pollution
when the library is embedded in a stitched script.
"""

from __future__ import annotations

from .constants import (
    ApatheticTest_Internal_Constants,
)
from .fixtures import (
    ApatheticTest_Internal_Fixtures,
)
from .logging import (
    ApatheticTest_Internal_Logging,
)
from .mock import (
    ApatheticTest_Internal_Mock,
)
from .patch import (
    ApatheticTest_Internal_Patch,
)
from .pytest import (
    ApatheticTest_Internal_Pytest,
)
from .runtime import (
    ApatheticTest_Internal_Runtime,
)


# --- Apathetic Testing Namespace -------------------------------------------


class apathetic_testing(  # noqa: N801
    ApatheticTest_Internal_Constants,
    ApatheticTest_Internal_Runtime,
    ApatheticTest_Internal_Logging,
    ApatheticTest_Internal_Fixtures,
    ApatheticTest_Internal_Pytest,
    ApatheticTest_Internal_Mock,
    ApatheticTest_Internal_Patch,
):
    """Namespace for apathetic testing functionality.

    All utility functionality is accessed via this namespace class to minimize
    global namespace pollution when the library is embedded in a stitched script.
    """


# Note: All exports are handled in __init__.py
# - For library builds (package/stitched): __init__.py is included, exports happen
# - For embedded builds: __init__.py is excluded, no exports (only class available)
