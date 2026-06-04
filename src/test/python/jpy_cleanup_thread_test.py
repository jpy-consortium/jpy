"""
jpy_cleanup_thread_test.py
==========================
Stress tests for the PyObject cleanup daemon thread.

Background
----------
When a Java PyObject wrapper becomes unreachable, the cleanup daemon
(PyObject-cleanup) drains the ReferenceQueue and calls Py_DECREF on the
underlying Python objects in batches via PyLib.decRefs().

The daemon calls ``ReferenceQueue.remove(passive_sleep_millis)`` to block
until work arrives, waking up immediately when references are enqueued.

Test strategy
-------------
* **High-throughput path** (tests 03–06): flood the ReferenceQueue with
  FLOOD = 20 000 objects — far more than the batch buffer (default 4 096).
  The daemon loops continuously without sleeping, exercising sustained
  high-throughput draining.
* **Passive path** (test 07): release a small batch (SMALL = 100, well below
  the buffer) and assert that cleanup completes well within the 1 000 ms
  passive timeout, proving the daemon wakes on the event rather than waiting
  out the full timeout.
* **OOM-triggered GC** (test 08): release PyObjects without calling
  System.gc(), then trigger an OOM via ``jpy.array``.  The mandatory
  pre-OOM full GC enqueues the WeakRefs organically.  The cleanup thread
  must survive and drain correctly under OOM conditions.

All tests verify correctness (no leak, no double-free) and robustness under
sustained load.
"""

import threading
import time
import unittest

import jpyutil

jpyutil.init_jvm(
    jvm_maxmem='256M',
    jvm_classpath=['target/classes', 'target/test-classes'],
)
import jpy

# Cache Java types at import time — jpy.get_type() may fail after an OOM
# because the internal lookup itself requires heap allocation.
_System  = jpy.get_type('java.lang.System')
_Runtime = jpy.get_type('java.lang.Runtime')


# DEFAULT_BATCH_CLOSE_SIZE = 4096; flooding with FLOOD objects forces the
# daemon to make FLOOD/4096 consecutive passes without sleeping.
FLOOD   = 20_000
TIMEOUT = 10.0   # seconds: generous upper bound for daemon to drain FLOOD objects

# ── Destruction tracking ──────────────────────────────────────────────────────
# Counters must be safe to update from Trackable.__del__ on both GIL and
# free-threaded CPython.
#
# A "safe point" is a place where the interpreter may pause a thread to run
# bookkeeping — signals, scheduled callbacks, GC, and (on free-threaded
# builds) draining queued cross-thread Py_DECREFs. Threads reach safe points
# at the eval-breaker check on CALL/RETURN/JUMP_BACKWARD bytecodes and
# whenever a primitive blocks (a contended Python-level lock, a thread-state
# detach for a blocking call). Guarding an incrementing counter with a lock
# inside __del__ can therefore drain queued decrefs while the lock is being
# acquired, calling more __del__s recursively and causing RecursionError.
#
# We therefore need a counter that is atomic without taking any
# Python-level lock. list.append(None) / len() satisfies both:
#   * GIL Python — both are single C calls under the GIL → atomic.
#   * Free-threaded — list.append() uses the list's per-object critical
#     section, which is a safe point only on contention. The cleanup daemon
#     defers Py_DECREF back to the owning thread, so each counter has a
#     single writer and the critical section stays uncontested.
#
# When CPython gh-124366 lands a thread-safe atomic counter, this idiom can
# be replaced with that API.

_created   = []
_destroyed = []


class Trackable:
    """Python object that counts constructions and destructions thread-safely."""

    def __init__(self):
        _created.append(None)

    def __del__(self):
        _destroyed.append(None)


def _make_trackable():
    return Trackable()


def _reset():
    _created.clear()
    _destroyed.clear()


def _counts():
    return len(_created), len(_destroyed)


# ── Helpers ───────────────────────────────────────────────────────────────────

def gc_java(n=3):
    """Request Java GC to enqueue WeakReferences promptly.

    WeakReferences are enqueued by System.gc() alone — no finalizer involvement.
    System.runFinalization() is deprecated for removal since Java 18 (JEP 421)
    and is not needed here.  _System is cached at import time so this function
    is safe to call even after an OutOfMemoryError.
    """
    for _ in range(n):
        _System.gc()


