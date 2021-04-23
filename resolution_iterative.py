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
        if isinstance(d, (list,)):
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
                        arguments2[j] = arguments1[i]
                        arg2_assignments[variable_name] = arguments1[i]

            elif arguments1[i][0].islower() and arguments2[i][0].isupper():
                # This Case should never come in our project
                variable_name = arguments1[i]
                for j in range(len(arguments1)):
                    if arguments1[j] == variable_name:
                        arguments1[j] = arguments2[i]
                        arg1_assignments[variable_name] = arguments2[i]

            elif arguments1[i][0].islower() and arguments2[i][0].islower():
                for j in range(len(arguments1)):
                    variable_name1 = arguments1[i]
                    variable_name2 = arguments2[i]
                    common_variable_name = "_" + variable_name1
                    if arguments1[j] == variable_name1:
                        arguments1[j] = common_variable_name
                    if arguments2[j] == variable_name2:
                        arguments2[j] = common_variable_name
                        arg2_assignments[variable_name2] = common_variable_name[1:]
                for j in range(len(arguments1)):
                    if arguments1[j][0] == '_':
                        arguments1[j] = arguments1[j][1:]
                    if arguments2[j][0] == '_':
                        arguments2[j] = arguments2[j][1:]
        return True, arg1_assignments, arg2_assignments

    @staticmethod
    def perform_assignment(statement: dict, assignment: dict):
        assigned_statement = {}
        for predicate, arguments_set in statement.items():
            arguments_set_copy = set()
            for argument in arguments_set:
                argument_copy = list(argument)
                for i in range(len(argument)):
                    if argument[i] in assignment.keys():
                        argument_copy[i] = assignment[argument[i]]
                arguments_set_copy.add(tuple(argument_copy))
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

    def apply_resolution(self, initial_statement) -> bool:

        while initial_statement:
            hash_key = Resolution.dict_hash(initial_statement)
            if hash_key in self.visited:
                return False
            else:
                self.visited.add(hash_key)

            predicate, arguments_set = next(iter(initial_statement.items()))
            arguments = next(iter(arguments_set))
            query = (predicate, arguments)

            negative_query = Resolution.get_negative_query(query)

            for statement in self.knowledge_base[negative_query[0]]:
                for args in statement[negative_query[0]]:
                    unifiable, arg1_assignments, arg2_assignments = Resolution.is_unifiable(negative_query[1], args)
                    if unifiable:
                        # Perform Unification Assignment on the statements
                        statement_copy = Resolution.perform_assignment(statement, arg2_assignments)
                        initial_statement_copy = Resolution.perform_assignment(initial_statement, arg1_assignments)

                        # Unify Statements
                        unified_statement = Resolution.unify(initial_statement_copy, statement_copy)
                        hash_key = Resolution.dict_hash(unified_statement)
                        if hash_key in self.visited:
                            continue
                        else:
                            initial_statement = unified_statement
                            break
                else:
                    continue
                break

        return True

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
                if result[-1]:
                    index = self.knowledge_base[negative_query[0]].index(initial_statement)
                    self.knowledge_base[negative_query[0]].pop(index)
                    negative_statement = {query[0]: {query[1]}}
                    if negative_statement not in self.knowledge_base[query[0]]:
                        self.knowledge_base[query[0]].append(negative_statement)

        return '\n'.join(map(lambda x: str(x).upper(), result))
