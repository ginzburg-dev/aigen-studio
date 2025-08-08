from aigen.core.file_handler import FileHandler

def test_file_handler():
    images = FileHandler.expand_images("././examples/image_samples/*")
    assert len(images) == 2
    assert "rabbit_pixel_art" in images[1]
    assert "pixel_art_landscape" in images[0]
    print(images)
