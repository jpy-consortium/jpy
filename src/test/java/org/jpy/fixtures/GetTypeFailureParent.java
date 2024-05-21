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
public abstract class GetTypeFailureParent {
    static {
        toFail();
    }

    static void toFail() {
        throw new RuntimeException("Can't be loaded!");
    }
}
