from resolution_iterative_v3 import Resolution as ResolutionIterative
from os import listdir
import time


def run_all(folder: str):
    input_file_format = "input"
    expected_output_file_format = "expected_output"
    output_file_format = "output"

    time_taken = []
    num_files = len(list(filter(lambda x: x.startswith('input'), listdir(folder))))
    for index in range(1, num_files + 1):
        start = time.time()
        print("Running Test Case {}".format(index))
        ResolutionIterative(input_file='{}/{}{}.txt'.format(folder, input_file_format, index),
                            output_file='{}/{}{}.txt'.format(folder, output_file_format, index))
        end = time.time()
        time_taken.append(end - start)

    for index in range(1, num_files + 1):
        with open('{}/{}{}.txt'.format(folder, expected_output_file_format, index)) as file:
            expected_output = file.read().strip()
        with open('{}/{}{}.txt'.format(folder, output_file_format, index)) as file:
            actual_output = file.read().strip()

        print("Test Case {}: {}, Time Taken: {}"
              .format(index, 'PASS' if expected_output == actual_output else 'FAIL', time_taken[index - 1]))


def run_all2(folder: str):
    input_file_format = "input"
    expected_output_file_format = "expected_output"
    output_file_format = "output"

    time_taken = []
    num_files = len(list(filter(lambda x: x.startswith('input'), listdir(folder))))
    for index in range(1, num_files + 1):
        start = time.time()
        if index not in {3, 25, 11}:
            ResolutionIterative(input_file='{}/{}{}.txt'.format(folder, input_file_format, index),
                                output_file='{}/{}{}.txt'.format(folder, output_file_format, index))
        end = time.time()
        time_taken.append(end - start)

    for index in range(1, num_files + 1):
        with open('{}/{}{}.txt'.format(folder, expected_output_file_format, index)) as file:
            expected_output = file.read().strip()
        with open('{}/{}{}.txt'.format(folder, output_file_format, index)) as file:
            actual_output = file.read().strip()

        print("Test Case {}: {}, Time Taken: {}"
              .format(index, 'PASS' if expected_output == actual_output else 'FAIL', time_taken[index - 1]))


if __name__ == "__main__":
    print("--SET 1--")
    run_all(folder='test_data1')
    print("--SET 2--")
    run_all2(folder='test_data2')
    print("--SET 3--")
    run_all(folder='test_data3')

    # ResolutionIterative(input_file='test_data1/_input0.txt', output_file='test_data1/_output0.txt')
