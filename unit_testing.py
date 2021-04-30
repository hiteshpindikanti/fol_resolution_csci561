from resolution_iterative_v2 import Resolution


def test_is_unifiable():
    arguments1 = ('x', 'y')
    arguments2 = ('w', 'w')
    result = Resolution.is_unifiable(arguments1, arguments2)
    print('arguments1 = {}, argument2 = {}, result = {}'.format(arguments1, arguments2, result))

    arguments1 = ('y', 'B', 'x')
    arguments2 = ('x', 'y', 'z')
    result = Resolution.is_unifiable(arguments1, arguments2)
    print('arguments1 = {}, argument2 = {}, result = {}'.format(arguments1, arguments2, result))

    arguments1 = ('x', 'C')
    arguments2 = ('B', 'x')
    result = Resolution.is_unifiable(arguments1, arguments2)
    print('arguments1 = {}, argument2 = {}, result = {}'.format(arguments1, arguments2, result))


def test_unify():
    statement1 = {'A': {('x', 'y'), ('H', 'M')}}
    statement2 = {'A': {('H', 'M')}}
    result = Resolution.unify(statement1, statement2)
    print('statement1 = {}, statement2 = {}, result = {}'.format(statement1, statement2, dict(result)))


def test_str_hash():
    statement = {'A': {('x', 'y'), ('H', 'M')}}
    result = Resolution.str_hash(statement)
    print('statement = {}, result = {}'.format(statement, result))


if __name__ == "__main__":
    # test_is_unifiable()
    # test_unify()
    test_str_hash()
