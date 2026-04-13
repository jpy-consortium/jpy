import unittest

import jpyutil

# target/classes   – org.jpy.PyLib / PyObject / PyInputMode used by EvalTestFixture
# target/test-classes – EvalTestFixture itself
jpyutil.init_jvm(jvm_maxmem='512M', jvm_classpath=['target/classes', 'target/test-classes'])
import jpy


class TestPythonExceptionChain(unittest.TestCase):
    """
    Verifies that PyLib_HandlePythonException preserves the full Python
    exception chain when a Python script is executed via Java (EvalTestFixture).

    The chain is formatted by Python's own traceback.format_exception(), so all
    three chaining cases defined by PEP 3134 are exercised:

      - Explicit cause   (raise B from A)
        → "The above exception was the direct cause of the following exception"
      - Implicit context (except A: raise B)
        → "During handling of the above exception, another exception occurred"
      - Suppressed       (raise B from None)
        → only B should appear; A must be absent
    """

    def setUp(self):
        self.fixture = jpy.get_type('org.jpy.fixtures.EvalTestFixture')
        self.assertIsNotNone(self.fixture)

    def _run_script(self, script: str) -> str:
        """Execute a Python snippet through Java and return the RuntimeError message."""
        with self.assertRaises(RuntimeError) as ctx:
            self.fixture.script(script)
        msg = str(ctx.exception)
        # Every Python exception propagated through Java must carry the base prefix
        # so it is immediately recognisable in Java stack traces and logs.
        # Note: the bridge prepends the Java exception class name, so the full
        # message looks like "java.lang.RuntimeException: Error in Python interpreter:\n..."
        self.assertIn("Error in Python interpreter:", msg,
                      f"Expected prefix 'Error in Python interpreter:' not found in:\n{msg}")
        return msg

    def test_explicit_cause(self):
        """raise B from A — both exceptions plus the 'direct cause' phrase must appear."""
        msg = self._run_script(
            "try:\n"
            "    raise TypeError('root cause')\n"
            "except TypeError as e:\n"
            "    raise ValueError('outer error') from e\n"
        )
        self.assertIn("TypeError", msg)
        self.assertIn("root cause", msg)
        self.assertIn("ValueError", msg)
        self.assertIn("outer error", msg)
        # Python's traceback module uses this exact phrase for __cause__
        self.assertIn("direct cause", msg)

    def test_implicit_context(self):
        """Implicit context (no 'from') — both exceptions must appear with the right phrase."""
        msg = self._run_script(
            "try:\n"
            "    raise TypeError('original error')\n"
            "except TypeError:\n"
            "    raise ValueError('replacement error')\n"
        )
        self.assertIn("TypeError", msg)
        self.assertIn("original error", msg)
        self.assertIn("ValueError", msg)
        self.assertIn("replacement error", msg)
        # Python's traceback module uses this exact phrase for __context__
        self.assertIn("During handling of the above exception", msg)

    def test_suppressed_context(self):
        """raise B from None — context is suppressed; only B should appear."""
        msg = self._run_script(
            "try:\n"
            "    raise TypeError('hidden cause')\n"
            "except TypeError:\n"
            "    raise ValueError('only this') from None\n"
        )
        self.assertIn("ValueError", msg)
        self.assertIn("only this", msg)
        # The suppressed cause must NOT leak into the message
        self.assertNotIn("TypeError", msg)
        self.assertNotIn("hidden cause", msg)

    def test_three_level_chain(self):
        """A → B → C explicit chain — all three levels must be present."""
        msg = self._run_script(
            "try:\n"
            "    try:\n"
            "        raise RuntimeError('level 1')\n"
            "    except RuntimeError as e:\n"
            "        raise TypeError('level 2') from e\n"
            "except TypeError as e:\n"
            "    raise ValueError('level 3') from e\n"
        )
        self.assertIn("RuntimeError", msg)
        self.assertIn("level 1", msg)
        self.assertIn("TypeError", msg)
        self.assertIn("level 2", msg)
        self.assertIn("ValueError", msg)
        self.assertIn("level 3", msg)


if __name__ == '__main__':
    print('\nRunning ' + __file__)
    unittest.main()

