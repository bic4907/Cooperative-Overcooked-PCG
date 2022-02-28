import copy


def remove_unusable_parts(layout):
    new_layout = copy.deepcopy(layout)

    def is_available(pos):
        x, y = pos

        if y - 1 >= 0 and layout[y - 1][x] == 0:
            return True
        if y + 1 < new_layout.shape[0] and layout[y + 1][x] == 0:
            return True
        if x - 1 >= 0 and layout[y][x - 1] == 0:
            return True
        if x + 1 < new_layout.shape[1] and layout[y][x + 1] == 0:
            return True

        return False

    remove_candidates = list()

    for y, row in enumerate(layout):
        for x, item in enumerate(row):
            if not is_available((x, y)):
                remove_candidates.append((x, y))

    for pos in remove_candidates:
        x, y = pos
        new_layout[y][x] = 1
    return new_layout