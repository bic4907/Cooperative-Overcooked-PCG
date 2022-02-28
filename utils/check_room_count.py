import copy
import os.path
import random
import seaborn as sns
import numpy as np
import cv2

from variables.blocks import BlockType, block_type_to_code
from overcooked_ai_py.env import OverCookedEnv
import overcooked_ai_py.mdp.layout_generator as overcooked_lg
import secrets
import random


layout = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

layout = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

layout = [
    [0, 1, 0, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 0, 0, 0, 1, 0, 1],
    [1, 1, 0, 1, 0, 0, 0, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

layout = np.array(layout)


class RoomFinder(object):

    def __init__(self, layout):
        self._layout = layout

    def _search_four_direction(self, position, spaces):
        x, y = position


        if x < 0 or x >= self._layout.shape[1]:
            return
        if y < 0 or y >= self._layout.shape[0]:
            return
        if self._layout[y][x] != 0:
            return

        if position in spaces:
            return

        spaces.append(position)

        self._search_four_direction((x - 1, y), spaces=spaces)

        self._search_four_direction((x + 1, y), spaces=spaces)

        self._search_four_direction((x, y - 1), spaces=spaces)

        self._search_four_direction((x, y + 1), spaces=spaces)

        return spaces


    def get_rooms(self):
        rooms = dict()
        closed_position = dict()

        for y, row in enumerate(layout):
            for x, _ in enumerate(row):
                if self._layout[y][x] != 0:
                    continue
                if closed_position.keys().__contains__((x, y)):
                    continue

                room_id = len(rooms) + 1

                spaces = list()

                searched = self._search_four_direction((x, y), spaces=spaces)
                rooms[room_id] = copy.deepcopy(searched)

                for pos in searched:
                    closed_position[pos] = True

        return rooms

    def get_item(self, position):
        x, y = position
        if x < 0 or x >= self._layout.shape[1]:
            return None
        if y < 0 or y >= self._layout.shape[0]:
            return None
        return self._layout[y][x]

    def get_accessible_item(self, rooms):
        accessible_items = dict()

        for room_id, positions in rooms.items():

            accessible_items[room_id] = list()
            searched_position = list()

            mtx = np.zeros(self._layout.shape, dtype=np.int)

            for pos in positions:

                x, y = pos

                if (x, y) not in searched_position:
                    item = self.get_item((x, y))
                    if item in [BlockType.DISH_DISPENSER, BlockType.ONION_DISPENSER, BlockType.POT, BlockType.OUTLET]:
                        accessible_items[room_id].append(item)

                        mtx[y][x] = item

                    searched_position.append((x, y))

                if (x - 1, y) not in searched_position:
                    item = self.get_item((x - 1, y))
                    if item in [BlockType.DISH_DISPENSER, BlockType.ONION_DISPENSER, BlockType.POT, BlockType.OUTLET]:
                        accessible_items[room_id].append(item)

                        mtx[y][x - 1] = item

                    searched_position.append((x - 1, y))

                if (x + 1, y) not in searched_position:
                    item = self.get_item((x + 1, y))
                    if item in [BlockType.DISH_DISPENSER, BlockType.ONION_DISPENSER, BlockType.POT, BlockType.OUTLET]:
                        accessible_items[room_id].append(item)

                        mtx[y][x + 1] = item

                    searched_position.append((x + 1, y))

                if (x, y - 1) not in searched_position:
                    item = self.get_item((x, y - 1))
                    if item in [BlockType.DISH_DISPENSER, BlockType.ONION_DISPENSER, BlockType.POT, BlockType.OUTLET]:
                        accessible_items[room_id].append(item)

                        mtx[y - 1][x] = item

                    searched_position.append((x, y - 1))

                if (x, y + 1) not in searched_position:
                    item = self.get_item((x, y + 1))
                    if item in [BlockType.DISH_DISPENSER, BlockType.ONION_DISPENSER, BlockType.POT, BlockType.OUTLET]:
                        accessible_items[room_id].append(item)

                        mtx[y + 1][x] = item

                    searched_position.append((x, y + 1))

        return accessible_items

    def get_item_positions(self) -> dict:

        items = dict()

        for i_h, row in enumerate(self._layout):
            for i_w, item in enumerate(row):
                if item not in [BlockType.EMPTY, BlockType.WALL]:

                    if item not in items.keys():
                        items[item] = list()

                    items[item].append((i_h, i_w))

        return items

    def get_avg_distance_between_items(self):
        avg_distances = dict()
        item_positions = self.get_item_positions()

        import math
        for item, positions in item_positions.items():

            sum_distances = 0
            cnt_comparison = 0

            for i, i_pos in enumerate(positions):
                for k, k_pos in enumerate(positions):

                    if i == k: continue

                    dist = math.sqrt((i_pos[0] - k_pos[0]) ** 2 + (i_pos[1] - k_pos[1]) ** 2)

                    if dist <= 2: continue

                    sum_distances += dist
                    cnt_comparison += 1

            if cnt_comparison == 0: continue

            avg_distance = sum_distances / cnt_comparison
            avg_distances[item] = avg_distance

        return avg_distances

    def distance_between_other_items(self):

        avg_location= dict()
        item_positions = self.get_item_positions()
        itemlist=list()
        import math
        for item, positions in item_positions.items():

            sum_x_coordinate= 0
            sum_y_coordinate= 0
            cnt_number= 0

            for i, i_pos in enumerate(positions):
                sum_x_coordinate+=i_pos[0]
                sum_y_coordinate+=i_pos[1]
                cnt_number+=1

            if cnt_number == 0: continue

            avg_location_xy = [sum_x_coordinate/cnt_number, sum_y_coordinate/cnt_number]
            avg_location[item] = avg_location_xy

            itemlist.append(item)
        new_distance=0
        if len(itemlist) != 4:
            new_distance = -10
            return new_distance
        a=[2,3,4,5]

        for i in range(0,3):

            new_distance += math.sqrt((avg_location[a[i]][0]-avg_location[a[i+1]][0])**2+(avg_location[a[i]][1]-avg_location[a[i+1]][1])**2)
        if new_distance>27:
            new_distance=-10
        return new_distance

import os
file_path = os.path.abspath(__file__)


def visualize_room(layout, rooms):
    w, h = layout.shape[1], layout.shape[0]

    output = np.zeros((h, w, 3))
    palette = sns.color_palette(None, len(rooms))

    for i, room_id in enumerate(rooms):
        room_list = rooms[room_id]

        for pos in room_list:
            x, y = pos
            output[y][x] = palette[i]

    for y, row in enumerate(layout):
        for x, item in enumerate(row):
            if item == BlockType.POT:
                output[y][x] = (128 / 255, 128 / 255, 128 / 255)
            elif item == BlockType.DISH_DISPENSER:
                output[y][x] = (255 / 255, 255 / 255, 255 / 255)
            elif item == BlockType.ONION_DISPENSER:
                output[y][x] = (0, 255 / 255, 255 / 255)
            # elif item == BlockType.TOMATO_DISPENSER:
            #    output[y][x] = (0, 255 / 255, 255 / 255)
            elif item == BlockType.OUTLET:
                output[y][x] = (255 / 255, 0 / 255, 255 / 255)

    output = cv2.resize(output, (300, 300), interpolation=cv2.INTER_NEAREST)
    # output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)

    # cv2.imshow('Rooms', output)



def render_to_game(map_array):

    map_array = np.pad(map_array, (1, 1), 'constant', constant_values=1)
    with open('sample_layout.layout', 'r') as f:
        sample = f.read()

    layout_str = ''
    for row_i, row in enumerate(map_array):
        if row_i != 0:
            layout_str += '                '
        for item in row:
            layout_str += block_type_to_code(item)
        layout_str += '\n'

    layout_str += '                ' + 'X' * map_array.shape[1] + '\n'
    layout_str += '                ' + 'X12PSOD' + 'X' * (map_array.shape[1] - 7) + '\n'
    layout_str += '                ' + 'X' * map_array.shape[1]

    map_name = 'tmp_' + secrets.token_hex(nbytes=16)
    file_name = map_name + '.layout'

    with open(os.path.join('.', 'overcooked_ai_py', 'data', 'layouts', file_name), 'w+') as f:
         dumped = sample.replace('[GRID]', layout_str)
         f.write(dumped)

    env = OverCookedEnv(scenario=map_name)
    output = env.render()
    try:
        os.remove(os.path.join('.', 'overcooked_ai_py', 'data', 'layouts', file_name))
    except:
        pass

    return output


def convert_to_layout(map_array):
    rooms = RoomFinder(map_array).get_rooms()

    if len(rooms) >= 2:
        keys = random.sample(rooms.keys(), k=2)

        positions_1 = random.choice(rooms[keys[0]])
        positions_2 = random.choice(rooms[keys[1]])
    else:
        key = random.sample(rooms.keys(), k=1)[0]
        positions = random.sample(rooms[key], k=2)

        positions_1, positions_2 = positions

    map_array[positions_1[1], positions_1[0]] = BlockType.PLAYER1
    map_array[positions_2[1], positions_2[0]] = BlockType.PLAYER2

    map_array = np.pad(map_array, (1, 1), 'constant', constant_values=1)
    with open('sample_layout.layout', 'r') as f:
        sample = f.read()

    layout_str = ''
    for row_i, row in enumerate(map_array):
        if row_i != 0:
            layout_str += '                '
        for item in row:
            layout_str += block_type_to_code(item)

        if row_i != 11:
            layout_str += '\n'

    converted = sample.replace('[GRID]', layout_str)

    return converted


