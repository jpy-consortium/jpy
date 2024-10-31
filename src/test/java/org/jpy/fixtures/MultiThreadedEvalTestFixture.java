package org.jpy.fixtures;

import org.jpy.PyInputMode;
import org.jpy.PyLib;
import org.jpy.PyObject;

import java.util.List;

public class MultiThreadedEvalTestFixture {

    public static void expression(String expression, int numThreads) {
        execute(PyInputMode.EXPRESSION, expression, numThreads);
    }

    public static void script(String expression, int numThreads) {
        execute(PyInputMode.SCRIPT, expression, numThreads);
    }

    private static void execute(PyInputMode mode, String expression, int numThreads) {
        List<Thread> threads = new java.util.ArrayList<>();
        PyObject globals = PyLib.getCurrentGlobals();
        PyObject locals = PyLib.getCurrentLocals();
        for (int i = 0; i < numThreads; i++) {
            threads.add(new Thread(() -> {
                PyObject.executeCode(expression, mode, globals, locals);
            }));
        }
        for (Thread thread : threads) {
            thread.start();
        }
        for (Thread thread : threads) {
            try {
                thread.join();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

}
