import cv2
import matplotlib.pyplot as plt
import random
import numpy as np
import statistics
import argparse
import logging
import os
import pandas as pd
import seaborn as sns
import json

from GA import GA
from utils.check_room_count import RoomFinder, visualize_room, render_to_game, convert_to_layout
from utils.postprocessing import remove_unusable_parts
from initializer import initialize
from fitness_function import fitness_function

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Workspace(object):
    def __init__(self, args):
        self.args = args
        logger.info(self.args)

        self.result_dir = './results/room{0}_pot{1}_onion{2}_dish{3}_outlet{4}_fd{5}_fbd{6}_seed{7}'.format(self.args.room_count,
                                                                                               self.args.pot_count,
                                                                                               self.args.onion_count,
                                                                                               self.args.dish_count,
                                                                                               self.args.outlet_count,
                                                                                               self.args.factor_distance,
                                                                                               self.args.factor_between_distance,

                                                                                               self.args.seed
                                                                                               )
        logger.info('Result path : {0}'.format(self.result_dir))
        random.seed(self.args.seed)

        # Save parameters to result directory
        os.makedirs(self.result_dir, exist_ok=True)
        os.makedirs(os.path.join(self.result_dir, 'images'), exist_ok=True)

        with open(os.path.join(self.result_dir, 'parameters.json'), 'w') as f:
            json.dump(vars(self.args), f)

        self.best_fitness = None

    def run(self):

        pop1 = initialize()
        shuffled_list=[2,3,4,5]

        random.shuffle(shuffled_list)

        ga = GA(
            population=pop1,
            selection_method='roulette',
            fitness_func=fitness_function,
            args=self.args

        )

        for i in range(500):
            ga.evolution(i)
            individual = ga.get_best_individual()

            individual = np.array(list(individual)).astype(int)
            individual = individual.reshape(10, 10)
            rooms = RoomFinder(individual).get_rooms()

            visualize_room(individual.reshape(10, 10), rooms)
            game_image = render_to_game(individual.reshape(10, 10))

            new_individual = remove_unusable_parts(individual)
            new_game_image = render_to_game(new_individual.reshape(10, 10))

            fitness, detail = fitness_function(individual, self.args)

            cv2.imwrite(os.path.join(self.result_dir, 'images', '{0}_original.jpg'.format(i)), game_image)
            cv2.imwrite(os.path.join(self.result_dir, 'images', '{0}_processed.jpg'.format(i)), new_game_image)

            if self.best_fitness is None or self.best_fitness < fitness:
                cv2.imwrite(os.path.join(self.result_dir, 'best_original.jpg'.format(i)), game_image)
                cv2.imwrite(os.path.join(self.result_dir, 'best_processed.jpg'.format(i)), new_game_image)

                sizes = [len(rooms[room]) for room in rooms]

                if len(sizes) > 1:
                    sizes = np.array(sizes)
                    size_stdev = statistics.stdev(sizes)
                    fit_size_std = size_stdev
                else:
                    fit_size_std = 1

                # Count for each block, count rooms, record fitness value -> to dataframe pickle
                information = {
                    'fitness': fitness,
                    'room_count': len(rooms),
                    'room_size': fit_size_std,
                    'block_0': np.count_nonzero(new_individual == 0),
                    'block_1': np.count_nonzero(new_individual == 1),
                    'block_2': np.count_nonzero(new_individual == 2),
                    'block_3': np.count_nonzero(new_individual == 3),
                    'block_4': np.count_nonzero(new_individual == 4),
                    'block_5': np.count_nonzero(new_individual == 5),
                }

                with open(os.path.join(self.result_dir, 'best_chromosome.json'), 'w') as f:
                    json.dump(information, f)

                with open(os.path.join(self.result_dir, 'best_level.layout'), 'w') as f:
                    layout = convert_to_layout(new_individual.reshape(10, 10))
                    f.write(layout)

                self.best_fitness = fitness

            logger.info('Generation {0:05} | mean {1:.4} | best {2:.4}'.format(i, ga.get_average_fitness(), ga.get_best_fitness()))


if __name__ == '__main__':

    parser = argparse.ArgumentParser('Parameter settings for experiment')
    parser.add_argument('--room_count', type=int, required=True, help='Number of rooms in the map')
    parser.add_argument('--pot_count', type=int, required=True, help='Number of pots in the map')
    parser.add_argument('--onion_count', type=int, required=True, help='Number of onions in the map')
    parser.add_argument('--dish_count', type=int, required=True, help='Number of dish in the map')
    parser.add_argument('--outlet_count', type=int, required=True, help='Number of outlet in the map')
    parser.add_argument('--weight_resource_distance', type=float, default=0., help='Distance between resource in a task.')
    parser.add_argument('--weight_task_distance', type=float, default=0., help='Distance between tasks in a level.')
    parser.add_argument('--seed', type=int, required=True, help='Seed of the experiment')


    args = parser.parse_args()

    workspace = Workspace(args)
    workspace.run()
