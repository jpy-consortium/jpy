import unittest
import array

import jpyutil

jpyutil.init_jvm(jvm_maxmem='512M', jvm_classpath=['target/test-classes'])
import jpy


class TestTypeConversions(unittest.TestCase):
    """
    This test covers type conversion, including:

    - Automatic conversions of Python values to Java when calling Java methods from Python
    - jpy.cast() (See JPy_cast)
    - jpy.convert() (See JPy_convert_internal / JType_ConvertPythonToJavaObject)
    """

    def setUp(self):
        self.Fixture = jpy.get_type('org.jpy.fixtures.TypeConversionTestFixture')
        self.assertTrue('org.jpy.fixtures.TypeConversionTestFixture' in jpy.types)

    def test_ToObjectConversion(self):
        """
        Test automatic conversion of Python values to Java objects (when passing Python values as arguments to Java methods).
        """

        fixture = self.Fixture()
        self.assertEqual(fixture.stringifyObjectArg(12), 'Byte(12)')
        self.assertEqual(fixture.stringifyObjectArg(0.34), 'Double(0.34)')
        self.assertEqual(fixture.stringifyObjectArg('abc'), 'String(abc)')

        with self.assertRaises(ValueError) as e:
            fixture.stringifyObjectArg(1 + 2j)
        self.assertEqual(str(e.exception), 'cannot convert a Python \'complex\' to a Java \'java.lang.Object\'')

    def test_cast(self):
        """
        Test casts of Java objects using jpy.cast()
        """
        fixture = self.Fixture()

        # Create a test String:
        my_jstr = jpy.get_type('java.lang.String')('testStr')
        self.assertEqual(type(my_jstr).jclassname, 'java.lang.String')
        self.assertEqual(fixture.stringifyObjectArg(my_jstr), 'String(testStr)')

        # Cast to String (this should be a no-op)
        my_jcharseq1 = jpy.cast(my_jstr, 'java.lang.String')
        self.assertTrue(fixture.isSameObject(my_jstr, my_jcharseq1))  # Should be same Java object...
        # self.assertTrue(my_jcharseq1 is my_jstr)  # and the same Python object. (But currently a new one is returned.)
        self.assertEqual(type(my_jcharseq1).jclassname, 'java.lang.String')
        self.assertEqual(fixture.stringifyObjectArg(my_jcharseq1), 'String(testStr)')

        # Cast to CharSequence (using class name, not explicit jpy.get_type())
        my_jcharseq1 = jpy.cast(my_jstr, 'java.lang.CharSequence')
        self.assertTrue(fixture.isSameObject(my_jstr, my_jcharseq1))  # Should be same Java object...
        self.assertFalse(my_jcharseq1 is my_jstr)  # but a new Python object
        self.assertEqual(type(my_jcharseq1).jclassname, 'java.lang.CharSequence')
        self.assertEqual(fixture.stringifyObjectArg(my_jcharseq1), 'String(testStr)')

        # Cast to CharSequence (using explicit jpy.get_type()):
        my_jcharseq2 = jpy.cast(my_jstr, jpy.get_type('java.lang.CharSequence'))
        self.assertTrue(fixture.isSameObject(my_jstr, my_jcharseq2))  # Should be same Java object...
        self.assertFalse(my_jcharseq2 is my_jstr)  # but a new Python object
        self.assertEqual(type(my_jcharseq2).jclassname, 'java.lang.CharSequence')
        self.assertEqual(fixture.stringifyObjectArg(my_jcharseq2), 'String(testStr)')

    def test_convert_cast(self):
        """
        Test casts of Java objects using jpy.convert()
        """
        fixture = self.Fixture()

        # Create a test String:
        my_jstr = jpy.get_type('java.lang.String')('testStr')
        self.assertEqual(type(my_jstr).jclassname, 'java.lang.String')
        self.assertEqual(fixture.stringifyObjectArg(my_jstr), 'String(testStr)')

        # Cast to String (this should be a no-op)
        my_jcharseq1 = jpy.convert(my_jstr, 'java.lang.String')
        self.assertTrue(fixture.isSameObject(my_jstr, my_jcharseq1))  # Should be same Java object...
        # self.assertTrue(my_jcharseq1 is my_jstr)  # and the same Python object. (But currently a new one is returned.)
        self.assertEqual(type(my_jcharseq1).jclassname, 'java.lang.String')
        self.assertEqual(fixture.stringifyObjectArg(my_jcharseq1), 'String(testStr)')

        # Cast to CharSequence (using class name, not explicit jpy.get_type())
        my_jcharseq1 = jpy.convert(my_jstr, 'java.lang.CharSequence')
        self.assertTrue(fixture.isSameObject(my_jstr, my_jcharseq1))  # Should be same Java object...
        self.assertFalse(my_jcharseq1 is my_jstr)  # but a new Python object.
        self.assertEqual(type(my_jcharseq1).jclassname, 'java.lang.CharSequence')
        self.assertEqual(fixture.stringifyObjectArg(my_jcharseq1), 'String(testStr)')

        # Cast to CharSequence (using explicit jpy.get_type()):
        my_jcharseq2 = jpy.convert(my_jstr, jpy.get_type('java.lang.CharSequence'))
        self.assertTrue(fixture.isSameObject(my_jstr, my_jcharseq2))  # Should be same Java object...
        self.assertFalse(my_jcharseq2 is my_jstr)  # but a new Python object.
        self.assertEqual(type(my_jcharseq2).jclassname, 'java.lang.CharSequence')
        self.assertEqual(fixture.stringifyObjectArg(my_jcharseq2), 'String(testStr)')

    def test_convert_toBoxedPrimitive(self):
        fixture = self.Fixture()

        # Convert Python values to boxed types explicitly (using jpy.get_type() to retrieve the boxed type):
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(65, jpy.get_type('java.lang.Character'))),
                         'Character(A)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, jpy.get_type('java.lang.Byte'))), 'Byte(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, jpy.get_type('java.lang.Short'))), 'Short(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, jpy.get_type('java.lang.Integer'))), 'Integer(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, jpy.get_type('java.lang.Long'))), 'Long(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, jpy.get_type('java.lang.Float'))), 'Float(12.0)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, jpy.get_type('java.lang.Double'))), 'Double(12.0)')

        # Convert Python values to boxed types (using type name, not explicit jpy.get_type())
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(65, 'java.lang.Character')), 'Character(A)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, 'java.lang.Byte')), 'Byte(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, 'java.lang.Short')), 'Short(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, 'java.lang.Integer')), 'Integer(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, 'java.lang.Long')), 'Long(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, 'java.lang.Float')), 'Float(12.0)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, 'java.lang.Double')), 'Double(12.0)')

        # Convert Python values to boxed types (using primitive type names — but they still get boxed):
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(65, jpy.get_type('char'))), 'Character(A)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, jpy.get_type('byte'))), 'Byte(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, jpy.get_type('short'))), 'Short(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, jpy.get_type('int'))), 'Integer(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, jpy.get_type('long'))), 'Long(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, jpy.get_type('float'))), 'Float(12.0)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.convert(12, jpy.get_type('double'))), 'Double(12.0)')

    def test_convert_toPrimitiveArray(self):
        fixture = self.Fixture()

        # Convert Python values to arrays of primitive types

        target_type = type(jpy.array(jpy.get_type('char'), 0))
        jobj = jpy.convert([65, 66, 67], target_type)
        self.assertEqual(type(jobj), target_type)
        self.assertEqual(fixture.stringifyObjectArg(jobj), 'char[](A,B,C)')

        target_type = type(jpy.array(jpy.get_type('byte'), 0))
        jobj = jpy.convert([12, 13, 14], target_type)
        self.assertEqual(type(jobj), target_type)
        self.assertEqual(fixture.stringifyObjectArg(jobj), 'byte[](12,13,14)')

        target_type = type(jpy.array(jpy.get_type('short'), 0))
        jobj = jpy.convert([12, 13, 14], target_type)
        self.assertEqual(type(jobj), target_type)
        self.assertEqual(fixture.stringifyObjectArg(jobj), 'short[](12,13,14)')

        target_type = type(jpy.array(jpy.get_type('int'), 0))
        jobj = jpy.convert([12, 13, 14], target_type)
        self.assertEqual(type(jobj), target_type)
        self.assertEqual(fixture.stringifyObjectArg(jobj), 'int[](12,13,14)')

        target_type = type(jpy.array(jpy.get_type('long'), 0))
        jobj = jpy.convert([12, 13, 14], target_type)
        self.assertEqual(type(jobj), target_type)
        self.assertEqual(fixture.stringifyObjectArg(jobj), 'long[](12,13,14)')

        target_type = type(jpy.array(jpy.get_type('float'), 0))
        jobj = jpy.convert([12, 13, 14], target_type)
        self.assertEqual(type(jobj), target_type)
        self.assertEqual(fixture.stringifyObjectArg(jobj), 'float[](12.0,13.0,14.0)')

        target_type = type(jpy.array(jpy.get_type('double'), 0))
        jobj = jpy.convert([12, 13, 14], target_type)
        self.assertEqual(type(jobj), target_type)
        self.assertEqual(fixture.stringifyObjectArg(jobj), 'double[](12.0,13.0,14.0)')

    def test_convert_toBoxedPrimitiveArray(self):
        fixture = self.Fixture()

        # Convert Python values to arrays of boxed types

        target_type = type(jpy.array(jpy.get_type('java.lang.Character'), 0))
        jobj = jpy.convert([65, 66, 67], target_type)
        self.assertEqual(type(jobj), target_type)
        self.assertEqual(fixture.stringifyObjectArg(jobj), 'Character[](Character(A),Character(B),Character(C))')

        target_type = type(jpy.array(jpy.get_type('java.lang.Byte'), 0))
        jobj = jpy.convert([12, 13, 14], target_type)
        self.assertEqual(type(jobj), target_type)
        self.assertEqual(fixture.stringifyObjectArg(jobj), 'Byte[](Byte(12),Byte(13),Byte(14))')

        target_type = type(jpy.array(jpy.get_type('java.lang.Short'), 0))
        jobj = jpy.convert([12, 13, 14], target_type)
        self.assertEqual(type(jobj), target_type)
        self.assertEqual(fixture.stringifyObjectArg(jobj), 'Short[](Short(12),Short(13),Short(14))')

        target_type = type(jpy.array(jpy.get_type('java.lang.Integer'), 0))
        jobj = jpy.convert([12, 13, 14], target_type)
        self.assertEqual(type(jobj), target_type)
        self.assertEqual(fixture.stringifyObjectArg(jobj), 'Integer[](Integer(12),Integer(13),Integer(14))')

        target_type = type(jpy.array(jpy.get_type('java.lang.Long'), 0))
        jobj = jpy.convert([12, 13, 14], target_type)
        self.assertEqual(type(jobj), target_type)
        self.assertEqual(fixture.stringifyObjectArg(jobj), 'Long[](Long(12),Long(13),Long(14))')

        target_type = type(jpy.array(jpy.get_type('java.lang.Float'), 0))
        jobj = jpy.convert([12, 13, 14], target_type)
        self.assertEqual(type(jobj), target_type)
        self.assertEqual(fixture.stringifyObjectArg(jobj), 'Float[](Float(12.0),Float(13.0),Float(14.0))')

        target_type = type(jpy.array(jpy.get_type('java.lang.Double'), 0))
        jobj = jpy.convert([12, 13, 14], target_type)
        self.assertEqual(type(jobj), target_type)
        self.assertEqual(fixture.stringifyObjectArg(jobj), 'Double[](Double(12.0),Double(13.0),Double(14.0))')

    def test_convert_toJavaLangObject(self):
        """
        Test converting values to java.lang.Object (and letting the jpy module determine what Java type to convert
        them to).
        """
        java_lang_object_type = jpy.get_type('java.lang.Object')

        jobj = jpy.convert('A', java_lang_object_type)
        expected_type = jpy.get_type('java.lang.String')
        self.assertTrue(type(jobj).jclass.equals(java_lang_object_type.jclass), f'Type is {type(jobj)}')
        self.assertTrue(jobj.getClass().equals(expected_type.jclass), f'Type is {jobj.getClass()}')
        self.assertEqual(jpy.cast(jobj, expected_type).toString(), 'A')

        jobj = jpy.convert('ABCDE', java_lang_object_type)
        expected_type = jpy.get_type('java.lang.String')
        self.assertTrue(type(jobj).jclass.equals(java_lang_object_type.jclass), f'Type is {type(jobj)}')
        self.assertTrue(jobj.getClass().equals(expected_type.jclass), f'Type is {jobj.getClass()}')
        self.assertEqual(jpy.cast(jobj, expected_type).toString(), 'ABCDE')

        jobj = jpy.convert(True, java_lang_object_type)
        expected_type = jpy.get_type('java.lang.Boolean')
        self.assertTrue(type(jobj).jclass.equals(java_lang_object_type.jclass), f'Type is {type(jobj)}')
        self.assertTrue(jobj.getClass().equals(expected_type.jclass), f'Type is {jobj.getClass()}')
        self.assertEqual(jpy.cast(jobj, expected_type).booleanValue(), True)

        jobj = jpy.convert(False, java_lang_object_type)
        expected_type = jpy.get_type('java.lang.Boolean')
        self.assertTrue(type(jobj).jclass.equals(java_lang_object_type.jclass), f'Type is {type(jobj)}')
        self.assertTrue(jobj.getClass().equals(expected_type.jclass), f'Type is {jobj.getClass()}')
        self.assertEqual(jpy.cast(jobj, expected_type).booleanValue(), False)

        jobj = jpy.convert(12, java_lang_object_type)
        expected_type = jpy.get_type('java.lang.Byte')
        self.assertTrue(type(jobj).jclass.equals(java_lang_object_type.jclass), f'Type is {type(jobj)}')
        self.assertTrue(jobj.getClass().equals(expected_type.jclass), f'Type is {jobj.getClass()}')
        self.assertEqual(jpy.cast(jobj, expected_type).byteValue(), 12)

        jobj = jpy.convert(129, java_lang_object_type)
        expected_type = jpy.get_type('java.lang.Short')
        self.assertTrue(type(jobj).jclass.equals(java_lang_object_type.jclass), f'Type is {type(jobj)}')
        self.assertTrue(jobj.getClass().equals(expected_type.jclass), f'Type is {jobj.getClass()}')
        self.assertEqual(jpy.cast(jobj, expected_type).shortValue(), 129)

        jobj = jpy.convert(100_000, java_lang_object_type)
        expected_type = jpy.get_type('java.lang.Integer')
        self.assertTrue(type(jobj).jclass.equals(java_lang_object_type.jclass), f'Type is {type(jobj)}')
        self.assertTrue(jobj.getClass().equals(expected_type.jclass), f'Type is {jobj.getClass()}')
        self.assertEqual(jpy.cast(jobj, expected_type).intValue(), 100_000)

        jobj = jpy.convert(10_000_000_000, java_lang_object_type)
        expected_type = jpy.get_type('java.lang.Long')
        self.assertTrue(type(jobj).jclass.equals(java_lang_object_type.jclass), f'Type is {type(jobj)}')
        self.assertTrue(jobj.getClass().equals(expected_type.jclass), f'Type is {jobj.getClass()}')
        self.assertEqual(jpy.cast(jobj, expected_type).longValue(), 10_000_000_000)

        jobj = jpy.convert(123.45, java_lang_object_type)
        expected_type = jpy.get_type('java.lang.Double')  # TODO: these go to Double, not Float ?
        self.assertTrue(type(jobj).jclass.equals(java_lang_object_type.jclass), f'Type is {type(jobj)}')
        self.assertTrue(jobj.getClass().equals(expected_type.jclass), f'Type is {jobj.getClass()}')
        self.assertEqual(jpy.cast(jobj, expected_type).doubleValue(), 123.45)

        too_big_for_float = jpy.get_type('java.lang.Double').MAX_VALUE
        jobj = jpy.convert(too_big_for_float, java_lang_object_type)
        expected_type = jpy.get_type('java.lang.Double')
        self.assertTrue(type(jobj).jclass.equals(java_lang_object_type.jclass), f'Type is {type(jobj)}')
        self.assertTrue(jobj.getClass().equals(expected_type.jclass), f'Type is {jobj.getClass()}')
        self.assertEqual(jpy.cast(jobj, expected_type).doubleValue(), too_big_for_float)

    def test_convert_toString(self):
        jobj = jpy.convert('test string', jpy.get_type('java.lang.Object'))
        self.assertTrue(type(jobj).jclass.equals(jpy.get_type('java.lang.Object').jclass), f'Type is {type(jobj)}')
        self.assertTrue(jobj.getClass().equals(jpy.get_type('java.lang.String').jclass), f'Type is {jobj.getClass()}')
        self.assertEqual(jpy.cast(jobj, jpy.get_type('java.lang.String')).toString(), 'test string')

        # Invalid conversion:
        with self.assertRaises(ValueError) as e:
            jpy.convert(12, jpy.get_type('java.lang.String'))
        actual_message = str(e.exception)
        expected_message = "cannot convert a Python 'int' to a Java 'java.lang.String'"
        self.assertEqual(actual_message, expected_message)

    def test_ToPrimitiveArrayConversion(self):
        fixture = self.Fixture()

        # Python int array to Java int array
        a = array.array('i', [1, 2, 3])
        self.assertEqual(fixture.stringifyIntArrayArg(a), 'int[](1,2,3)')

        # integer list
        a = [4, 5, 6]
        self.assertEqual(fixture.stringifyIntArrayArg(a), 'int[](4,5,6)')

        # integer tuple
        a = (7, 8, 9)
        self.assertEqual(fixture.stringifyIntArrayArg(a), 'int[](7,8,9)')

        with self.assertRaises(RuntimeError) as e:
            fixture.stringifyIntArrayArg(1 + 2j)
        self.assertEqual(str(e.exception), 'no matching Java method overloads found')

    def test_ToObjectArrayConversion(self):
        fixture = self.Fixture()

        self.assertEqual(fixture.stringifyObjectArrayArg(('A', 12, 3.4)), 'Object[](String(A),Byte(12),Double(3.4))')
        self.assertEqual(fixture.stringifyObjectArrayArg(['A', 12, 3.4]), 'Object[](String(A),Byte(12),Double(3.4))')

        self.assertEqual(fixture.stringifyStringArrayArg(('A', 'B', 'C')), 'String[](String(A),String(B),String(C))')
        self.assertEqual(fixture.stringifyStringArrayArg(['A', 'B', 'C']), 'String[](String(A),String(B),String(C))')


if __name__ == '__main__':
    print('\nRunning ' + __file__)
    unittest.main()
