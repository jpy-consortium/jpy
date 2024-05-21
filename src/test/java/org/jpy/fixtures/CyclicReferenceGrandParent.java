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
public class CyclicReferenceGrandParent {
    private int x;
    public int z = 100;

    public CyclicReferenceGrandParent() {
    }

    public void refChild2(CyclicReferenceChild2 child2) {
    }

    public int grandParentMethod() {
        return 888;
    }

    public int get_x() {
        return this.x;
    }
}
