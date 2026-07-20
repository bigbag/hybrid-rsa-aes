import runpy
from pathlib import Path


def test_basic_usage_example_runs() -> None:
    namespace = runpy.run_path(Path("examples/basic_usage.py"))
    assert namespace["decrypted"] == {"message": "authenticated hybrid encryption", "version": 1}
