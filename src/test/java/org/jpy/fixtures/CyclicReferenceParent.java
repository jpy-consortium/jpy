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
public abstract class CyclicReferenceParent extends CyclicReferenceGrandParent {
    private int x;
    public int y = 10;

    public static CyclicReferenceChild1 of(int x) {
        return CyclicReferenceChild1.of(x);
    }

    public int parentMethod() {
        return 88;
    }

    public int get_x() {
        return this.x;
    }

}
