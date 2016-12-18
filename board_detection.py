'''
Board detection works for lichess.org/chess.com
'''
import objc
from AppKit import NSBitmapImageRep
from Quartz.CoreGraphics import CGMainDisplayID

from PIL import ImageGrab

from board import Board
from pieces import WHITE, BLACK, PIECES, get_opp_color
from utils import normalize_cell
from mocks import get_mock


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


LICHESS = 'lichess'

def get_settings(mode):
    if mode == LICHESS:
        board_radius_pixels = 1
        colors = {
            'white_piece': (1, 1, 1),
            'black_piece': (0, 0, 0),
            'white_board_cell': (239 / 255.0, 216 / 255.0, 183 / 255.0),
            'moved_white_board_cell': (206 / 255.0, 209 / 255.0, 113 / 255.0),
            'moved_black_board_cell': (170 / 255.0, 161 / 255.0, 67 / 255.0),
            'letter': (137 / 255.0, 137 / 255.0, 137 / 255.0)
        }
        cell_size = 64
        pixels = {
            'pawn': {
                'white': [((73, 89), 'white_piece'), ((78, 77), ('black_piece'))],
                'black': [((54, 71), 'black_piece'), ((94, 113), ('black_piece'))],
            },
            'rook': {
                'white': [((25, 111), 'black_piece'), ((76, 40), ('black_piece'))],
                'black': [((79, 30), 'black_piece'), ((54, 104), ('black_piece'))],
            },
            'knight': {
                'white': [((69, 59), 'white_piece'), ((93, 103), ('white_piece'))],
                'black': [((32, 49), 'black_piece'), ((89, 100), ('black_piece'))],
            },
            'bishop': {
                'white': [((70, 42), 'white_piece'), ((75, 94), ('black_piece'))],
                'black': [((110, 107), 'black_piece'), ((52, 81), ('black_piece'))],
            },
            'queen': {
                'white': [((12, 37), 'black_piece'), ((34, 91), ('black_piece'))],
                'black': [((37, 86), 'black_piece'), ((14, 34), ('black_piece'))],
            },
            'king': {
                'white': [((81, 105), 'white_piece'), ((74, 52), ('black_piece'))],
                'black': [((101, 62), 'black_piece'), ((71, 44), ('black_piece'))],
            }
        }
        white_letter_count = 84
        black_letter_count = 59
    else:
        board_radius_pixels = 3
        colors = {
            'white_piece': (1, 1, 1),
            'black_piece': (0, 0, 0),
            'white_board_cell': (240 / 255.0, 217 / 255.0, 181 / 255.0),
            'moved_white_board_cell': (247 / 255.0, 236 / 255.0, 116 / 255.0),
            'moved_black_board_cell': (218 / 255.0, 195 / 255.0, 75 / 255.0),
            'letter': (152 / 255.0, 150 / 255.0, 149 / 255.0)
        }
        cell_size = 64
        pixels = {
            'pawn': {
                'white': [((43, 58), 'black_piece'), ((79, 91), ('white_piece'))],
                'black': [((60, 73), 'black_piece'), ((88, 106), ('black_piece'))],
            },
            'rook': {
                'white': [((91, 108), 'white_piece'), ((51, 83), ('black_piece'))],
                'black': [((47, 33), 'black_piece'), ((56, 113), ('black_piece'))],
            },
            'knight': {
                'white': [((30, 56), 'white_piece'), ((71, 94), ('white_piece'))],
                'black': [((93, 57), 'white_piece'), ((85, 92), ('black_piece'))],
            },
            'bishop': {
                'white': [((71, 80), 'white_piece'), ((83, 103), ('black_piece'))],
                'black': [((18, 101), 'black_piece'), ((82, 65), ('black_piece'))],
            },
            'queen': {
                'white': [((90, 81), 'white_piece'), ((94, 108), ('black_piece'))],
                'black': [((85, 26), 'black_piece'), ((13, 32), ('black_piece'))],
            },
            'king': {
                'white': [((51, 85), 'white_piece'), ((84, 69), ('white_piece'))],
                'black': [((56, 79), 'white_piece'), ((110, 63), ('black_piece'))],
            }
        }
        white_letter_count = 92
        black_letter_count = 43

    return {
        'board_radius_pixels': board_radius_pixels,
        'colors': colors,
        'cell_size': cell_size,
        'pixels': pixels,
        'white_letter_count': white_letter_count,
        'black_letter_count': black_letter_count
    }


