from collections import defaultdict

from PIL import ImageGrab


if __name__ == '__main__':
    im = ImageGrab.grab()
    im.load()

    stats = defaultdict(int)
    # Determine top-left corner of board
    for x in xrange(im.width):
        for y in xrange(im.height):
            pixel = im.im.getpixel((x, y))
            pixel = pixel[:-1]
            stats[pixel] += 1

    print sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]
