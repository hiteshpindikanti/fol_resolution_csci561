def invert_case(s: str) -> str:
    return ''.join(map(lambda x: x.lower() if x.isupper() else x.upper(), s))


def convert_to_prolog(input_file: str, output_file: str):
    prolog_data = []
    with open(input_file, 'r+') as file:
        num_query = int(file.readline())
        queries = []
        for _ in range(num_query):
            line = file.readline().strip().replace(" ", "")
            line = line[:-1]
            predicate, remaining = line.split("(")
            arguments = tuple(remaining.split(','))
            queries.append((predicate, arguments))
        num_kb = int(file.readline())

        for _ in range(num_kb):
            line = file.readline().strip().replace(" ", "")
            literals = line.split("=>")
            new_line = ""
            if len(literals) == 2:
                new_line += invert_case(literals[1]) + ' :- '

            new_line += ','.join(map(invert_case, literals[0].split("&")))
            prolog_data.append(new_line.replace("~", "\\+ ") + '.')

    with open(output_file, 'w+') as file:
        file.write('\n'.join(sorted(prolog_data)))


convert_to_prolog(input_file='test_data/input4.txt', output_file='prolog_input.txt')