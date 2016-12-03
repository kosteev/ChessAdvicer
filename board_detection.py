import objc
from AppKit import NSBitmapImageRep
from Quartz.CoreGraphics import CGMainDisplayID

from PIL import ImageGrab

from board import Board
from pieces import WHITE, BLACK, PIECES, get_opp_color


# Big big thanks to https://bitbucket.org/ronaldoussoren/pyobjc/ for updated .bridgesupport files
# And also this particular message that showed how to use them:
# http://www.mail-archive.com/pythonmac-sig@python.org/msg09749.html

# Import the definition for CGDisplayCreateImageForRect
objc.parseBridgeSupport( """<?xml version='1.0'?>
<!DOCTYPE signatures SYSTEM "file://localhost/System/Library/DTDs/BridgeSupport.dtd">
<signatures version='1.0'>
  <depends_on path='/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation' />
  <depends_on path='/System/Library/Frameworks/IOKit.framework/IOKit' />
  <depends_on path='/System/Library/Frameworks/CoreServices.framework/CoreServices' />
  <function name='CGDisplayCreateImageForRect'>
    <retval already_cfretained='true' type='^{CGImage=}' />
    <arg type='I' />
    <arg type='{CGRect={CGPoint=ff}{CGSize=ff}}' type64='{CGRect={CGPoint=dd}{CGSize=dd}}' />
  </function>
</signatures>
""", globals(), '/System/Library/Frameworks/ApplicationServices.framework/Frameworks/CoreGraphics.framework')


CELL_SIZE = 128


COLORS = {
    'white': (1, 1, 1),
    'black': (0, 0, 0),
    'white_board': (239 / 255.0, 216 / 255.0, 183 / 255.0),
    'yellow_white_board': (206 / 255.0, 209 / 255.0, 113 / 255.0),
    'yellow_black_board': (170 / 255.0, 161 / 255.0, 67 / 255.0),
    'grey': (137 / 255.0, 137 / 255.0, 137 / 255.0)
}


DEVIATION = 1 / 255.0


def similiar_pixel(p1, colors):
    for color in colors:
        if (abs(p1[0] - color[0]) < DEVIATION and
            abs(p1[1] - color[1]) < DEVIATION and
                abs(p1[2] - color[2]) < DEVIATION):
            return True

    return False


def get_screen_bitmap(lt, rb):
    mainID = CGMainDisplayID()
    # Grab a chunk of the screen from lt to rb
    image = CGDisplayCreateImageForRect(mainID, (lt, rb))
    bitmap = NSBitmapImageRep.alloc()
    bitmap.initWithCGImage_(image)

    return bitmap


def get_pixel(bitmap, x, y):
    c = bitmap.colorAtX_y_(x, y)
    return c.redComponent(), c.greenComponent(), c.blueComponent()


def get_lt_screen(prev_board):
    '''
    Try to guess left-top of screen.
    '''
    lt_screen = None

    if prev_board is None:
        im = ImageGrab.grab()
        im.load()

        # Determine top-left corner of board
        for x in xrange(im.width):
            for y in xrange(im.height):
                pixel = im.im.getpixel((x, y))
                pixel = [c / 255.0 for c in pixel[:-1]]
                if similiar_pixel(pixel, [COLORS['white_board'], COLORS['yellow_white_board']]):
                    # left-top corner pixel is not our, should move 1 point up
                    # real coordinates are twice less
                    lt_screen = (x / 2, y / 2 - 1)
                    break

            if lt_screen:
                break
    else:
        lt_screen = prev_board.lt_screen

    return lt_screen


def get_board_data(prev_board):
    lt_screen = get_lt_screen(prev_board)
    if not lt_screen:
        print 'Not found left top corner'
        return None

    # + 30, be careful, extra pixels for letters below the board
    bitmap_width = CELL_SIZE * 8
    bitmap_height = CELL_SIZE * 8 + 30
    bitmap = get_screen_bitmap(lt_screen, (bitmap_width / 2, bitmap_height / 2))
    if (bitmap.size().width < bitmap_width or
            bitmap.size().height < bitmap_height):
        print 'Not full board is visible on the screen'
        return None

    # Check right bottom pixel
    # right-bottom corner pixel is not our, should move 2 points up
    rb_pixel = get_pixel(bitmap, 8 * CELL_SIZE - 1, 8 * CELL_SIZE - 3)
    if not similiar_pixel(
            rb_pixel, [COLORS['white_board'], COLORS['yellow_white_board']]):
        # Not a board
        print 'Right bottom pixel is incorrect'
        return None

    # Determine orientation
    or_xy = (3 * CELL_SIZE + CELL_SIZE / 2 - 10, 8 * CELL_SIZE + 5)
    or_xy_rb = (or_xy[0] + 20, or_xy[1] + 22)

    grey_count = 0
    for x in xrange(or_xy[0], or_xy_rb[0]):
        for y in xrange(or_xy[1], or_xy_rb[1]):
            pixel = get_pixel(bitmap, x, y)
            if pixel == COLORS['grey']:
                grey_count += 1

    move_up_color = None
    if abs(grey_count - 84) < 1:
        # D - 84
        move_up_color = WHITE
    elif abs(grey_count - 59) < 1:
        # E - 59
        move_up_color = BLACK
    else:
        print 'Can not determine move up color'
        return None

    return {
        'bitmap': bitmap,
        'move_up_color': move_up_color,
        'lt_screen': lt_screen
    }


def get_board(prev_board):
    board_data = get_board_data(prev_board)
    if not board_data:
        return None

    bitmap = board_data['bitmap']

    pieces = {}
    move_color = None
    yellow_cells = []
    for c in xrange(8):
        for r in xrange(8):
            x = c * CELL_SIZE
            y = r * CELL_SIZE

            for piece, info in PIECES.items():
                for ind, color in enumerate([WHITE, BLACK]):
                    for pixel_info in info['pixels'][ind]:
                        px = pixel_info[0]
                        py = pixel_info[1]
                        pixel = get_pixel(bitmap, x + px, y + py)
                        if pixel != COLORS[pixel_info[-1]]:
                            break
                    else:
                        pieces[(c, r)] = (piece, color)

            # Determine whose move
            pixel = get_pixel(bitmap, x + 5, y + 5)
            if pixel in [COLORS['yellow_white_board'], COLORS['yellow_black_board']]:
                yellow_cells.append((c, r))
                if (c, r) in pieces:
                    move_color = get_opp_color(pieces[(c, r)][1])

    move_up_color = board_data['move_up_color']
    if move_color is None:
        if not yellow_cells:
            # Initial position
            move_color = WHITE
        elif (len(yellow_cells) == 2 and
                yellow_cells[0][1] == 0 and yellow_cells[1][1] == 0):
            move_color = move_up_color
        elif (len(yellow_cells) == 2 and
                yellow_cells[0][1] == 7 and yellow_cells[1][1] == 7):
            move_color = get_opp_color(move_up_color)
        else:
            print 'Can not determine move color'
            return None

    return Board(
        pieces=pieces,
        move_up_color=move_up_color,
        move_color=move_color,
        lt_screen=board_data['lt_screen']
    )
