"""Manta Bot package.

This module intentionally contains no top-level execution. Previous versions
attempted to construct launch `Node` objects at import time which caused
exceptions (e.g. when `get_package_share_directory` is not available during a
plain import). Keep module initialization minimal to allow importing the
package for runtime entry points.
"""

__all__ = []