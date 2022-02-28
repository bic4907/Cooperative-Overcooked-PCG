import numpy as np
import random
import copy
from copy import deepcopy
from multiprocessing import Pool

class GA:

    def __init__(self,
                 population,
                 selection_method,
                 fitness_func,
                 args):

        self._population = population
        self._population_size = len(self._population)
        self._gene_size = len(self._population[0])
        self._selection_method = selection_method
        self._fitness_func = fitness_func
        self.args = args


    def _crossover(self, offspring, prob=1):
        offspring = copy.deepcopy(offspring)
        idx= np.arange(len(offspring))
        shuffled_offspring=list()
        np.random.shuffle(idx)

        for i in range(len(offspring)):
            shuffled_offspring.append(offspring[idx[i]])
        offspring=shuffled_offspring ## crossover 전 셔플 추가
        RECT_SIZE = 4
        MAX_RANGE = 10 - RECT_SIZE

        median = len(offspring) // 2

        for offspring_i in range(median):
            if random.random() <= prob:

                #  Sample a rectangle area for crossover
                x, y = random.randint(0, MAX_RANGE), random.randint(0, MAX_RANGE)

                individual_1 = np.array(list(offspring[offspring_i])).reshape(10, 10)
                individual_2 = np.array(list(offspring[offspring_i + median])).reshape(10, 10)

                individual_1[y:y+RECT_SIZE, x:x+RECT_SIZE], individual_2[y:y+RECT_SIZE, x:x+RECT_SIZE] \
                    = individual_2[y:y+RECT_SIZE, x:x+RECT_SIZE], individual_1[y:y+RECT_SIZE, x:x+RECT_SIZE]

                individual_1 = list(individual_1.reshape(-1))
                individual_2 = list(individual_2.reshape(-1))

                offspring[offspring_i] = ''.join(individual_1)
                offspring[offspring_i + median] = ''.join(individual_2)

        return offspring

    def _mutation(self, offspring, prob=0.01):
        offspring = copy.deepcopy(offspring)

        weights = [0.4, 0.2, 0.1, 0.1, 0.1, 0.1]

        for individual_index, item in enumerate(offspring):
            for gene_index in range(self._gene_size):
                if random.random() <= prob:
                    rand_int = random.choices(population=list(range(0, 6)), weights=weights, k=1)[0]

                    # rand_int = random.choice(list(range(0, 6)))

                    offspring[individual_index] = offspring[individual_index][:gene_index] + \
                        str(rand_int) + \
                        offspring[individual_index][gene_index + 1:]

        return offspring

    def _get_fitness(self, individual):
        fitness, _ = self._fitness_func(individual, self.args)
        return fitness

    def _selection(self):
        if self._selection_method == 'roulette':

            offspring = copy.deepcopy(self._population)
            new_population = list()

            fitness_values = np.array([self._get_fitness(individual) for individual in offspring])
            fitness_values = (fitness_values - fitness_values.min()) / (fitness_values.max() - fitness_values.min())

            sum_fitness = sum(fitness_values)
            ratios = fitness_values / sum_fitness

            for i in range(len(self._population)):
                x = random.uniform(0, 1)

                k = 0

                while k < len(self._population) - 1 and x > (sum(fitness_values[:k + 1]) / sum_fitness):
                    k = k + 1

                new_population.append(offspring[k])

            return new_population

        elif self._selection_method == 'tournament':

            new_population = list()

            for candidate1 in range(len(self._population)):
                candidate2 = random.randrange(0, len(self._population))

                individual_1 = self._population[candidate1]
                individual_2 = self._population[candidate2]

                fitness_1 = self._get_fitness(individual_1)
                fitness_2 = self._get_fitness(individual_2)

                if fitness_1 > fitness_2:
                    new_population.append(individual_1)
                else:
                    new_population.append(individual_2)

            return new_population

        else:
            raise Exception('Unknown selection method')

    def _sorting(self, offspring):
        fitness_value=list(range(0,200))
        for i in range(200):
            fitness_value[i]=self._get_fitness(offspring[i])
        sorted_fitness= sorted(fitness_value,reverse=True)

        sorted_offspring= []

        for i in range(len(offspring)):
            for j in range(len(offspring)):
                if sorted_fitness[i]==fitness_value[j]:
                    sorted_offspring.append(offspring[j])
                    break

        return sorted_offspring

    def evolution(self,generation):## 엘리티즘 추가
        offspring2=self._population

        offspring2=self._sorting(offspring2) ## 내림차순으로 정렬
        offspring = self._selection()
        offspring = self._crossover(offspring, prob=0.9)
        offspring = self._mutation(offspring, prob=0.02)

        offspring=self._sorting(offspring)
        for k in range(int(generation/5), 200): ## 세대에 걸쳐서 엘리티즘 비율이 선형적으로 증가
            offspring2[k] = deepcopy(offspring[k-int(generation/5)])
        offspring=deepcopy(offspring2)
        self._population = offspring

    @property
    def population(self):
        return self._population

    def get_average_fitness(self):
        fitness_values = np.array([self._get_fitness(individual) for individual in self._population])
        sum_fitness = sum(fitness_values)
        return sum_fitness / len(self._population)

    def get_best_fitness(self):
        fitness_values = np.array([self._get_fitness(individual) for individual in self._population])
        return max(fitness_values)

    def get_nth_best_index(self, n):
        fitness_values = np.array([self._get_fitness(individual) for individual in self._population])
        indices = (-fitness_values).argsort()[n - 1]
        return indices

    def get_best_individual(self):
        return self._population[self.get_nth_best_index(1)]
