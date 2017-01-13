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

    stats_list = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    print stats_list[:10]

    for p1, p2 in zip(stats_list[:-1], stats_list[1:]):
        if abs(p1[1] - 64 * 64 * 4) < 10:
            print p1, p2
