import objc
from AppKit import NSBitmapImageRep
from Quartz.CoreGraphics import CGMainDisplayID

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


DEVIATION = 2 / 255.0


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


def get_board_data():
    bitmap = get_screen_bitmap((0, 0), (-1, -1))

    # Determine top-left corner of board
    xy_min = None
    bitmap_size = bitmap.size()
    for x in xrange(int(bitmap_size.width + 0.5)):
        for y in xrange(int(bitmap_size.height + 0.5)):
            lt_pixel = get_pixel(bitmap, x, y)
            if similiar_pixel(
                    lt_pixel, [COLORS['white_board'], COLORS['yellow_white_board']]):
                # left-top corner pixel is not our, should move 2 points up
                xy_min = (x, y - 2)
                xy_max = (xy_min[0] + 8 * CELL_SIZE, xy_min[1] + 8 * CELL_SIZE)

                # Check right bottom pixel
                # right-bottom corner pixel is not our, should move 2 points up
                try:
                    # !!!! except error on outbound
                    rb_pixel = get_pixel(bitmap, xy_max[0] - 1, xy_max[1] - 3)
                except:
                    return None
                if not similiar_pixel(
                        rb_pixel, [COLORS['white_board'], COLORS['yellow_white_board']]):
                    # Not a board
                    return None

                break

        if xy_min:
                break

    if not xy_min:
        return None

    # Determine orientation
    or_xy_min = (xy_min[0] + 3 * CELL_SIZE + CELL_SIZE / 2 - 10, xy_max[1] + 5)
    or_xy_max = (or_xy_min[0] + 20, or_xy_min[1] + 22)

    grey_count = 0
    for x in xrange(or_xy_min[0], or_xy_max[0]):
        for y in xrange(or_xy_min[1], or_xy_max[1]):
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
        'board_lt': xy_min,
        'move_up_color': move_up_color
    }


def get_board():
    board_data = get_board_data()
    if not board_data:
        return None

    bitmap = board_data['bitmap']
    board_lt = board_data['board_lt']

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
                        pixel = get_pixel(bitmap, board_lt[0] + x + px, board_lt[1] + y + py)
                        if pixel != COLORS[pixel_info[-1]]:
                            break
                    else:
                        pieces[(c, r)] = (piece, color)

            # Determine whose move
            pixel = get_pixel(bitmap, board_lt[0] + x + 5, board_lt[1] + y + 5)
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
        board_lt=board_lt
    )
