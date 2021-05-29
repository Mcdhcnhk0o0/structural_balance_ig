from module import *
import time
import math
import signed_utils as utils
import random as rd


class IteratedGreedy:
    """
    IG：
        1. s_z <- generate an initial solution;
        2. s_* <- apply local search to s_z;
        3. while termination condition is not satisfied do:
            s_p <- apply destruction to s_*
            s_' <- apply construction to s_p
            s_' <- apply local search to s_'
            if acceptance criterion is satisfied then
                s_* <- s_'
            end
        4. return s_*
    """

    def __init__(self, dataset: utils.Dataset, beta=0.3):
        """
        class initialization

        :param dataset: a given dataset
        """
        self._dataset = dataset
        self.neighborhood = Neighborhood(dataset=dataset)
        self.objective_function = Frustration(dataset)
        self.node_available = self.__pretreatment()
        self.local_search = LocalSearch(self.objective_function, self.neighborhood, self.node_available)
        self.beta = beta
        self.T = - 1

    def initialization(self, output=True):
        init = Initialization(self._dataset, self.neighborhood)
        solution, partition = init.greedy_initialization(self.objective_function)
        # solution, partition = init.multi_start_greedy_initialization(self.objective_function)
        self.objective_function.set_solution(solution)
        self.objective_function.update_objective_function()
        self.T = self.objective_function.obj_value
        if output:
            print("Initialization complete!")
            print("Initial value:", self.objective_function.obj_value)
            print('Num of initial clusters', len(self.objective_function.partition))
            print("Solution:", self.objective_function.solution)

    def destruction_and_reconstruction(self):
        destruction_nodes = self.__destruction()
        self.__reconstruction(destruction_nodes)

    def acceptance_criterion(self, status, alpha=0.99, method='metropolis'):
        obj = self.objective_function
        last_solution = status['solution']
        last_value = status['value']
        if method == 'better':
            if last_value < obj.obj_value:
                obj.set_solution(last_solution)
                obj.obj_value = last_value
        else:

            if last_value < obj.obj_value and rd.random() > math.exp((last_value - obj.obj_value) / self.T):
                obj.set_solution(last_solution)
                obj.obj_value = last_value
        self.T *= alpha

    def run(self, max_iter=2000, output=True, multi_start=False):
        print("IG is running……")
        start_time = time.time()
        if not multi_start:
            self.initialization()
        abandoned = self._dataset.vnum - len(self.node_available)
        ct = 1
        ls = self.local_search
        ls.local_move()
        ls.community_merge()
        best_values = []

        while ct <= max_iter:

            status = self.record_status()
            self.destruction_and_reconstruction()
            ls.local_move()
            ls.community_merge()

            self.acceptance_criterion(status, method='better')
            # self.acceptance_criterion(status)
            # if self.objective_function.obj_value < self.best_value:
            #     self.best_value = self.objective_function.obj_value
            #     self.best_solution_set = [self.objective_function.solution, self.objective_function.partition]

            if output:
                current_time = time.time()
                print("execution time: ", current_time - start_time, "s")
                print('%d/%d: best value --> %d with %d clusters' %
                      (ct, max_iter, self.objective_function.obj_value, len(self.objective_function.partition) - abandoned))
                # print('        current value --> ', self.objective_function.obj_value)
            best_values.append(self.objective_function.obj_value)
            ct += 1

        end_time = time.time()
        print('IG Complete!')
        print('=' * 40)
        print('Best Value:', best_values[-1])
        print('time cost:', end_time - start_time, "s")
        return best_values

    def record_status(self):
        """
        for acceptance criterion

        :return: current partition status
        """
        status = {
            'solution': self.objective_function.solution.copy(),
            'value': self.objective_function.obj_value
        }
        return status

    def __destruction(self):
        """
        destruction phase

        :param beta: ratio of nodes removed
        :return: a list of the removed nodes
        """

        obj = self.objective_function
        removed_node = rd.sample(self.node_available, int(obj.vnum * self.beta))

        for node in removed_node:
            delta = obj.delta_caused_by_decompose(node, self.neighborhood.neighborhood_structure[node])
            obj.decompose(node, delta=delta)

        return removed_node

    def __reconstruction(self, isolated_node):
        """
        construction phase

        :param isolated_node: a removed node list
        :return: None, reconstruct the partition
        """

        obj = self.objective_function
        nbr = self.neighborhood

        for node in isolated_node:
            min_delta = 0
            candidate = -1

            for nbr_community in nbr.get_adjacent_cluster(node, obj.solution):

                delta = obj.delta_caused_by_move(node, nbr_community, nbr.neighborhood_structure[node])
                if delta < min_delta:
                    min_delta = delta
                    candidate = nbr_community
            if candidate != -1:
                obj.move(node, candidate, min_delta)

    def __pretreatment(self):
        alone = set()
        isolated = set()

        for i in range(self._dataset.vnum):
            if i not in self.neighborhood.neighborhood_structure.keys():
                alone.add(i)
                continue
            if not self.neighborhood.neighborhood_structure[i]['+']:
                isolated.add(i)
        for node in isolated:
            for nbr in self.neighborhood.neighborhood_structure[node]["-"]:
                self.neighborhood.neighborhood_structure[nbr]["-"].remove(node)
            del self.neighborhood.neighborhood_structure[node]

        node_available = set(range(self._dataset.vnum)) - alone - isolated
        return list(node_available)

    # def __reconstruction_old(self, destruction_nodes, p_type):
    #
    #     obj = self.objective_function
    #
    #     if p_type == 'all':
    #         candidate_community = set(obj.partition.keys())
    #         for node in destruction_nodes:
    #             try:
    #                 obj.solution[node] = rd.choice(list(candidate_community - {obj.solution[node]}))
    #             except IndexError:
    #                 continue
    #
    #     elif p_type == 'neighbor':
    #         for node in destruction_nodes:
    #             try:
    #                 obj.solution[node] = rd.choice(list(obj.get_adjacent_community(node, self.neighborhood)))
    #             except IndexError:
    #                 continue
    #
    #     obj.partition = utils.solution2partition(obj.solution)
    #     obj.update_objective_function()


def get_end_position(values):
    target = values[-1]
    for i in range(len(values)):
        if values[i] == target:
            return i + 1
    return len(values)


if __name__ == '__main__':

    file_name = r'datasets\slashdot-undirected-size4000-part0.g'
    ds = utils.load_data(file_name)
    min_iterations = []
    results = []
    for _ in range(20):
        ig = IteratedGreedy(ds)
        vs = ig.run(max_iter=200)
        results.append(vs[-1])
        min_iterations.append(get_end_position(vs))
    print(min_iterations)
    print(results)
    print(sum(results) / 20)
    print(sum(min_iterations) / 20)
