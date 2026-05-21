package org.jpy.fixtures;

import org.jpy.PyObject;

import java.util.ArrayList;
import java.util.List;

/**
 * Fixture for stress-testing the {@code PyObject} cleanup daemon thread.
 *
 * <p>The fixture holds Java {@link PyObject} wrappers around Python objects,
 * then releases them so the cleanup daemon can {@code Py_DECREF} the underlying
 * Python objects.  Tests verify that all Python objects are freed correctly,
 * promptly, and exactly once.
 */
public class CleanupThreadTestFixture {

    private List<PyObject> held = new ArrayList<>();

    /**
     * Calls the given Python factory callable {@code n} times and holds each
     * returned {@link PyObject} wrapper, keeping the underlying Python object
     * alive (refcount &gt; 0) for as long as this fixture holds the wrapper.
     *
     * @param factory a zero-argument Python callable that returns a Python object
     * @param n       number of wrappers to create and hold
     */
    public void holdPyObjects(PyObject factory, int n) {
        for (int i = 0; i < n; i++) {
            held.add(factory.callMethod("__call__"));
        }
    }

    /**
     * Returns the number of {@link PyObject} wrappers currently held.
     */
    public int heldCount() {
        return held.size();
    }

    /**
     * Releases all held {@link PyObject} wrappers.  The caller is responsible
     * for triggering GC (e.g. via {@code System.gc()}) if it needs the
     * {@link java.lang.ref.WeakReference}s to be enqueued promptly.
     */
    public void releaseAll() {
        held.clear();
    }

    /**
     * Returns {@code true} if the {@code PyObject-cleanup} daemon thread is
     * currently alive.  Used by tests to verify the cleanup thread was started.
     */
    public static boolean isCleanupThreadAlive() {
        return Thread.getAllStackTraces().keySet().stream()
                .anyMatch(t -> "PyObject-cleanup".equals(t.getName()) && t.isAlive());
    }
}

