import random
import math
import argparse
import importlib
import time
from functools import wraps
import matplotlib.pyplot as plt


def profile(fn):
    @wraps(fn)
    def with_profiling(*args, **kwargs):
        start_time = time.time()
        ret = fn(*args, **kwargs)
        elapsed_time = time.time() - start_time

        if fn.__name__ not in PROF_DATA:
            PROF_DATA[fn.__name__] = [0, []]
        PROF_DATA[fn.__name__][0] += 1
        PROF_DATA[fn.__name__][1].append(elapsed_time)
        return ret

    return with_profiling


@profile
def algorithm(size):
    args = arg_function(size)
    if type(args) is tuple:
        my_function(*args)
    elif type(args) is dict:
        my_function(**args)
    else:
        my_function(args)


PROF_DATA = {}


def print_prof_data():
    global avg_time
    for fname, data in PROF_DATA.items():
        # max_time = max(data[1])
        avg_time = sum(data[1]) / len(data[1])
        # print("Function %s called %d times. " % (fname, data[0])),
        # print('Execution time max: %.3f, average: %.3f' %(max_time,avg_time))
        # print('time = %.3f' % (avg_time))


def clear_prof_data():
    global PROF_DATA
    PROF_DATA = {}


def rand(size, do):  # zwraca tablicę o podanym rozmiarze
    tab = []  # z wylosowanymi wartościami
    while size > 0:  # dopóki jakieś musi dodać
        tmp = random.randint(0, do)
        tab.append(tmp)
        size -= 1  # zmniejsza ilość pozostałych komórek do wylosowania
    return tab


