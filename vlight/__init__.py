"""vlight package initialization."""

try:
    from pkg_resources import get_distribution, DistributionNotFound
    __version__ = get_distribution(__name__).version
except Exception:
    __version__ = "0.4.4"

__all__ = ["__version__"]
