from collections import defaultdict
from copy import deepcopy
from time import sleep, time


class Resolution:
    def __init__(self, input_file: str = "input.txt", output_file: str = "output.txt"):
        self.num_query = 0
        self.num_kb = 0
        self.knowledge_base = {}
        self.queries = []
        self.read_input(input_file)
        result = self.resolve_queries()
        # print("Result = {}".format(result.replace("\n", ", ")))
        self.write_output(output_file, result)

    def read_input(self, input_file: str):
        """
        Reads the input file and updates the class instance variables
        :param input_file: input file name with path
        :return:
        """

        with open(input_file, 'r+') as file:
            self.num_query = int(file.readline())
            queries = []
            for _ in range(self.num_query):
                line = file.readline().strip().replace(" ", "")
                line = line[:-1]
                predicate, remaining = line.split("(")
                arguments = tuple(remaining.split(','))
                queries.append((predicate, arguments))

            knowledge_base = defaultdict(list)
            self.num_kb = int(file.readline())
            for index in range(self.num_kb):
                line = file.readline().strip().replace(" ", "")
                horn_clause = line.split("=>")
                statement = horn_clause[0].split("&")
                cnf = defaultdict(set)
                if len(horn_clause) == 2:
                    for literal in statement:
                        if literal[0] == '~':
                            literal = literal[1:-1]
                        else:
                            literal = '~' + literal[:-1]

                        predicate, remaining = literal.split('(')
                        arguments = tuple(map(lambda x: x + str(index) if x.islower() else x, remaining.split(',')))
                        cnf[predicate].add(arguments)
                    statement = [horn_clause[1]]

                predicate, remaining = statement[0][:-1].split('(')
                arguments = tuple(map(lambda x: x + str(index) if x.islower() else x, remaining.split(',')))
                cnf[predicate].add(arguments)

                for predicate, _ in cnf.items():
                    knowledge_base[predicate].append(cnf)

            self.knowledge_base = knowledge_base
            self.queries = queries

    @staticmethod
    def write_output(output_file: str, data: str):
        """
        Writes the result in the output file
        :param output_file: output filename with path
        :param data: string data to be written
        :return:
        """

        with open(output_file, 'w+') as file:
            file.write(data)

    @staticmethod
    def any_hash(obj) -> int:
        """
        any_hash is a recursive hashing function which creates hash of
        any mutable or immutable object passed to it.
        :param obj:
        :return: int hash value of the object
        """

        if isinstance(obj, (list, tuple)):
            return hash(tuple([Resolution.any_hash(e) for e in obj]))
        elif isinstance(obj, (set,)):
            return hash(tuple([Resolution.any_hash(e) for e in sorted(obj)]))
        elif not isinstance(obj, (dict, defaultdict)):
            return hash(obj)

        new_obj = deepcopy(obj)
        for k, v in new_obj.items():
            new_obj[k] = Resolution.any_hash(v)

        return hash(tuple(frozenset(sorted(new_obj.items()))))

    @staticmethod
    def make_hashable(statement):
        hashable_statement = {}
        variable_index = 0
        for predicate, arguments_set in sorted(statement.items()):
            arguments_set_copy = set()
            for arguments in sorted(arguments_set):
                arguments_copy = list(arguments)
                for i in range(len(arguments)):
                    if arguments[i].islower():
                        arguments_copy[i] = 'var' + str(variable_index)
                        variable_index += 1
                arguments_set_copy.add(tuple(arguments_copy))
            hashable_statement[predicate] = arguments_set_copy
        pass

    @staticmethod
    def str_hash(statement):
        result = []
        for predicate, arguments_set in sorted(statement.items()):
            for arguments in sorted(arguments_set):
                result.append(predicate + str(arguments))
        return ' '.join(result)

    @staticmethod
    def str_hash2(statement):
        result = []
        for predicate, arguments_set in sorted(statement.items()):
            for arguments in sorted(arguments_set):
                result.append(predicate + str(arguments))
        return ' '.join(result)

    @staticmethod
    def get_negative_predicate(predicate: str) -> str:
        """
        Returns the negated query.
        :param predicate: predicate
        :return: negated predicate
        """

        if predicate.startswith('~'):
            return predicate[1:]
        else:
            return '~' + predicate

    @staticmethod
    def is_unifiable(arguments1: tuple, arguments2: tuple) -> tuple:

        if len(arguments1) != len(arguments2):
            return False, None

        # Stack structure:
        # 1. remaining_arguments1
        # 2. remaining_arguments2
        # 3. unifier
        stack = [(list(arguments1), list(arguments2), {})]
        while stack:
            remaining_arguments1, remaining_arguments2, unifier = stack.pop(-1)
            unifier_instances = []
            if not remaining_arguments1 and not remaining_arguments2:
                return True, unifier
            elif remaining_arguments1[0].islower() and remaining_arguments2[0].islower():
                if remaining_arguments1[0] not in unifier.keys() and remaining_arguments1[0] not in unifier.values():
                    unifier_copy = deepcopy(unifier)
                    unifier_copy[remaining_arguments1[0]] = remaining_arguments2[0]
                    unifier_instances.append(unifier_copy)

                if remaining_arguments2[0] not in unifier.keys() and remaining_arguments2[0] not in unifier.values():
                    unifier_copy = deepcopy(unifier)
                    unifier_copy[remaining_arguments2[0]] = remaining_arguments1[0]
                    unifier_instances.append(unifier_copy)

            elif remaining_arguments1[0].islower() and not remaining_arguments2[0].islower():
                unifier_copy = deepcopy(unifier)
                for key, value in unifier.items():
                    if remaining_arguments1[0] == value:
                        unifier_copy[key] = remaining_arguments2[0]
                unifier_copy[remaining_arguments1[0]] = remaining_arguments2[0]
                unifier_instances.append(unifier_copy)

            elif not remaining_arguments1[0].islower() and remaining_arguments2[0].islower():
                unifier_copy = deepcopy(unifier)
                for key, value in unifier.items():
                    if remaining_arguments2[0] == value:
                        unifier_copy[key] = remaining_arguments1[0]
                unifier_copy[remaining_arguments2[0]] = remaining_arguments1[0]
                unifier_instances.append(unifier_copy)

            elif not remaining_arguments1[0].islower() and not remaining_arguments2[0].islower():
                if remaining_arguments1[0] == remaining_arguments2[0]:
                    unifier_copy = deepcopy(unifier)
                    unifier_instances.append(unifier_copy)

            # Append to stack
            for unifier in unifier_instances:
                # Substituting the change in the argument lists
                new_remaining_arguments1 = list(
                    map(lambda x: unifier[x] if x in unifier.keys() else x, remaining_arguments1))
                new_remaining_arguments2 = list(
                    map(lambda x: unifier[x] if x in unifier.keys() else x, remaining_arguments2))

                # Appending to stack
                stack.append((new_remaining_arguments1[1:], new_remaining_arguments2[1:], deepcopy(unifier)))

        return False, None

    @staticmethod
    def is_unifiable2(arguments1: tuple, arguments2: tuple) -> tuple:
        """
        Checks if two argument sequences are unifiable or not.
        E.g. ~A(x,y) v B(x) AND A(H, M) v C(z)
        arguments1 = (x, y), arguments2 = (H, M)
        It will return statement1_assignments = {x: H, y: M}, statement2_assignments = {}

        :param arguments1: argument sequence of 1st expression
        :param arguments2: argument sequence of 2nd expression.
        :return: (can_be_unified: bool, statement1_assignment2: dict, statement2_assignments: dict)
        """

        if len(arguments1) != len(arguments2):
            return False, None, None
        arguments1 = list(arguments1)
        arguments2 = list(arguments2)
        arg1_assignments = {}
        arg2_assignments = {}
        for i in range(len(arguments1)):
            if arguments1[i][0].isupper() and arguments2[i][0].isupper():
                if arguments1[i] != arguments2[i]:
                    return False, None, None
            elif arguments1[i][0].isupper() and arguments2[i][0].islower():
                variable_name = arguments2[i]
                for j in range(len(arguments2)):
                    if arguments2[j] == variable_name:
                        if j < i:
                            if arguments1[j][0].isupper() and arguments1[j] != arguments1[i]:
                                return False, {}, {}
                            if arguments1[j][0].islower():
                                for k in range(len(arguments1)):
                                    if arguments1[k] == arguments1[j]:
                                        arguments1[k] = arguments1[i]
                        arguments2[j] = arguments1[i]
                        arg2_assignments[variable_name] = arguments1[i]

            elif arguments1[i][0].islower() and arguments2[i][0].isupper():
                variable_name = arguments1[i]
                for j in range(len(arguments1)):
                    if arguments1[j] == variable_name:
                        if j < i:
                            if arguments2[j][0].isupper() and arguments2[j] != arguments2[i]:
                                return False, {}, {}
                            if arguments2[j][0].islower():
                                for k in range(len(arguments2)):
                                    if arguments2[k] == arguments2[j]:
                                        arguments2[k] = arguments2[i]
                        arguments1[j] = arguments2[i]
                        arg1_assignments[variable_name] = arguments2[i]

            elif arguments1[i][0].islower() and arguments2[i][0].islower():
                variable_name1 = arguments1[i]
                variable_name2 = arguments2[i]
                arguments1_copy = deepcopy(arguments1)
                arguments2_copy = deepcopy(arguments2)
                execute_other_option_flag = False
                common_variable_name = "_" + variable_name1
                for j in range(len(arguments1)):
                    if arguments1[j] == variable_name1:
                        arguments1[j] = common_variable_name
                    if arguments2[j] == variable_name2:
                        if j < i and arguments2[j] != common_variable_name[1:]:
                            execute_other_option_flag = True
                            break
                        arguments2[j] = common_variable_name
                        arg2_assignments[variable_name2] = common_variable_name[1:]
                else:
                    pass
                if execute_other_option_flag:
                    arguments1 = arguments1_copy
                    arguments2 = arguments2_copy
                    common_variable_name = "_" + variable_name2
                    for j in range(len(arguments2)):
                        if arguments2[j] == variable_name2:
                            arguments2[j] = common_variable_name
                        if arguments1[j] == variable_name1:
                            arguments1[j] = common_variable_name
                            arg1_assignments[variable_name1] = common_variable_name[1:]

                for j in range(len(arguments1)):
                    if arguments1[j][0] == '_':
                        arguments1[j] = arguments1[j][1:]
                    if arguments2[j][0] == '_':
                        arguments2[j] = arguments2[j][1:]
        return arguments1 == arguments2, arg1_assignments, arg2_assignments

    @staticmethod
    def perform_assignment(statement: dict, unifier: dict, elimination_literal: tuple = None):
        """
        Perform assignment on the statement according to the unifier.
        Also eliminates any literal from the statement.

        :param statement: statement on which assignment has to be performed
        :param unifier:
        :param elimination_literal:
        :return: the assigned statement
        """

        # Generate assigned statement
        assigned_statement = {}
        for predicate, arguments_set in statement.items():
            arguments_set_copy = set()
            for arguments in arguments_set:
                arguments_copy = list(arguments)
                for i in range(len(arguments)):
                    if arguments[i] in unifier.keys():
                        arguments_copy[i] = unifier[arguments[i]]
                arguments_set_copy.add(tuple(arguments_copy))
            assigned_statement[predicate] = arguments_set_copy

        # Remove the elimination literal, if given
        if elimination_literal is not None:
            elimination_literal_arguments = tuple(
                map(lambda x: unifier[x] if x in unifier else x, elimination_literal[1]))
            assigned_statement[elimination_literal[0]].remove(elimination_literal_arguments)
            if not assigned_statement[elimination_literal[0]]:
                assigned_statement.pop(elimination_literal[0])

        return assigned_statement

    @staticmethod
    def unify(statement1, statement2):
        """
        Merges the two statements and also performs factoring of the unified statement before returning
        :param statement1:
        :param statement2:
        :return: unified statement
        """
        # Perform factoring
        while True:
            unifier = None
            statement1_eliminate_literal = None
            for predicate1, arguments_set1 in statement1.items():
                predicate2 = Resolution.get_negative_predicate(predicate1)
                if predicate2 in statement2:
                    for arguments_set2 in statement2[predicate2]:
                        for arguments1 in arguments_set1:
                            for arguments2 in arguments_set2:
                                is_unifiable, unifier = Resolution.is_unifiable(arguments1, arguments2)
                                if is_unifiable:
                                    statement1_eliminate_literal = (predicate1, arguments1)
                                    break
                            else:
                                continue
                            break
                        else:
                            continue
                        break
                    else:
                        continue
                    break

            if unifier is not None:
                statement1 = Resolution.perform_assignment(statement1, unifier, statement1_eliminate_literal)
                statement2 = Resolution.perform_assignment(statement2, unifier)
            else:
                break

        # Merge of the two statements
        unified_statement = defaultdict(set)
        for predicate, arguments_set in statement1.items():
            if arguments_set:
                unified_statement[predicate].update(arguments_set)
        for predicate, arguments_set in statement2.items():
            if arguments_set:
                unified_statement[predicate].update(arguments_set)

        return unified_statement

    def apply_resolution(self, initial_statement) -> bool:
        """
        Apply resolution starting from the initial statement
        :param initial_statement:
        :return: boolean value if the requested query is True or False
        """

        predicate, arguments_set = next(iter(initial_statement.items()))
        arguments = next(iter(arguments_set))
        initial_literal = (predicate, arguments)
        negative_predicate = Resolution.get_negative_predicate(predicate)

        # Stack structure:
        # 1. initial_statement (dict):
        # 2. initial_literal (tuple -> (predicate: str, arguments: tuple)): the literal in initial_statement
        # which is chosen to be unified with the kb_literal
        # 3. kb_statement: statement from kb which is chosen to resolve with the initial_statement
        # 4. kb_literal: the literal in kb_statement which is chosen to be unified with the initial_literal
        # 5. visited:
        stack = [(initial_statement, initial_literal, deepcopy(kb_statement),
                  (negative_predicate, deepcopy(kb_literal_arguments)))
                 for kb_statement in self.knowledge_base[negative_predicate]
                 for kb_literal_arguments in kb_statement[negative_predicate]]
        visited = set()
        depth = 0
        while stack:
            depth += 1
            initial_statement, initial_literal, kb_statement, kb_literal = stack.pop(-1)
            initial_statement_hash = Resolution.str_hash(initial_statement)
            visited.add(initial_statement_hash)

            # TODO: Remove this code
            # if depth == 4:
            #     exit(0)

            is_unifiable, unifier = Resolution.is_unifiable(initial_literal[1], kb_literal[1])
            if is_unifiable:
                assigned_initial_statement = Resolution.perform_assignment(initial_statement, unifier,
                                                                           initial_literal)
                assigned_kb_statement = Resolution.perform_assignment(kb_statement, unifier, kb_literal)
                resolvent_statement = Resolution.unify(assigned_initial_statement, assigned_kb_statement)

                print(("initial_statement = {}, unifying_initial_literal = {}\nkb_statement = {}, "
                       "unifying_kb_literal = {}\nunifier = {}\nresolvent_statement = {}\nvisited = {}\n")
                      .format(dict(initial_statement), initial_literal, dict(kb_statement), kb_literal, unifier,
                              dict(resolvent_statement), visited))

                # Return True if Resolution completed i.e., statement contradicted
                if not resolvent_statement:
                    print("DEPTH PROCESSED: {}".format(depth))
                    return True

                elif Resolution.str_hash(resolvent_statement) not in visited:
                    # Append the next available options to stack
                    predicate, arguments_set = next(iter(resolvent_statement.items()))
                    negative_predicate = Resolution.get_negative_predicate(predicate)
                    arguments = next(iter(arguments_set))
                    resolvent_literal = (predicate, arguments)
                    for kb_statement in self.knowledge_base[negative_predicate]:
                        for kb_literal_arguments in kb_statement[negative_predicate]:
                            kb_literal = (negative_predicate, deepcopy(kb_literal_arguments))
                            stack.append((deepcopy(resolvent_statement), resolvent_literal,
                                          deepcopy(kb_statement), kb_literal))

        print("DEPTH PROCESSED: {}".format(depth))
        return False

    def resolve_queries(self) -> str:
        """
        Resolve the queries one by one
        :return: Boolean Array Str data for all the processed queries
        """

        result = []
        for query in self.queries:
            start = time()
            negative_predicate = Resolution.get_negative_predicate(query[0])
            negated_query = {negative_predicate: {query[1]}}
            if negated_query in self.knowledge_base[negative_predicate]:
                result.append(False)
            else:
                self.knowledge_base[negative_predicate].append(negated_query)

                result.append(self.apply_resolution(initial_statement=negated_query))

                index = self.knowledge_base[negative_predicate].index(negated_query)
                self.knowledge_base[negative_predicate].pop(index)
                if not self.knowledge_base[negative_predicate]:
                    self.knowledge_base.pop(negative_predicate)
            end = time()
            print("RESULT: {}, query: {}, time taken: {} secs".format(result[-1], query, end - start))

        return '\n'.join(map(lambda x: str(x).upper(), result))


if __name__ == "__main__":
    Resolution(input_file='test_data1/_input0.txt')
