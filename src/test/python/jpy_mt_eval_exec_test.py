import math
import unittest

import jpyutil

jpyutil.init_jvm(jvm_maxmem='512M', jvm_classpath=['target/classes', 'target/test-classes'])
import jpy

NUM_THREADS = 20


# A CPU-bound task: computing a large number of prime numbers
def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def count_primes(start: int, end: int) -> int:
    count = 0
    for i in range(start, end):
        if is_prime(i):
            count += 1
    return count


def use_circular_java_classes():
    j_child1_class = jpy.get_type("org.jpy.fixtures.CyclicReferenceChild1")
    j_child2_class = jpy.get_type("org.jpy.fixtures.CyclicReferenceChild2")
    j_child2 = j_child2_class()
    j_child1 = j_child1_class.of(8)
    result = j_child1.parentMethod()
    assert result == 88
    assert 888 == j_child1.grandParentMethod()
    j_child1.refChild2(j_child2)
    assert 8 == j_child1.get_x()
    assert 10 == j_child1.y
    assert 100 == j_child1.z


class MultiThreadedTestEvalExec(unittest.TestCase):
    def setUp(self):
        self.fixture = jpy.get_type("org.jpy.fixtures.MultiThreadedEvalTestFixture")
        self.assertIsNotNone(self.fixture)

    def test_inc_baz(self):
        baz = 15
        self.fixture.script("baz = baz + 1; self.assertGreater(baz, 15)", NUM_THREADS)
        # note: this *is* correct wrt python semantics w/ exec(code, globals(), locals())
        # https://bugs.python.org/issue4831 (Note: it's *not* a bug, is working as intended)
        self.assertEqual(baz, 15)

    def test_exec_import(self):
        import sys
        self.assertTrue("json" not in sys.modules)
        self.fixture.script("import json", NUM_THREADS)
        self.assertTrue("json" in sys.modules)

    def test_exec_function_call(self):
        self.fixture.expression("use_circular_java_classes()", NUM_THREADS)

    def test_count_primes(self):
        self.fixture.expression("count_primes(1, 10000)", NUM_THREADS)

    def test_java_threading_jpy_get_type(self):

        py_script = """
j_child1_class = jpy.get_type("org.jpy.fixtures.CyclicReferenceChild1")
j_child2_class = jpy.get_type("org.jpy.fixtures.CyclicReferenceChild2")
j_child2 = j_child2_class()
j_child1 = j_child1_class.of(8)
result = j_child1.parentMethod()
assert result == 88
assert 888 == j_child1.grandParentMethod()
j_child1.refChild2(j_child2)
assert 8 == j_child1.get_x()
assert 10 == j_child1.y
assert 100 == j_child1.z
    """
        self.fixture.script(py_script, NUM_THREADS)

    def test_py_threading_jpy_get_type(self):
        import threading

        test_self = self

        class MyThread(threading.Thread):
            def __init__(self):
                threading.Thread.__init__(self)

            def run(self):
                barrier.wait()
                j_child1_class = jpy.get_type("org.jpy.fixtures.CyclicReferenceChild1")
                j_child2_class = jpy.get_type("org.jpy.fixtures.CyclicReferenceChild2")
                j_child2 = j_child2_class()
                j_child1 = j_child1_class.of(8)
                test_self.assertEqual(88, j_child1.parentMethod())
                test_self.assertEqual(888, j_child1.grandParentMethod())
                test_self.assertIsNone(j_child1.refChild2(j_child2))
                test_self.assertEqual(8, j_child1.get_x())
                test_self.assertEqual(10, j_child1.y)
                test_self.assertEqual(100, j_child1.z)

        barrier = threading.Barrier(NUM_THREADS)
        threads = []
        for i in range(NUM_THREADS):
            t = MyThread()
            t.start()
            threads.append(t)

        for t in threads:
            t.join()


if __name__ == '__main__':
    print('\nRunning ' + __file__)
    unittest.main()
