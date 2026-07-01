"""Top-level modules for RobotCode / ``Library    GeminiLibrary``."""

import importlib


def test_import_gemini_library_module():
    mod = importlib.import_module("GeminiLibrary")
    assert mod.GeminiLibrary.__name__ == "GeminiLibrary"


def test_import_browser_gemini_library_module():
    mod = importlib.import_module("BrowserGeminiLibrary")
    assert mod.BrowserGeminiLibrary.__name__ == "BrowserGeminiLibrary"
    assert issubclass(mod.BrowserGeminiLibrary, importlib.import_module("GeminiLibrary").GeminiLibrary)


def test_robot_entry_points_use_top_level_shims():
    from importlib.metadata import entry_points

    libs = {ep.name: ep.value for ep in entry_points(group="robotframework.libraries")}
    assert libs["GeminiLibrary"] == "GeminiLibrary:GeminiLibrary"
    assert libs["BrowserGeminiLibrary"] == "BrowserGeminiLibrary:BrowserGeminiLibrary"
