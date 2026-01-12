import unittest
import sys

import jpyutil

jpyutil.init_jvm(jvm_maxmem='512M', jvm_classpath=['target/test-classes', 'target/classes'])
import jpy


class TestGIL(unittest.TestCase):
    """
    Tests for GIL-related functionality in PyLib
    """

    def setUp(self):
        self.PyLib = jpy.get_type('org.jpy.PyLib')
        self.assertIsNotNone(self.PyLib)

    def test_isGILEnabled(self):
        """
        Test that PyLib.isGILEnabled() returns the correct GIL status.
        Verifies the JNI implementation matches Python's own sys._is_gil_enabled().
        """
        # Get GIL status from Java/JNI
        gil_enabled_from_jni = self.PyLib.isGILEnabled()
        self.assertIsInstance(gil_enabled_from_jni, bool)

        # Get expected GIL status from Python
        # For Python 3.13+ free-threaded builds, check sys._is_gil_enabled()
        # For older versions or standard builds, GIL is always enabled
        if hasattr(sys, '_is_gil_enabled'):
            expected_gil_enabled = sys._is_gil_enabled()
        else:
            # Older Python or standard build - GIL is always enabled
            expected_gil_enabled = True

        # Verify they match
        self.assertEqual(
            gil_enabled_from_jni,
            expected_gil_enabled,
            f"PyLib.isGILEnabled() returned {gil_enabled_from_jni}, "
            f"but Python's sys._is_gil_enabled() indicates {expected_gil_enabled}"
        )

    def test_isGILEnabled_always_returns_boolean(self):
        """
        Test that isGILEnabled() always returns a boolean value.
        """
        result = self.PyLib.isGILEnabled()
        self.assertIsInstance(result, bool)

    def test_isGILEnabled_standard_python(self):
        """
        Test that for standard Python builds (non-free-threaded),
        isGILEnabled() returns True.
        """
        # Check if this is a free-threaded build
        is_free_threaded = hasattr(sys, '_is_gil_enabled')

        if not is_free_threaded:
            # For standard Python builds, GIL should always be enabled
            self.assertTrue(
                self.PyLib.isGILEnabled(),
                "GIL should always be enabled in standard Python builds"
            )


if __name__ == '__main__':
    print('\nRunning ' + __file__)
    unittest.main()

