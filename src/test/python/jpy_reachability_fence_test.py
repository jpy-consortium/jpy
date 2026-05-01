"""
jpy_reachability_fence_test.py
===============================
Stress tests for the Reference.reachabilityFence guards in PyObject.

Problem
-------
When a PyObject wrapper is used transiently — e.g. the result of getAttribute()
is immediately passed to callMethod(), getIntValue(), str(), etc. — JLS §12.6.1
permits the JIT to treat the wrapper as reachability-dead once getPointer() has
copied the native pointer into a long.  At that point the GC may collect the
wrapper and the cleanup thread may Py_DECREF the underlying PyObject* while JNI
is still using it, producing a SIGSEGV (use-after-free).

Approach
--------
Each test method defines a Python object with specific attributes, starts a
background GC-pressure thread (continuously allocating to trigger young-gen GC),
then hammers a particular PyObject method path at high iteration count.

Without the Reference.reachabilityFence fix these tests crash the JVM with
SIGSEGV inside libpython.  With the fix they must complete without error.
"""

import unittest

import jpyutil

# Use a small heap so GC fires frequently, exposing the race window.
jpyutil.init_jvm(jvm_maxmem='128M', jvm_classpath=['target/classes', 'target/test-classes'])
import jpy

ITERATIONS = 500_000