def check_2_to_n():
    # precision - how many points are out of line
    precision = 0
    last_point = ((size_max - size_min) // step) - 1
    global c
    c = points[last_point][1] * (2 ** (-points[last_point][0]))
    for i in range(0, (size_max - size_min) // step):
        if points[i][1] > 0:
            ratio = (c * (2 ** points[i][0])) / points[i][1]
            if abs(ratio - 1) > 1:
                precision += 1
    precision /= points_quantity
    if precision > 0.2 or points[i][1] < 0.005:  # c==0
        print("It's faster than O(2^n)")
        return False
    print("It's O(2^n) with c = " + str(c))
    return True


def check_exp_to_r(r):
    precision = 0
    global c
    c = points[middle_point][1] / (points[middle_point][0] ** (r))
    for i in range(0, (size_max - size_min) // step):
        if points[i][1] == 0:
            points[i][1] = 0.01
        ratio = (c * (points[i][0]) ** r) / points[i][1]
        if abs(ratio - 1) > 0.31:
            precision += 1
    precision /= points_quantity
    if precision > 0.2 or points[i][1] < 0.005:
        print("It's faster than O(n^" + str(r) + ")")
        return False
    print("It's O(n^" + str(r) + ") with c = " + str(c))
    return True


def set_points(total_time):
    height = (size_max - size_min) // step
    # points[][0] = size
    # points[][1] = avg_time
    points = [[0 for x in range(2)] for y in range(height + 1)]  # matrix
    counter = 0
    global tab
    tab = []
    for size in range(size_min, size_max, step):
        # how many times algorithm should be run for one size
        # higher number = higher point_precision
        for i in range(0, point_precision + 1):
            tab = rand(size, 100000)
            algorithm(size)
        print_prof_data()
        clear_prof_data()
        # print('%d, %.3f' % (size, avg_time))
        points[counter][0] = size
        points[counter][1] = avg_time
        try:
            total_time += avg_time
            if total_time > timeout:
                raise RuntimeError()
        except RuntimeError:
            print("Time limit reached. Check last statement")
            exit()
        counter += 1
    return points


#   complexity == 1  -  O(2^n)
#   complexity == 2  -  O(n^3)
#   complexity == 3  -  O(n^2)
#   complexity == 4  -  O(n)

def count_time(c, size):
    result = 0
    if complexity == 1:
        result = c * (2 ** size)
    elif complexity == 2:
        result = c * (size ** 3)
    elif complexity == 3:
        result = c * (size ** 2)
    elif complexity == 4:
        result = c * size
    return result


def count_size(c, time, complexity):
    result = 0
    if complexity == 1:
        result = math.log((time / c), 2)
    elif complexity == 2:
        result = (time / c) ** (1 / 3)
    elif complexity == 3:
        result = (time / c) ** (1 / 2)
    elif complexity == 4:
        result = time / c
    return result


# n in range (1 000 - 40 000), 100 points QUICKSORT O(n^1)
# n in range (100 - 2000), 40 points BUBBLESORT O(n^2)
# n in range (100 - 450), 15 points ALGORITH_N_TO_3 O(n^3)
# n in range (10 - 25), 15 points HANOI O(2^n)
# O(nlog(n)) is too fast, problem with memory for list


def main():
    global arg_function
    global my_function

    parser = argparse.ArgumentParser()
    parser.add_argument("timeout",
                        help="Max time for counting one point", type=int)
    parser.add_argument("module_path", help="path of tested program "
                                            "(use . not /)")
    parser.add_argument("function_name", help="name of tested function")
    parser.add_argument("generate_args_function",
                        help="function which generate arguments "
                             "for tested function")
    parser.add_argument("-point_precision",
                        help="How many times algorithm should be run for "
                             "a single point", type=int, default=1)
    args = parser.parse_args()

    global timeout
    timeout = args.timeout
    global point_precision
    point_precision = args.point_precision

    module_path = args.module_path
    module = importlib.import_module(module_path)

    function_name = args.function_name
    arg_function = getattr(module, args.generate_args_function)
    my_function = getattr(module, function_name)

    global c
    c = 0
    global total_time
    total_time = 0
    global size_max
    size_max = 25
    global size_min
    size_min = 10
    global points_quantity
    points_quantity = 15
    global step
    step = (size_max - size_min) // points_quantity
    global complexity

    print("I'm checking O(2^n) with size_min = " + str(size_min) +
          ", size_max = " + str(size_max) + ", points_quantity = " +
          str(points_quantity))
    if step == 0:
        step = 1
        global points
    points = set_points(total_time)
    # checking O(2^n)
    if check_2_to_n() is False:
        # checking O(n^r)
        size_max = 450
        size_min = 100
        points_quantity = 15
        print("I'm checking O(n^3) with size_min = " + str(size_min) +
              ", size_max = " + str(size_max) + ", points_quantity = " +
              str(points_quantity))
        step = (size_max - size_min) // points_quantity
        if step == 0:
            step = 1
        points = set_points(total_time)
        global middle_point
        middle_point = points_quantity // 2
        if check_exp_to_r(3) is False:
            size_min = 100  # was 1000
            size_max = 2000  # was 5000
            points_quantity = 40
            print("I'm checking O(n^2) with size_min = " + str(size_min) +
                  ", size_max = " + str(size_max) +
                  ", points_quantity = " + str(points_quantity))
            step = (size_max - size_min) // points_quantity
            if step == 0:
                step = 1
            points = set_points(total_time)
            middle_point = points_quantity // 2
            if check_exp_to_r(2) is False:
                size_min = 1000  # 50000
                size_max = 35000  # 500000
                points_quantity = 100
                print("I'm checking O(n) with size_min = " + str(size_min) +
                      ", size_max = " + str(size_max) +
                      ", points_quantity = " + str(points_quantity))
                step = (size_max - size_min) // points_quantity
                if step == 0:
                    step = 1
                middle_point = points_quantity // 2
                step = (size_max - size_min) // points_quantity
                points = set_points(total_time)
                if check_exp_to_r(1) is False:
                    print("It's O(log(n))")
                    exit()
                else:
                    complexity = 4
            else:
                complexity = 3
        else:
            complexity = 2
    else:
        complexity = 1

    choice = 1
    while choice != 3:
        choice = int(input(
            "Choose option:\n"
            "0 - type size and count needed time for your algorithm\n"
            "1 - type time and count size that you can use in this time\n"
            "2 - show plot with counted points\n"
            "3 - exit program\n"))
        if choice == 0:
            size = int(input("Type size: "))
            print("Needed time: " + str(count_time(c, size)))
        elif choice == 1:
            max_time = float(input("Type time: "))
            print("Max size: " + str(count_size(c, max_time, complexity)))
        elif choice == 2:
            plt.scatter(*zip(*points))
            plt.ylabel('time')
            plt.xlabel('size')
            plt.show()
        elif choice == 3:
            print("Exiting program")
            exit()


if __name__ == "__main__":
    main()
