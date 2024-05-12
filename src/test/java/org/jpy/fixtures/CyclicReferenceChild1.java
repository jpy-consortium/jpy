//
// Copyright 2024 jpy-consortium
//

package org.jpy.fixtures;

import java.lang.reflect.Array;
import java.lang.reflect.Method;

/**
 * Used as a test class for the test cases in jpy_gettype_test.py
 *
 * @author Jianfeng Mao
 */
@SuppressWarnings("UnusedDeclaration")
public class CyclicReferenceChild1 extends CyclicReferenceParent {
    private int x;

    private CyclicReferenceChild1(int x) {
        this.x = x;
    }

    public static CyclicReferenceChild1 of(int x) {
        return new CyclicReferenceChild1(x);
    }

    public int get_x() {
        return this.x;
    }
}
