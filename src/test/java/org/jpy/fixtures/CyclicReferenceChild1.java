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

    public CyclicReferenceChild2[] getChild2s() {
        CyclicReferenceChild2[] child2s = new CyclicReferenceChild2[2];
        child2s[0] = new CyclicReferenceChild2();
        child2s[1] = new CyclicReferenceChild2();
        return child2s;
    }
}
