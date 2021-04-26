from resolution_iterative import Resolution


def create_test_file_1(file_name: str):
    data = "1\nA(Constant)\n"
    predicates = list(map(chr, range(ord('A'), ord('Z') + 1)))
    data = data + str(len(predicates) - 1) + "\n"
    i = 0
    while i < len(predicates) - 1:
        data = data + predicates[i] + "(Constant) => " + predicates[i + 1] + "(Constant)\n"
        i += 1

    with open(file_name, 'w+') as file:
        file.write(data)


def create_test_file_2(file_name: str):
    data = "1\nA(Constant)\n"
    predicates = list(map(chr, range(ord('A'), ord('Z') + 1)))
    data = data + str(len(predicates)) + "\n"
    i = 0
    while i < len(predicates):
        left_str = " & ".join(map(lambda x: x + "(Constant)", predicates[:i] + predicates[i + 1:]))
        data = data + left_str + " => " + predicates[i] + "(Constant)\n"
        i += 1

    with open(file_name, 'w+') as file:
        file.write(data)
    pass


def create_test_file_3(file_name: str):
    data = "1\nA(a)\n"
    predicates = list(map(chr, range(ord('A'), ord('Z') + 1)))
    data = data + str(len(predicates) - 1) + "\n"
    i = 0
    while i < len(predicates) - 1:
        data = "{}{}({}) => {}({})\n".format(data, predicates[i], predicates[i].lower(),
                                             predicates[i + 1], predicates[i].lower())
        i += 1

    with open(file_name, 'w+') as file:
        file.write(data)


def unit_testing(statement1: dict, args1: tuple, statement2: dict, args2: tuple):
    print("statement1 = {}\nstatement2 = {}".format(statement1, statement2))

    unifiable, args1_assignment, args2_assignment = Resolution.is_unifiable(args1, args2)
    print("unifiable = {}\nargs1_assignment = {}\nargs2_assignment = {}"
          .format(unifiable, args1_assignment, args2_assignment))

    assigned_statement1 = Resolution.perform_assignment(statement1, args1_assignment)
    assigned_statement2 = Resolution.perform_assignment(statement2, args2_assignment, assigned_statement1)
    print("assigned_statement1 = {}\nassigned_statement2 = {}".format(assigned_statement1, assigned_statement2))

    unified_statement = Resolution.unify(assigned_statement1, assigned_statement2)
    print('unified_statement = {}'.format(unified_statement))


if __name__ == "__main__":
    # create_test_file_1('test_data1/input9.txt')
    # create_test_file_2('test_data1/input10.txt')
    # create_test_file_3('test_data1/input19.txt')

    _1statement1 = {'~P': {('H', 'T')}}
    _1statement2 = {'R': {('x',), ('y',)}, 'P': {('x', 'y')}}
    _1args1 = ('H', 'T')
    _1args2 = ('x', 'y')

    _2statement1 = {'~A': {('x',)}, 'Z': {('Constant',)}}
    _2statement2 = {'~Z': {('y',)}, 'B': {('x',)}}
    _2args1 = ('Constant',)
    _2args2 = ('y',)

    # unit_testing(statement1=_2statement1, args1=_2args1, statement2=_2statement2, args2=_2args2)

    _3statement1 = {'Z': {('Constant',)}, '~B': {('x',)}}
    _3statement2 = {'B': {('x',)}, '~Z': {('y',)}}
    _3args1 = ('Constant',)
    _3args2 = ('y',)

    # unit_testing(statement1=_3statement1, args1=_3args1, statement2=_3statement2, args2=_3args2)

    _4statement1 = {'A': {('x',)}, '~B': {('x',)}}
    _4statement2 = {'B': {('x',)}, '~A': {('C',)}}

    print(Resolution.unify2(_4statement1, _4statement2))