DEVIATION = 1.5 / 255.0


def show_image(lt, rb):
    im = ImageGrab.grab(bbox=list(lt) + list(rb))
    im.load()
    im.show()


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


def get_lt_screen_cell_size(mode, prev_board):
    '''
    Try to guess left-top of screen and cell size.
    '''
    settings = get_settings(mode)

    lt_screen = None
    cell_size = None

    if prev_board is None:
        im = ImageGrab.grab()
        im.load()

        # Determine top-left corner of board
        for x in xrange(im.width):
            for y in xrange(im.height):
                pixel = im.im.getpixel((x, y))
                pixel = [c / 255.0 for c in pixel[:-1]]
                if similiar_pixel(pixel, [settings['colors']['white_board_cell'], settings['colors']['moved_white_board_cell']]):
                    # left-top corner pixel is not our, should move 1 point up
                    # real coordinates are twice less
                    lt_screen = (x / 2, y / 2 - settings['board_radius_pixels'])
                    # determine cell size
                    while similiar_pixel(pixel, [
                            settings['colors']['white_board_cell'], settings['colors']['moved_white_board_cell']]):
                        y += 1
                        # ??? if out of the image
                        pixel = im.im.getpixel((x, y))
                        pixel = [c / 255.0 for c in pixel[:-1]]
                    cell_size = y / 2 - lt_screen[1]
#                     xi = lt_screen[0] * 2
#                     yi = lt_screen[1] * 2
#                     show_image((xi, yi), (xi + cell_size * 8 * 2, yi + cell_size * 8 * 2))
#                     raise
                    break

            if lt_screen:
                break
    else:
        lt_screen = prev_board.lt_screen
        cell_size = prev_board.cell_size

    return lt_screen, cell_size


def get_board_data(mode, prev_board):
    settings = get_settings(mode)

    lt_screen, cell_size = get_lt_screen_cell_size(mode, prev_board)
    if not lt_screen:
        print 'Not found left top corner'
        return None
    if cell_size != settings['cell_size']:
        print 'Not a valid cell size, actual - {}, required - {}'.format(cell_size, settings['cell_size'])
        return None

    # + 30, be careful, extra pixels for letters below the board
    bitmap_width = cell_size * 8
    bitmap_height = cell_size * 8 + 15
    bitmap = get_screen_bitmap(lt_screen, (bitmap_width, bitmap_height))
    if (bitmap.size().width / 2 < bitmap_width or
            bitmap.size().height / 2 < bitmap_height):
        print 'Not full board is visible on the screen'
        return None

    # Check right bottom and center pixel
    rb_pixel = get_pixel(
        bitmap, 8 * cell_size * 2 - 1, 8 * cell_size * 2 - 1 - settings['board_radius_pixels'] * 2)
    center_pixel = get_pixel(
        bitmap, 4 * cell_size * 2 - 1, 4 * cell_size * 2 - 1)
    if not similiar_pixel(
            rb_pixel, [settings['colors']['white_board_cell'], settings['colors']['moved_white_board_cell']]):
        # Not a board
        print 'Right bottom pixel is incorrect'
        return None
    if not similiar_pixel(
            center_pixel, [settings['colors']['white_board_cell'], settings['colors']['moved_white_board_cell']]):
        # Not a board
        print 'Center pixel is incorrect'
        return None

    # Determine orientation
    or_xy = (3 * cell_size * 2 + cell_size * 2 / 2 - 10, 8 * cell_size * 2 + 5)
    or_xy_rb = (or_xy[0] + 20, or_xy[1] + 22)
