import os.path
from io import StringIO
import pytest


@pytest.fixture
def config_file():
    """Creates a config file stream whose location points into the example folder."""

    def create(yaml: str = ""):
        file = StringIO(yaml)
        file.name = os.path.join(os.path.dirname(__file__), "env", "config.yaml")
        return file

    return create
