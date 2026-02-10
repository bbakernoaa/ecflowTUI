from ectop import Ectop


def test_app_instantiation():
    """Basic test to check if the App can be instantiated."""
    app = Ectop()
    assert app is not None
