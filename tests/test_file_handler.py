from aigen.core.file_handler import FileHandler

def test_file_handler():
    images = FileHandler.expand_images("././examples/image_samples/*")
    assert len(images) == 2
    assert "palm" in images[0]
    assert "landscape" in images[1]
    print(images)
