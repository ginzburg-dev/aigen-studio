import pytest

from aigen.common.file_handler import FileHandler

pytestmark = pytest.mark.unit


def test_file_handler():
    images = FileHandler.search_images("././examples/article_generator/article_example/images/")
    assert len(images) == 2
    print(images)
