import warnings


def test_import():
    import funlanzou  # noqa: F401


def test_import_legacy_lanzou_shim():
    """`lanzou` is a deprecated compat shim forwarding to `funlanzou` (see
    funlanzou/../lanzou/__init__.py). It should still import cleanly, but
    emits a DeprecationWarning."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        import lanzou  # noqa: F401
