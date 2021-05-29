import iterated_greedy_algorithm as ig
import signed_utils as utils
# import matplotlib.pyplot as plt
import time


"""
# target frustration index:
# 200: 45
# 400: 57
# 600: 109
# 800: 241
# 1000: 600
# 2000: 2184
# 4000: 6190
# 8000: 16035
# 10000: 20527
"""


def main(path, t=10):
    # path = "generated_dataset_20_120_6_0.8_0.2_0.5_1619942955.g"
    dataset = utils.load_data(path)

    # the multi start mechanism of initialization method is implemented here.
    multi_initialization = []
    initial_values = []

    ts = time.time()
    for i in range(t):
        print("initializing:", i + 1, "/", t)
        multi_alg = ig.IteratedGreedy(dataset=dataset, beta=0.3)
        multi_alg.initialization(output=False)
        multi_initialization.append(multi_alg)
        initial_values.append(multi_alg.objective_function.obj_value)
    te = time.time()
    print("Initialization cost:", te - ts, "s")

    b = initial_values.index(min(initial_values))
    alg = multi_initialization[b]
    best_values = alg.run(max_iter=150, output=False, multi_start=True)
    print(best_values)
    return best_values[-1]
    # plt.plot([t * 0.1 for t in range(700)], best_values)
    # plt.xlabel("Computational time (s)")
    # plt.ylabel("Frustration index")
    # plt.show()


if __name__ == "__main__":
    path = "datasets/slashdot-undirected-size2000-part0.g"
    main(path)