#     show_image(
#         (lt_screen[0] * 2 + or_xy[0], lt_screen[1] * 2 + or_xy[1]),
#         (lt_screen[0] * 2 + or_xy_rb[0], lt_screen[1] * 2 + or_xy_rb[1]))

    letter_count = 0
    for x in xrange(or_xy[0], or_xy_rb[0]):
        for y in xrange(or_xy[1], or_xy_rb[1]):
            pixel = get_pixel(bitmap, x, y)
            if pixel == settings['colors']['letter']:
                letter_count += 1

    move_up_color = None
    if abs(letter_count - settings['white_letter_count']) < 4:
        # d
        move_up_color = WHITE
    elif abs(letter_count - settings['black_letter_count']) < 4:
        # e
        move_up_color = BLACK
    else:
        print letter_count
        print 'Can not determine move up color'
        return None

    return {
        'bitmap': bitmap,
        'move_up_color': move_up_color,
        'lt_screen': lt_screen,
        'cell_size': cell_size
    }


def get_board(mode, prev_board):
    board_data = get_board_data(mode, prev_board)
    if not board_data:
        return None

    settings = get_settings(mode)
    bitmap = board_data['bitmap']
    move_up_color = board_data['move_up_color']
    cell_size = board_data['cell_size']

    pieces = {}
    move_color = None
    yellow_cells = []
    for c in xrange(8):
        for r in xrange(8):
            x = c * cell_size * 2
            y = (7 - r) * cell_size * 2
            cell = normalize_cell((c, r), move_up_color)
            for piece, piece_info in settings['pixels'].items():
                for color, piece_color_info in piece_info.items():
                    for pixel_info in piece_color_info:
                        px = pixel_info[0][0]
                        py = pixel_info[0][1]
                        pixel = get_pixel(bitmap, x + px, y + py)
                        if pixel != settings['colors'][pixel_info[1]]:
                            break
                    else:
                        if cell in pieces:
                            print 'Two pieces for cell {}: {}, {}'.format(
                                cell, pieces[cell], (piece, color))
                            return None
                        pieces[cell] = (piece, color)

            # Determine whose move
            pixel = get_pixel(bitmap, x + 5, y + 5)
            if similiar_pixel(
                    pixel, [settings['colors']['moved_white_board_cell'], settings['colors']['moved_black_board_cell']]):
                yellow_cells.append(cell)
                if cell in pieces:
                    move_color = get_opp_color(pieces[cell][1])

    if move_color is None:
        if (not yellow_cells and
                all((c, r) in pieces for c in xrange(8) for r in [0, 1, 6, 7])):
            # Initial position, consider alson 960
            move_color = WHITE
        elif (len(yellow_cells) == 2 and
                yellow_cells[0][1] == 0 and yellow_cells[1][1] == 0):
            move_color = BLACK
        elif (len(yellow_cells) == 2 and
                yellow_cells[0][1] == 7 and yellow_cells[1][1] == 7):
            move_color = WHITE
        else:
            print 'Can not determine move color'
            return None

    en_passant = None
    if (len(yellow_cells) == 2 and
            abs(yellow_cells[0][1] - yellow_cells[1][1]) == 2):
        if (pieces.get(yellow_cells[0], (None, None))[0] == 'pawn' or
                pieces.get(yellow_cells[1], (None, None))[0] == 'pawn'):
            en_passant = (yellow_cells[0][0], (yellow_cells[0][1] + yellow_cells[1][1]) / 2)

    return Board(
        pieces=pieces,
        move_color=move_color,
        en_passant=en_passant,
        move_up_color=move_up_color,
        lt_screen=board_data['lt_screen'],
        cell_size=cell_size
    )
