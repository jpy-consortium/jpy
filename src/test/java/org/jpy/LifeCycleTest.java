package org.jpy;

import org.junit.Assert;
import org.junit.Assume;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TestRule;

public class LifeCycleTest {

    @Rule
    public TestRule testStatePrinter = new TestStatePrinter();

    private static final boolean ON_WINDOWS = System.getProperty("os.name").toLowerCase().contains("windows");

    @Test
    public void testCanStartAndStopWithoutException() {
        // CPython cannot be restarted once finalized (issue #70).  When stopIsNoOp=true,
        // stopPython() skips Py_Finalize, so isPythonRunning() never returns false and the
        // module pointers are stable across restarts.  Skip rather than produce a misleading pass.
        Assume.assumeFalse("Skipped: CPython restart not supported (jpy.stopIsNoOp=true)",
                Boolean.getBoolean("jpy.stopIsNoOp"));
        PyLib.startPython();
        Assert.assertTrue(PyLib.isPythonRunning());
        PyModule sys1 = PyModule.importModule("sys");
        Assert.assertNotNull(sys1);
        final long sys1Pointer = sys1.getPointer();

        PyLib.stopPython();
        if (!ON_WINDOWS) {
            Assert.assertFalse(PyLib.isPythonRunning());
        }

        PyLib.startPython();
        Assert.assertTrue(PyLib.isPythonRunning());

        PyModule sys2 = PyModule.importModule("sys");
        Assert.assertNotNull(sys2);
        final long sys2Pointer = sys2.getPointer();

        if (!ON_WINDOWS) {
            Assert.assertNotEquals(sys1Pointer, sys2Pointer);
        }

        PyLib.stopPython();
        if (!ON_WINDOWS) {
            Assert.assertFalse(PyLib.isPythonRunning());
        }
    }
}
