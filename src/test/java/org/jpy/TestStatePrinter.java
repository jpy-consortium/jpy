package org.jpy;

import org.junit.rules.TestWatcher;
import org.junit.runner.Description;

import java.time.Instant;

public class TestStatePrinter extends TestWatcher {
    @Override
    protected void starting(Description desc) {
        System.out.println(Instant.now().toString() + " Starting test: " + desc.getClassName() + ": " + desc.getMethodName());
    }

    @Override
    protected void succeeded(Description desc) {
        System.out.println(Instant.now().toString() + " Passed test: " + desc.getClassName() + ": " + desc.getMethodName());
    }

    @Override
    protected void failed(Throwable e, Description desc) {
        System.err.println(Instant.now().toString() + " Failed test: " + desc.getClassName() + ": " + desc.getMethodName());
    }

    @Override
    protected void finished(Description desc) {
        // TODO: Seems like this makes the tests fail (w/ JVM crash) more reliably. need to figure out why.
        // (Without the GC, the tests usually fail but sometimes pass. With it, they always fail.)
        System.out.println(Instant.now().toString() + " Running GC after test: " + desc.getClassName() + ": " + desc.getMethodName());
        System.gc();
    }
}
