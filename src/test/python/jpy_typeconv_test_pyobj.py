import unittest

import jpyutil

jpyutil.init_jvm(jvm_maxmem='512M', jvm_classpath=['target/classes'])
import jpy


class TestTypeConversionsPyObj(unittest.TestCase):
    """
    This test covers explicitly converting Python objects to Java PyObject instances. It is separate from
    jpy_typeconv_test.py because it requires a different classpath.
    """

    def test_convert_toPyObject(self):
        # Note that this test requires jvm_classpath=['target/classes'] (not jvm_classpath=['target/***test-***classes']

        print('Starting test_convert_toPyObject')
        PyObject_type = jpy.get_type('org.jpy.PyObject')
        print('test_convert_toPyObject: Got type for PyObject')

        print('test_convert_toPyObject: Testing value: \'A\'')
        print('test_convert_toPyObject: Doing first conversion')
        val = 'A'
        conv = jpy.convert(val, PyObject_type)
        print('test_convert_toPyObject: Getting first pointer')
        ptr = conv.getPointer()
        print('test_convert_toPyObject: Got first pointer')
        self.assertEqual(ptr, id(val))
        print('test_convert_toPyObject: Passed first assertion')

        print('test_convert_toPyObject: Testing value: string')
        val = 'ABCDE'
        self.assertEqual(jpy.convert(val, PyObject_type).getPointer(), id(val))

        print('test_convert_toPyObject: Testing value: True')
        val = True
        self.assertEqual(jpy.convert(val, PyObject_type).getPointer(), id(val))

        print('test_convert_toPyObject: Testing value: False')
        val = False
        self.assertEqual(jpy.convert(val, PyObject_type).getPointer(), id(val))

        print('test_convert_toPyObject: Testing value: 12')
        val = 12
        self.assertEqual(jpy.convert(val, PyObject_type).getPointer(), id(val))

        print('test_convert_toPyObject: Testing value: 12.2')
        val = 12.2
        self.assertEqual(jpy.convert(val, PyObject_type).getPointer(), id(val))

        print('test_convert_toPyObject: Testing value: [1, 2.0, "ABCDE"]')
        val = [1, 2.0, "ABCDE"]
        self.assertEqual(jpy.convert(val, PyObject_type).getPointer(), id(val))

        print('Finished test_convert_toPyObject')


if __name__ == '__main__':
    print('\nRunning ' + __file__)
    unittest.main()