def wait_until_cleaned(expected, timeout=TIMEOUT):
    """Poll until destroyed == expected or timeout expires."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        _, destroyed = _counts()
        if destroyed >= expected:
            return
        time.sleep(0.1)


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestCleanupThreadStress(unittest.TestCase):

    def setUp(self):
        _reset()
        self.Fixture = jpy.get_type('org.jpy.fixtures.CleanupThreadTestFixture')
        self.PyObjectClass = jpy.get_type('org.jpy.PyObject')
        self.fixture = self.Fixture()

    def _drain(self):
        # Release any objects still held by the fixture and drain the cleanup
        # queue before the next test resets the counters.  Without this,
        # objects from one test bleed into the next test's destroyed count.
        self.fixture.releaseAll()
        gc_java()
        created, _ = _counts()
        wait_until_cleaned(created)

    def test_01_daemon_thread_starts_and_is_alive(self):
        """Daemon thread must start after the first PyObject is created from JNI."""
        self.fixture.holdPyObjects(_make_trackable, 1)

        self.assertTrue(
            self.Fixture.isCleanupThreadAlive(),
            "PyObject-cleanup daemon thread is not alive after PyObject creation",
        )
        self._drain()

    def test_02_held_java_refs_prevent_python_deallocation(self):
        """While Java holds PyObject wrappers the Python objects must not be freed."""
        self.fixture.holdPyObjects(_make_trackable, FLOOD)

        created, destroyed = _counts()
        self.assertEqual(created, FLOOD)
        self.assertEqual(destroyed, 0,
                         f"{destroyed} objects freed while Java still held references")
        self._drain()

    def test_03_daemon_drains_single_large_flood(self):
        """Daemon must free all objects from a single large burst.

        FLOOD >> buffer size forces multiple consecutive passes without sleeping,
        exercising the high-throughput draining path.
        """
        self.fixture.holdPyObjects(_make_trackable, FLOOD)
        self.fixture.releaseAll()
        gc_java()

        wait_until_cleaned(FLOOD)

        created, destroyed = _counts()
        self.assertEqual(destroyed, FLOOD,
                         f"Single flood: expected {FLOOD} freed, got {destroyed} "
                         f"(leaked {FLOOD - destroyed})")

    def test_04_daemon_handles_repeated_sequential_floods(self):
        """No accumulation or leakage across multiple release cycles."""
        CYCLES = 5

        for cycle in range(1, CYCLES + 1):
            self.fixture.holdPyObjects(_make_trackable, FLOOD)
            self.fixture.releaseAll()
            gc_java()

            expected = FLOOD * cycle
            wait_until_cleaned(expected)

            _, destroyed = _counts()
            self.assertEqual(destroyed, expected,
                             f"Cycle {cycle}: expected {expected} freed, got {destroyed}")

    def test_05_daemon_keeps_up_under_concurrent_load(self):
        """Daemon drains correctly while Python releases new batches concurrently."""
        BURSTS  = 5
        errors  = []

        def release_loop():
            try:
                for _ in range(BURSTS):
                    self.fixture.holdPyObjects(_make_trackable, FLOOD)
                    self.fixture.releaseAll()
                    gc_java(n=1)
            except Exception as exc:
                errors.append(exc)

        t = threading.Thread(target=release_loop, daemon=True)
        t.start()
        t.join()

        self.assertEqual(errors, [], f"Exception in release loop: {errors}")

        total = FLOOD * BURSTS
        wait_until_cleaned(total, timeout=TIMEOUT * BURSTS)

        created, destroyed = _counts()
        self.assertEqual(created, total)
        self.assertEqual(destroyed, total,
                         f"Concurrent load: {created} created, {destroyed} freed")


    def test_06_explicit_cleanup_and_daemon_do_not_double_decrement(self):
        """PyObject.cleanup() racing with the daemon must not double-decrement.

        Thread-safety is guaranteed by ReferenceQueue's internal lock — each
        reference is dequeued exactly once regardless of how many callers race.
        """
        self.fixture.holdPyObjects(_make_trackable, FLOOD)
        self.fixture.releaseAll()
        gc_java()

        # Race: explicit cleanup() from Python thread while daemon also runs.
        for _ in range(20):
            self.PyObjectClass.cleanup()
            time.sleep(0.02)

        wait_until_cleaned(FLOOD)

        created, destroyed = _counts()
        self.assertEqual(created, FLOOD)
        self.assertEqual(destroyed, FLOOD,
                         f"Race: {created} created, {destroyed} freed "
                         f"(expected exactly {FLOOD})")


    def test_07_passive_path_wakes_up_promptly(self):
        """Small batch is cleaned up promptly via the blocking ReferenceQueue.remove() path.

        A batch of SMALL objects (well below the buffer size of 4096) is released
        and we assert that cleanup completes well within the default 1 000 ms
        passive timeout (``PROMPT_DEADLINE = 0.5 s``), proving the daemon woke
        up on the event rather than waiting out the full timeout.
        """
        SMALL          = 100    # << buffer size (4096)
        PROMPT_DEADLINE = 0.5   # seconds; comfortably below passive_sleep_millis (1 000 ms)

        self.fixture.holdPyObjects(_make_trackable, SMALL)
        created, destroyed = _counts()
        self.assertEqual(created, SMALL)
        self.assertEqual(destroyed, 0,
                         f"{destroyed} objects freed while Java still held references")

        self.fixture.releaseAll()
        gc_java()

        wait_until_cleaned(SMALL, timeout=PROMPT_DEADLINE)

        _, destroyed = _counts()
        self.assertEqual(
            destroyed, SMALL,
            f"Passive path: expected {SMALL} freed within {PROMPT_DEADLINE:.1f}s, "
            f"got {destroyed} — daemon may not have woken on ReferenceQueue.remove()",
        )

    def test_08_cleanup_survives_involuntary_gc_under_oom(self):
        """Cleanup thread must survive and drain correctly when GC is triggered by an OOM.

        The JVM runs a mandatory full GC before throwing OutOfMemoryError, which enqueues
        pending WeakReferences as a side effect. The cleanup daemon wakes up immediately
        via ReferenceQueue.remove() and calls PyLib.decRefs() while OOM conditions persist.

        A balloon of 50% of maxMemory is held so a second allocation of equal size cannot
        succeed even after the pre-OOM full GC, guaranteeing OOM. No gc_java() is called —
        cleanup must be driven by the OOM-triggered GC alone.

        Concurrent GC activity can enqueue WeakRefs before the OOM attempt, making it
        impossible to attribute cleanup to OOM. We retry up to MAX_ATTEMPTS times; if the
        precondition never holds the test is skipped.
        """
        MAX_ATTEMPTS = 3
        max_mem      = _Runtime.getRuntime().maxMemory()
        balloon_size = int(max_mem * 0.5)

        for attempt in range(1, MAX_ATTEMPTS + 1):
            _reset()
            self.fixture = self.Fixture()

            balloon = jpy.array('byte', balloon_size)  # noqa: F841 — holds Java ref

            self.fixture.holdPyObjects(_make_trackable, FLOOD)
            self.fixture.releaseAll()
            # no gc_java() — WeakRefs must be enqueued by the OOM GC only

            _, destroyed_before = _counts()
            if destroyed_before > 0:
                # Concurrent GC fired before the OOM attempt; retry.
                del balloon
                wait_until_cleaned(FLOOD)
                continue

            try:
                jpy.array('byte', balloon_size)
                self.fail("Expected OutOfMemoryError not raised — balloon may be too small")
            except MemoryError:
                pass

            wait_until_cleaned(FLOOD, timeout=TIMEOUT)

            _, destroyed = _counts()
            self.assertEqual(destroyed, FLOOD,
                             f"OOM-triggered GC: expected {FLOOD} freed, got {destroyed} "
                             f"— cleanup thread may have crashed under OOM conditions")
            return  # success

        self.skipTest(
            f"Concurrent GC fired early on all {MAX_ATTEMPTS} attempts "
            f"— cannot prove cleanup is attributable to OOM-triggered GC"
        )


if __name__ == '__main__':
    print('\nRunning ' + __file__)
    unittest.main()
