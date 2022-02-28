
class BlockType(object):
    EMPTY = 0
    WALL = 1

    POT = 3
    DISH_DISPENSER = 4
    ONION_DISPENSER = 2

    OUTLET = 5

    PLAYER1 = 7
    PLAYER2 = 8


def block_type_to_code(block_type):
    if block_type == BlockType.EMPTY:
        return ' '
    elif block_type == BlockType.WALL:
        return 'X'
    elif block_type == BlockType.POT:
        return 'P'
    elif block_type == BlockType.DISH_DISPENSER:
        return 'D'
    elif block_type == BlockType.ONION_DISPENSER:
        return 'O'
    elif block_type == BlockType.OUTLET:
        return 'S'
    elif block_type == BlockType.PLAYER1:
        return '1'
    elif block_type == BlockType.PLAYER2:
        return '2'
    else:
        assert 'Not support block type'
