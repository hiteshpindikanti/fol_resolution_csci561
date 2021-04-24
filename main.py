from resolution import Resolution
from resolution_iterative2 import Resolution as ResolutionIterative
from os import listdir
import time


def run_all():
    input_file_format = "input"
    expected_output_file_format = "expected_output"
    output_file_format = "output"

    time_taken = []
    num_files = len(list(filter(lambda x: x.startswith('input'), listdir('test_data'))))
    for index in range(1, num_files + 1):
        start = time.time()
        ResolutionIterative(input_file='test_data/{}{}.txt'.format(input_file_format, index),
                            output_file='test_data/{}{}.txt'.format(output_file_format, index))
        end = time.time()
        time_taken.append(end - start)

    for index in range(1, num_files + 1):
        with open('test_data/{}{}.txt'.format(expected_output_file_format, index)) as file:
            expected_output = file.read().strip()
        with open('test_data/{}{}.txt'.format(output_file_format, index)) as file:
            actual_output = file.read().strip()

        print("Test Case {}: {}, Time Taken: {}"
              .format(index, 'PASS' if expected_output == actual_output else 'FAIL', time_taken[index - 1]))


def run_all2():
    input_file_format = "input"
    expected_output_file_format = "expected_output"
    output_file_format = "output"

    time_taken = []
    num_files = len(list(filter(lambda x: x.startswith('input'), listdir('test_data2'))))
    for index in range(1, num_files + 1):
        start = time.time()
        if index not in {3, 25, 11}:
            ResolutionIterative(input_file='test_data2/{}{}.txt'.format(input_file_format, index),
                                output_file='test_data2/{}{}.txt'.format(output_file_format, index))
        end = time.time()
        time_taken.append(end - start)

    for index in range(1, num_files + 1):
        with open('test_data2/{}{}.txt'.format(expected_output_file_format, index)) as file:
            expected_output = file.read().strip()
        with open('test_data2/{}{}.txt'.format(output_file_format, index)) as file:
            actual_output = file.read().strip()

        print("Test Case {}: {}, Time Taken: {}"
              .format(index, 'PASS' if expected_output == actual_output else 'FAIL', time_taken[index - 1]))


if __name__ == "__main__":
    print("--SET 1--")
    run_all()
    print("--SET 2--")
    run_all2()
    # ResolutionIterative(input_file='test_data/input24.txt', output_file='test_data/output24.txt')
    # ResolutionIterative(input_file='test_data/input25.txt', output_file='test_data/output25.txt')
    #ResolutionIterative(input_file='test_data2/input24.txt', output_file='test_data2/output24.txt')
