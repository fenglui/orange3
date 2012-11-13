import functools
import pickle
import unittest

from Orange import data

class PickleTest(unittest.TestCase):
    def setUp(self):
        """ Override __eq__ for Orange objects that do not implement it"""

        self.add_comparator(data.DiscreteVariable,
                            compare_members=("var_type", "name", "values", "ordered", "base_value"))
        self.add_comparator(data.ContinuousVariable,
                            compare_members=("var_type", "name"))
        self.add_comparator(data.StringVariable,
                            compare_members=("var_type", "name"))
        self.add_comparator(data.Domain,
                            compare_members=("attributes", "class_vars", "class_var", "variables", "metas", "anonymous"))

    old_comparators = {}
    def add_comparator(self, class_, compare_members):
        def compare(self, y):
            for m in compare_members:
                if getattr(self, m) != getattr(y, m):
                    return False
            return True

        def hash(self):
            return "".join(map(lambda m : str(getattr(self, m)), compare_members)).__hash__()

        self.old_comparators[class_] = (class_.__eq__, class_.__hash__)
        class_.__eq__ = compare
        class_.__hash__ = hash

    def tearDown(self):
        for c, (eq, hash) in self.old_comparators.items():
            c.__eq__, c.__hash__ = eq, hash

    def assertPicklingPreserves(self, obj):
        for protocol in range(1, pickle.HIGHEST_PROTOCOL + 1):
            obj2 = pickle.loads(pickle.dumps(obj, protocol))
            self.assertEqual(obj, obj2)

def create_pickling_tests(classname, *objs):
    def create_test(descr):
        name, construct_object = descr
        def f(self):
            obj = construct_object()
            self.assertPicklingPreserves(obj)
        return "test_{}".format(name), f

    tests = dict(map(create_test, objs))
    return type(classname, (PickleTest,), tests)