class TestReachabilityFence(unittest.TestCase):

    def setUp(self):
        self.Fixture = jpy.get_type(
            'org.jpy.fixtures.ReachabilityFenceTestFixture')
        self.assertIsNotNone(self.Fixture)

    def tearDown(self):
        self.Fixture.stopAllocator()

    def _run_with_gc_pressure(self, stress_fn):
        """Helper: start allocator, run the stress function, stop allocator."""
        self.Fixture.startAllocator()
        try:
            stress_fn()
        finally:
            self.Fixture.stopAllocator()

    # ------------------------------------------------------------------
    # Test: getAttribute + callMethod
    # ------------------------------------------------------------------
    def test_stress_call_method(self):
        """getAttribute('__call__') -> transient.callMethod('__call__')"""

        class _Holder:
            def __call__(self):
                return 42

        holder = _Holder()
        self._run_with_gc_pressure(
            lambda: self.Fixture.stressCallTransient(holder, ITERATIONS))

    # ------------------------------------------------------------------
    # Test: getAttribute + getIntValue
    # ------------------------------------------------------------------
    def test_stress_get_int_value(self):
        """getAttribute('value') -> transient.getIntValue()"""

        class _Holder:
            value = 99

        holder = _Holder()
        self._run_with_gc_pressure(
            lambda: self.Fixture.stressGetIntValue(holder, ITERATIONS))

    # ------------------------------------------------------------------
    # Test: getAttribute + getStringValue
    # ------------------------------------------------------------------
    def test_stress_get_string_value(self):
        """getAttribute('name') -> transient.getStringValue()"""

        class _Holder:
            name = "hello"

        holder = _Holder()
        self._run_with_gc_pressure(
            lambda: self.Fixture.stressGetStringValue(holder, ITERATIONS))

    # ------------------------------------------------------------------
    # Test: getAttribute + str()
    # ------------------------------------------------------------------
    def test_stress_str(self):
        """getAttribute('value') -> transient.str()"""

        class _Holder:
            value = 42

        holder = _Holder()
        self._run_with_gc_pressure(
            lambda: self.Fixture.stressStr(holder, ITERATIONS))

    # ------------------------------------------------------------------
    # Test: getAttribute + repr()
    # ------------------------------------------------------------------
    def test_stress_repr(self):
        """getAttribute('value') -> transient.repr()"""

        class _Holder:
            value = 42

        holder = _Holder()
        self._run_with_gc_pressure(
            lambda: self.Fixture.stressRepr(holder, ITERATIONS))

    # ------------------------------------------------------------------
    # Test: getAttribute + hash()
    # ------------------------------------------------------------------
    def test_stress_hash(self):
        """getAttribute('name') -> transient.hash()"""

        class _Holder:
            name = "hashme"

        holder = _Holder()
        self._run_with_gc_pressure(
            lambda: self.Fixture.stressHash(holder, ITERATIONS))

    # ------------------------------------------------------------------
    # Test: getAttribute + type-check methods (isInt, isCallable, etc.)
    # ------------------------------------------------------------------
    def test_stress_type_checks(self):
        """getAttribute('value') -> transient.isInt()/isFloat()/isString()/..."""

        class _Holder:
            value = 7

        holder = _Holder()
        self._run_with_gc_pressure(
            lambda: self.Fixture.stressTypeChecks(holder, ITERATIONS))

    # ------------------------------------------------------------------
    # Test: getAttribute + hasAttribute
    # ------------------------------------------------------------------
    def test_stress_has_attribute(self):
        """getAttribute('nested') -> transient.hasAttribute('value')"""

        class _Nested:
            value = 1

        class _Holder:
            nested = _Nested()

        holder = _Holder()
        self._run_with_gc_pressure(
            lambda: self.Fixture.stressHasAttribute(holder, ITERATIONS))

    # ------------------------------------------------------------------
    # Test: getAttribute + call (function-style)
    # ------------------------------------------------------------------
    def test_stress_call(self):
        """getAttribute('compute') -> transient.call('__call__', arg)"""

        class _Holder:
            @staticmethod
            def compute(x):
                return x * 2

        holder = _Holder()
        self._run_with_gc_pressure(
            lambda: self.Fixture.stressCall(holder, ITERATIONS))

    # ------------------------------------------------------------------
    # Test: getAttribute + getObjectValue
    # ------------------------------------------------------------------
    def test_stress_get_object_value(self):
        """getAttribute('value') -> transient.getObjectValue()"""

        class _Holder:
            value = 123

        holder = _Holder()
        self._run_with_gc_pressure(
            lambda: self.Fixture.stressGetObjectValue(holder, ITERATIONS))

    # ------------------------------------------------------------------
    # Test: createProxy + method call on transient proxy (PyProxyHandler)
    # ------------------------------------------------------------------
    def test_stress_proxy(self):
        """createProxy(Computable) -> transient proxy.compute(i)"""

        class _Computable:
            def compute(self, x):
                return x * 2

        obj = _Computable()
        self._run_with_gc_pressure(
            lambda: self.Fixture.stressProxy(obj, ITERATIONS))

    # ------------------------------------------------------------------
    # Test: asDict().containsKey() on transient PyDictWrapper
    # ------------------------------------------------------------------
    def test_stress_dict_contains_key(self):
        """asDict().containsKey('key') on a transient wrapper"""

        d = {"key": 42, "other": 99}
        # Convert to a PyObject-wrapped dict via jpy
        py_dict = jpy.get_type('org.jpy.PyObject').executeCode(
            "{'key': 42, 'other': 99}", jpy.get_type('org.jpy.PyInputMode').EXPRESSION)
        self._run_with_gc_pressure(
            lambda: self.Fixture.stressDictContainsKey(py_dict, ITERATIONS))

    # ------------------------------------------------------------------
    # Test: asDict().keySet() on transient PyDictWrapper
    # ------------------------------------------------------------------
    def test_stress_dict_key_set(self):
        """asDict().keySet() on a transient wrapper"""

        py_dict = jpy.get_type('org.jpy.PyObject').executeCode(
            "{'a': 1, 'b': 2, 'c': 3}", jpy.get_type('org.jpy.PyInputMode').EXPRESSION)
        self._run_with_gc_pressure(
            lambda: self.Fixture.stressDictKeySet(py_dict, ITERATIONS))

    # ------------------------------------------------------------------
    # Test: asDict().copy() on transient PyDictWrapper
    # ------------------------------------------------------------------
    def test_stress_dict_copy(self):
        """asDict().copy() on a transient wrapper"""

        py_dict = jpy.get_type('org.jpy.PyObject').executeCode(
            "{'x': 10}", jpy.get_type('org.jpy.PyInputMode').EXPRESSION)
        self._run_with_gc_pressure(
            lambda: self.Fixture.stressDictCopy(py_dict, ITERATIONS))


if __name__ == '__main__':
    print('\nRunning ' + __file__)
    unittest.main()

