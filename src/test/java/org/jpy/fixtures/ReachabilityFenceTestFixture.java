package org.jpy.fixtures;

import org.jpy.PyObject;

import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Fixture for stress-testing the {@code Reference.reachabilityFence} guards
 * in {@link PyObject}.
 *
 * <p><b>Problem:</b> When a {@code PyObject} wrapper is used transiently — e.g.
 * the result of {@code getAttribute} is immediately dereferenced via
 * {@code callMethod}, {@code getIntValue}, etc. — JLS §12.6.1 permits the JIT
 * to treat the wrapper as reachability-dead once {@code getPointer()} has copied
 * the native pointer into a {@code long}.  At that point the GC may collect the
 * wrapper and the cleanup thread may {@code Py_DECREF} the underlying
 * {@code PyObject*} while JNI is still using it, causing a use-after-free crash.
 *
 * <p><b>Approach:</b> A background thread continuously allocates short-lived
 * objects to keep the young-generation GC busy.  Meanwhile, the main thread
 * repeatedly obtains a transient {@code PyObject} via {@code getAttribute} and
 * immediately invokes a JNI-backed method on it.  Without
 * {@code Reference.reachabilityFence} these patterns crash with SIGSEGV; with
 * the fence they must complete cleanly.
 */
public class ReachabilityFenceTestFixture {

    private static final AtomicBoolean running = new AtomicBoolean(false);
    private static Thread allocatorThread = null;

    /**
     * Starts a background thread that continuously allocates byte arrays to
     * drive young-generation GC, which is needed to trigger the race.
     */
    public static void startAllocator() {
        if (!running.compareAndSet(false, true)) {
            return;
        }
        allocatorThread = new Thread(() -> {
            Object[] sink = new Object[256];
            int i = 0;
            while (running.get()) {
                sink[i++ & 255] = new byte[64 * 1024]; // 64 KB each
            }
        }, "uaf-allocator");
        allocatorThread.setDaemon(true);
        allocatorThread.start();
    }

    /**
     * Stops the background allocator thread.
     */
    public static void stopAllocator() throws InterruptedException {
        running.set(false);
        if (allocatorThread != null) {
            allocatorThread.join(5_000);
            allocatorThread = null;
        }
    }

    /**
     * Stress getAttribute + callMethod on the transient bound method.
     */
    public static void stressCallTransient(PyObject callable, int iterations) {
        for (int i = 0; i < iterations; i++) {
            PyObject m = callable.getAttribute("__call__");
            m.callMethod("__call__");
        }
    }

    /**
     * Stress getAttribute + getIntValue on the transient result.
     * The object should have a "value" attribute that is an int.
     */
    public static void stressGetIntValue(PyObject obj, int iterations) {
        for (int i = 0; i < iterations; i++) {
            PyObject attr = obj.getAttribute("value");
            attr.getIntValue();
        }
    }

    /**
     * Stress getAttribute + getStringValue on the transient result.
     * The object should have a "name" attribute that is a string.
     */
    public static void stressGetStringValue(PyObject obj, int iterations) {
        for (int i = 0; i < iterations; i++) {
            PyObject attr = obj.getAttribute("name");
            attr.getStringValue();
        }
    }

    /**
     * Stress getAttribute + str() on the transient result.
     */
    public static void stressStr(PyObject obj, int iterations) {
        for (int i = 0; i < iterations; i++) {
            PyObject attr = obj.getAttribute("value");
            attr.str();
        }
    }

    /**
     * Stress getAttribute + repr() on the transient result.
     */
    public static void stressRepr(PyObject obj, int iterations) {
        for (int i = 0; i < iterations; i++) {
            PyObject attr = obj.getAttribute("value");
            attr.repr();
        }
    }

    /**
     * Stress getAttribute + hash() on the transient result.
     */
    public static void stressHash(PyObject obj, int iterations) {
        for (int i = 0; i < iterations; i++) {
            PyObject attr = obj.getAttribute("name");
            attr.hash();
        }
    }

    /**
     * Stress getAttribute + type-check methods (isInt, isCallable, etc.)
     * on transient results.  Each check uses a fresh getAttribute result so
     * the transient wrapper is the last use — making it eligible for
     * premature GC per JLS §12.6.1.
     */
    public static void stressTypeChecks(PyObject obj, int iterations) {
        for (int i = 0; i < iterations; i++) {
            obj.getAttribute("value").isInt();
            obj.getAttribute("value").isFloat();
            obj.getAttribute("value").isString();
            obj.getAttribute("value").isCallable();
            obj.getAttribute("value").isNone();
            obj.getAttribute("value").isList();
            obj.getAttribute("value").isDict();
        }
    }

    /**
     * Stress getAttribute + hasAttribute on the transient result.
     */
    public static void stressHasAttribute(PyObject obj, int iterations) {
        for (int i = 0; i < iterations; i++) {
            PyObject attr = obj.getAttribute("nested");
            attr.hasAttribute("value");
        }
    }

    /**
     * Stress call (function-style) on a transient callable.
     * The object should have a "compute" attribute that accepts one int argument.
     */
    public static void stressCall(PyObject obj, int iterations) {
        for (int i = 0; i < iterations; i++) {
            PyObject fn = obj.getAttribute("compute");
            fn.call("__call__", i);
        }
    }

    /**
     * Stress getAttribute + getObjectValue on the transient result.
     */
    public static void stressGetObjectValue(PyObject obj, int iterations) {
        for (int i = 0; i < iterations; i++) {
            PyObject attr = obj.getAttribute("value");
            attr.getObjectValue();
        }
    }

    /**
     * Stress createProxy + method call on a transient proxy.
     * The object should implement a "compute" method returning an int.
     */
    public static void stressProxy(PyObject obj, int iterations) {
        for (int i = 0; i < iterations; i++) {
            // Create a transient proxy and immediately invoke a method on it.
            // The proxy (and its PyProxyHandler holding pyObject) can become
            // reachability-dead after getPointer() in PyProxyHandler.invoke().
            Computable proxy = obj.createProxy(Computable.class);
            proxy.compute(i);
        }
    }

    /**
     * Stress asDict().containsKey() on a transient PyDictWrapper.
     * The object should be a Python dict.
     */
    public static void stressDictContainsKey(PyObject dict, int iterations) {
        for (int i = 0; i < iterations; i++) {
            dict.asDict().containsKey("key");
        }
    }

    /**
     * Stress asDict().keySet() on a transient PyDictWrapper.
     */
    public static void stressDictKeySet(PyObject dict, int iterations) {
        for (int i = 0; i < iterations; i++) {
            dict.asDict().keySet();
        }
    }

    /**
     * Stress asDict().copy() on a transient PyDictWrapper.
     */
    public static void stressDictCopy(PyObject dict, int iterations) {
        for (int i = 0; i < iterations; i++) {
            dict.asDict().copy().close();
        }
    }

    /**
     * Interface for proxy stress test.
     */
    public interface Computable {
        int compute(int x);
    }
}
