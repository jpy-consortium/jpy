package org.jpy;

import java.lang.ref.PhantomReference;
import java.lang.ref.Reference;
import java.lang.ref.ReferenceQueue;
import java.lang.ref.WeakReference;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Tracks live {@link PyObject} instances via {@link WeakReference}s and drives
 * {@code Py_DECREF} on the underlying Python objects once the Java wrappers
 * become unreachable.
 *
 * <h3>Why not {@link java.lang.ref.Cleaner}?</h3>
 * {@code Cleaner} (Java 9+) is the modern replacement for {@link Object#finalize()}.
 * Internally it also uses a {@link PhantomReference} + {@link ReferenceQueue} daemon,
 * but it invokes each registered action individually.  jpy needs to batch multiple
 * {@code Py_DECREF} calls into a single JNI round-trip ({@link PyLib#decRefs}) for
 * performance — {@code Cleaner} offers no batching hook.  A hand-rolled
 * {@link ReferenceQueue} daemon with a fixed-size buffer gives us exactly that.
 *
 * <h3>Why {@link WeakReference} rather than {@link PhantomReference}?</h3>
 * See {@link #asRef} for the rationale.
 *
 * <p>Note: this setup could likely be better structured as a factory, but then the
 * existing JNI code would need to be aware of it.  Instead, new {@link PyObject}s
 * self-register on construction.
 */
class PyObjectReferences {
    private static final String WEAK = "weak";
    private static final String REF_TYPE = System.getProperty("PyObject.reference_type", WEAK);

    /**
     * At the end of the day, this is the most important number in determining the relative value
     * that is being placed in cleaning up vs performing more python work first. The larger this
     * number is, the more emphasis that is placed on cleaning up. The smaller this number is, the
     * more emphasis that is placed on other python work. It's possible that out of memory issues
     * occur if too small a number is provided here - thus the guidance is to err on the larger
     * side.
     */
    private static final int DEFAULT_BATCH_CLOSE_SIZE = Integer.parseInt(System.getProperty("PyObject.batch_close_size", "4096"));

    private static final long CLEANUP_THREAD_PASSIVE_SLEEP_MILLIS = Long.parseLong(System.getProperty("PyObject.passive_sleep_millis", "1000"));

    private final ReferenceQueue<PyObject> referenceQueue;
    private final Map<Reference<PyObject>, PyObjectState> references;
    private final int batchCloseSize;

    PyObjectReferences() {
        this(DEFAULT_BATCH_CLOSE_SIZE);
    }

    PyObjectReferences(int batchCloseSize) {
        if (batchCloseSize <= 0) {
            throw new IllegalArgumentException("batchCloseSize must be positive");
        }
        referenceQueue = new ReferenceQueue<>();
        references = new ConcurrentHashMap<>();
        this.batchCloseSize = batchCloseSize;
    }

    void register(PyObject pyObject) {
        if (references.put(asRef(pyObject), pyObject.getState()) != null) {
            throw new IllegalStateException("Existing reference overwritten - this should not happen.");
        }
    }

    private Reference<PyObject> asRef(PyObject pyObject) {
        // The implementation details regarding best-practices of phantom vs weak references
        // notifications is a bit murky to me. While the most technically correct replacement for
        // finalization logic is a phantom reference, does a weak reference serve a similar purpose
        // if we can guarantee the object won't ever be re-animated after being marked as weak? If
        // so, does using weak references get us the notification a bit sooner? And - does using
        // weak references actually allow us to reclaim memory a bit faster, since phantom
        // references don't allow GC to actually proceed on the object until the phantom references
        // themselves are collected (see the phantom references javadoc)?
        //
        // I *think* the answer to the above questions are "yes".
        //
        // As such, using a weak reference here, while a bit unsafer, is the more performant choice.
        // We must guarantee that no other users will keep weak references to PyObjects and
        // re-animate them.
        return WEAK.equals(REF_TYPE) ?
            new WeakReference<>(pyObject, referenceQueue) :
            new PhantomReference<>(pyObject, referenceQueue);
    }

    /**
     * Drains the reference queue and decrements the Python reference counts of all collected
     * {@link PyObject} instances in a single batch.
     *
     * <p>Safe to call concurrently with the cleanup daemon: {@link ReferenceQueue#poll()} is
     * internally synchronized so each enqueued reference is dequeued exactly once, and
     * {@link ConcurrentHashMap} ensures safe concurrent map access. Each caller uses its own
     * independently allocated buffer, so there is no shared mutable state between callers.
     */
    public int cleanup() {
        return drainAndDecRef(new long[batchCloseSize], 0);
    }

    /**
     * Drains the reference queue into {@code buffer} starting at {@code index}, then
     * decrements the Python reference counts of all collected pointers via
     * {@link PyLib#decRef}/{@link PyLib#decRefs}.
     */
    private int drainAndDecRef(final long[] buffer, int index) {
        while (index < buffer.length) {
            final Reference<? extends PyObject> ref = referenceQueue.poll();
            if (ref == null) {
                break;
            }
            index = appendIfNotClosed(buffer, index, ref);
        }
        if (index == 0) {
            return 0;
        }
        if (index == 1) {
            PyLib.decRef(buffer[0]);
            return 1;
        }
        PyLib.decRefs(buffer, index);
        return index;
    }

    private int appendIfNotClosed(long[] buffer, int index, Reference<? extends PyObject> reference) {
        reference.clear(); // helps GC proceed a bit faster for PhantomReference - guava Finalizer does this too

        final PyObjectState state = references.remove(reference);
        if (state == null) {
            throw new IllegalStateException("Reference from queue not in map - this should not happen.");
        }
        final long pointerForClosure = state.takePointer();
        if (pointerForClosure == 0) {
            // it's already been closed
            return index;
        }
        buffer[index] = pointerForClosure;
        return index + 1;
    }


    Thread createCleanupThread(String name) {
        return new Thread(this::cleanupThreadLogic, name);
    }

    private void cleanupThreadLogic() {
        // Buffer allocated once and owned exclusively by this thread for its lifetime.
        final long[] buffer = new long[batchCloseSize];
        try {
            while (!Thread.currentThread().isInterrupted()) {
                // Block until a reference is enqueued or the timeout expires.
                final Reference<? extends PyObject> first =
                        referenceQueue.remove(CLEANUP_THREAD_PASSIVE_SLEEP_MILLIS);
                if (first == null) {
                    continue;
                }
                drainAndDecRef(buffer, appendIfNotClosed(buffer, 0, first));
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        // Any RuntimeException escaping here propagates to the thread's
        // UncaughtExceptionHandler (stderr + thread death by default).
        // All plausible causes are non-recoverable:
        //   1. Python is in a non-recoverable state — no new PyObjects can be
        //      created so the ReferenceQueue will not grow further.
        //   2. An invalid pointer reached decRef/decRefs, indicating a double-dec
        //      or memory corruption; continuing would risk further corruption.
        //   3. A violated invariant inside PyObjectReferences itself (e.g.
        //      IllegalStateException from appendIfNotClosed) — internal state is
        //      inconsistent and cannot be trusted.
        // In all cases letting the thread die is the correct behaviour.
    }
}
