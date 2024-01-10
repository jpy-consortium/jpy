package org.jpy;

import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TestRule;

/**
 * Wraps up {@link EmbeddableTest} with JUnit so {@link EmbeddableTest} doesn't have to have the
 * JUnit dependency.
 */
public class EmbeddableTestJunit {

    @Rule
    public TestRule testStatePrinter = new TestStatePrinter();

    @Test
    public void testStartingAndStoppingIfAvailable() {
        EmbeddableTest.testStartingAndStoppingIfAvailable();
    }

    @Test
    public void testPassStatement() {
        EmbeddableTest.testPassStatement();
    }

    @Test
    public void testPrintStatement() {
        EmbeddableTest.testPrintStatement();
    }

    @Test
    public void testIncrementByOne() {
        EmbeddableTest.testIncrementByOne();
    }
}
