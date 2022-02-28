import numpy as np
import statistics

from utils.check_room_count import RoomFinder

from variables.blocks import BlockType


def fitness_function(individual, args):
    """Calculate fitness value of an individual."""

    individual = np.array(list(individual)).astype(int)
    individual = individual.reshape(10, 10)

    rooms = RoomFinder(individual).get_rooms()

    sizes = [len(rooms[room]) for room in rooms]
    fit_room_cnt = abs(args.room_count - len(rooms))

    available_items = RoomFinder(individual).get_accessible_item(rooms)

    TARGET_POT_CNT = args.pot_count
    TARGET_DISH_CNT = args.dish_count
    TARGET_ONION_CNT = args.onion_count
    TARGET_OUTLET_CNT = args.outlet_count

    pot_cnt, dish_cnt, onion_cnt, outlet_cnt = 0, 0, 0, 0
    pot_cnt_arr, dish_cnt_arr, onion_cnt_arr = [], [], []

    for room_id, items in available_items.items():
        pot_cnt += items.count(BlockType.POT)
        dish_cnt += items.count(BlockType.DISH_DISPENSER)
        onion_cnt += items.count(BlockType.ONION_DISPENSER)
        outlet_cnt += items.count(BlockType.OUTLET)

        pot_cnt_arr.append(items.count(BlockType.POT))
        dish_cnt_arr.append(items.count(BlockType.DISH_DISPENSER))
        onion_cnt_arr.append(items.count(BlockType.ONION_DISPENSER))

    n_controls = 4
    fit_pot_cnt = abs(TARGET_POT_CNT - pot_cnt) / TARGET_POT_CNT / n_controls
    fit_dish_cnt = abs(TARGET_DISH_CNT - dish_cnt) / TARGET_DISH_CNT / n_controls
    fit_onion_cnt = abs(TARGET_ONION_CNT - onion_cnt) / TARGET_ONION_CNT / n_controls
    fit_outlet_cnt = abs(TARGET_OUTLET_CNT - outlet_cnt) / TARGET_OUTLET_CNT / n_controls
    fit_item_cnt = fit_pot_cnt + fit_dish_cnt + fit_onion_cnt + fit_outlet_cnt

    fit_task_distance = RoomFinder(individual).distance_between_other_items()

    avg_distances = RoomFinder(individual).get_avg_distance_between_items()
    fit_resource_distance = sum(avg_distances.values()) / (n_controls - 1)

    if len(sizes) > 1:
        sizes = np.array(sizes)
        size_stdev = statistics.stdev(sizes)
        fit_size_std = size_stdev * 0.1
    else:
        fit_size_std = 1

    fitness = -(1.5 * fit_room_cnt + 3 * fit_item_cnt + 2 * fit_size_std + \
                args.weight_resource_distance * fit_resource_distance - \
                args.weight_task_distance * fit_task_distance)

    detail = {
        'fit_room_cnt': -fit_room_cnt,

        'fit_pot_cnt': -fit_pot_cnt,
        'fit_dish_cnt': -fit_dish_cnt,
        'fit_onion_cnt': -fit_onion_cnt,
        'fit_outlet_cnt': -fit_outlet_cnt,
        'fit_item_cnt': -fit_item_cnt,

        'fit_size_std': -fit_size_std,

        'fit_resource_distance': -fit_resource_distance,
        'fit_task_distance': -fit_task_distance,

        'total_fitness': fitness
    }

    return fitness, detail