import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_imports():
    import flowmaker
    import main


def test_main_functions_are_callable():
    import main
    assert callable(main.no_args_function)
    assert callable(main.arg_given_function)
