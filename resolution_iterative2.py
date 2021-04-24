from collections import defaultdict
from copy import deepcopy


class Resolution:
    def __init__(self, input_file: str = "input.txt", output_file: str = "output.txt"):
        self.num_query = 0
        self.num_kb = 0
        self.knowledge_base = {}
        self.queries = []
        self.read_input(input_file)
        result = self.resolve_queries()
        self.visited = set()

        self.write_output(output_file, result)
        pass

    def read_input(self, input_file):
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
            for _ in range(self.num_kb):
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
                        arguments = tuple(remaining.split(','))
                        cnf[predicate].add(arguments)
                    statement = [horn_clause[1]]

                predicate, remaining = statement[0][:-1].split('(')
                arguments = tuple(remaining.split(','))
                cnf[predicate].add(arguments)

                for predicate, _ in cnf.items():
                    knowledge_base[predicate].append(cnf)

            self.knowledge_base = knowledge_base
            self.queries = queries

    @staticmethod
    def write_output(output_file: str, data: str):
        with open(output_file, 'w+') as file:
            file.write(data)

    @staticmethod
    def dict_hash(d):
        if isinstance(d, (list, tuple)):
            return hash(tuple([Resolution.dict_hash(e) for e in d]))
        elif isinstance(d, (set,)):
            return hash(tuple([Resolution.dict_hash(e) for e in sorted(d)]))
        elif not isinstance(d, (dict, defaultdict)):
            return hash(d)

        new_d = deepcopy(d)
        for k, v in new_d.items():
            new_d[k] = Resolution.dict_hash(v)

        return hash(tuple(frozenset(sorted(new_d.items()))))

    @staticmethod
    def get_negative_query(query) -> tuple:
        if query[0][0] == '~':
            negative_query = (query[0][1:], query[1])
        else:
            negative_query = ('~' + query[0], query[1])
        return negative_query

    @staticmethod
    def is_unifiable(arguments1: tuple, arguments2: tuple) -> tuple:
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
                # This Case should never come in our project
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
    def perform_assignment(statement: dict, assignment: dict, prev_statement=None):
        # Check variable name used in prev_statement, if exists
        prev_statement_variables = set()
        if prev_statement is not None:
            for _, arguments_set in prev_statement.items():
                for arguments in arguments_set:
                    for argument in arguments:
                        if argument[0].islower():
                            prev_statement_variables.add(argument)

        assigned_statement = {}
        for predicate, arguments_set in statement.items():
            arguments_set_copy = set()
            for arguments in arguments_set:
                arguments_copy = list(arguments)
                for i in range(len(arguments)):
                    if arguments[i] in assignment.keys():
                        arguments_copy[i] = assignment[arguments[i]]
                    elif arguments[i] in prev_statement_variables:

                        arguments_copy[i] = arguments_copy[i] + arguments_copy[i][0]
                arguments_set_copy.add(tuple(arguments_copy))
            assigned_statement[predicate] = arguments_set_copy

        return assigned_statement

    @staticmethod
    def unify(statement1: dict, statement2: dict) -> dict:
        for predicate, arguments_set in deepcopy(statement1).items():
            negative_predicate, _ = Resolution.get_negative_query((predicate, tuple()))
            if negative_predicate in statement2.keys():
                for args in deepcopy(statement2[negative_predicate]):
                    if args in arguments_set:
                        statement1[predicate].remove(args)
                        statement2[negative_predicate].remove(args)

        unified_statement = defaultdict(set)
        for predicate, arguments_set in statement1.items():
            if arguments_set:
                unified_statement[predicate].update(arguments_set)
        for predicate, arguments_set in statement2.items():
            if arguments_set:
                unified_statement[predicate].update(arguments_set)

        return unified_statement

    @staticmethod
    def unify2(statement1, statement2):
        # Keep unifying until no more unification exists
        flag = True
        while flag:
            flag = False
            arg1_assignments = {}
            arg2_assignments = {}
            for predicate1, arguments_set1 in statement1.items():
                for predicate2, arguments_set2 in statement2.items():
                    if Resolution.get_negative_query((predicate1, None)) == (predicate2, None):
                        for arguments1 in arguments_set1:
                            for arguments2 in arguments_set2:
                                unifiable, arg1_assignments, arg2_assignments = Resolution.is_unifiable(arguments1,
                                                                                                        arguments2)
                                if unifiable:
                                    flag = True
                                    break
                                else:
                                    arg1_assignments = {}
                                    arg2_assignments = {}
                            else:
                                continue
                            break
                        else:
                            continue
                        break
                else:
                    continue
                break

            if not flag:
                break
            # Perform the found assignment
            statement1 = Resolution.perform_assignment(statement1, arg1_assignments)
            statement2 = Resolution.perform_assignment(statement2, arg2_assignments, statement1)

            # Eliminate opposite predicates
            for predicate, arguments_set in deepcopy(statement1).items():
                negative_predicate, _ = Resolution.get_negative_query((predicate, tuple()))
                if negative_predicate in statement2.keys():
                    for args in deepcopy(statement2[negative_predicate]):
                        if args in arguments_set:
                            statement1[predicate].remove(args)
                            statement2[negative_predicate].remove(args)

            updated_statement1 = defaultdict(set)
            updated_statement2 = defaultdict(set)
            for predicate, arguments_set in statement1.items():
                if arguments_set:
                    updated_statement1[predicate].update(arguments_set)
            for predicate, arguments_set in statement2.items():
                if arguments_set:
                    updated_statement2[predicate].update(arguments_set)
            statement1 = updated_statement1
            statement2 = updated_statement2

        # Final merge of the two statements
        unified_statement = defaultdict(set)
        for predicate, arguments_set in statement1.items():
            if arguments_set:
                unified_statement[predicate].update(arguments_set)
        for predicate, arguments_set in statement2.items():
            if arguments_set:
                unified_statement[predicate].update(arguments_set)

        return unified_statement

    def apply_resolution(self, initial_statement) -> bool:

        predicate, arguments_set = next(iter(initial_statement.items()))
        arguments = next(iter(arguments_set))
        query = (predicate, arguments)
        negative_query = Resolution.get_negative_query(query)
        visited = set()
        stack = [(initial_statement, query, statement, arguments)
                 for statement in self.knowledge_base[negative_query[0]]
                 for arguments in statement[negative_query[0]]]
        while stack:
            initial_statement, query, statement, arguments = stack.pop(-1)
            visited.add(self.dict_hash((initial_statement, query, statement, arguments)))

            negative_query = Resolution.get_negative_query(query)

            unifiable, _, _ = Resolution.is_unifiable(negative_query[1], arguments)
            if unifiable:
                # Unify Statements
                unified_statement = Resolution.unify2(initial_statement, statement)

                if not unified_statement:
                    return True

                initial_statement = unified_statement

                predicate, arguments_set = next(iter(initial_statement.items()))
                arguments = next(iter(arguments_set))
                query = (predicate, arguments)
                negative_query = Resolution.get_negative_query(query)

                for statement in self.knowledge_base[negative_query[0]]:
                    for arguments in statement[negative_query[0]]:
                        if self.dict_hash((initial_statement, query, statement, arguments)) not in visited:
                            stack.append((initial_statement, query, statement, arguments))
        return False

    def resolve_queries(self) -> str:
        result = []
        for query in self.queries:
            negative_query = Resolution.get_negative_query(query)
            self.visited = set()
            initial_statement = {negative_query[0]: {negative_query[1]}}
            if initial_statement in self.knowledge_base[negative_query[0]]:
                result.append(False)
            else:
                self.knowledge_base[negative_query[0]].append(initial_statement)
                result.append(self.apply_resolution(initial_statement=initial_statement))
                index = self.knowledge_base[negative_query[0]].index(initial_statement)
                self.knowledge_base[negative_query[0]].pop(index)
                if not self.knowledge_base[negative_query[0]]:
                    self.knowledge_base.pop(negative_query[0])

        return '\n'.join(map(lambda x: str(x).upper(), result))


if __name__ == "__main__":
    Resolution()
