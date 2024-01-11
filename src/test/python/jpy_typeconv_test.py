import unittest
import array

import jpyutil


jpyutil.init_jvm(jvm_maxmem='512M', jvm_classpath=['target/test-classes'])
import jpy


class TestTypeConversions(unittest.TestCase):
    def setUp(self):
        self.Fixture = jpy.get_type('org.jpy.fixtures.TypeConversionTestFixture')
        self.assertTrue('org.jpy.fixtures.TypeConversionTestFixture' in jpy.types)


    def test_ToObjectConversion(self):
        fixture = self.Fixture()
        self.assertEqual(fixture.stringifyObjectArg(12), 'Byte(12)')
        self.assertEqual(fixture.stringifyObjectArg(0.34), 'Double(0.34)')
        self.assertEqual(fixture.stringifyObjectArg('abc'), 'String(abc)')

        with self.assertRaises(ValueError) as e:
            fixture.stringifyObjectArg(1 + 2j)
        self.assertEqual(str(e.exception), 'cannot convert a Python \'complex\' to a Java \'java.lang.Object\'')

    def test_noOpCast(self):
        fixture = self.Fixture()

        my_jstr = jpy.get_type('java.lang.String')('testStr')
        self.assertEqual(type(my_jstr).jclassname, 'java.lang.String')
        self.assertEqual(fixture.stringifyObjectArg(my_jstr), 'String(testStr)')

        my_jcharseq1 = jpy.cast(my_jstr, 'java.lang.CharSequence')
        self.assertEqual(type(my_jcharseq1).jclassname, 'java.lang.CharSequence')
        self.assertEqual(fixture.stringifyObjectArg(my_jcharseq1), 'String(testStr)')

        my_jcharseq2 = jpy.cast(my_jstr, jpy.get_type('java.lang.CharSequence'))
        self.assertEqual(type(my_jcharseq2).jclassname, 'java.lang.CharSequence')
        self.assertEqual(fixture.stringifyObjectArg(my_jcharseq2), 'String(testStr)')


    def test_ToObjectConversionTyped(self):
        fixture = self.Fixture()
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, jpy.get_type('java.lang.Byte'))), 'Byte(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, jpy.get_type('java.lang.Short'))), 'Short(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, jpy.get_type('java.lang.Integer'))), 'Integer(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, jpy.get_type('java.lang.Long'))), 'Long(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, jpy.get_type('java.lang.Float'))), 'Float(12.0)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, jpy.get_type('java.lang.Double'))), 'Double(12.0)')

        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, 'java.lang.Byte')), 'Byte(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, 'java.lang.Short')), 'Short(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, 'java.lang.Integer')), 'Integer(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, 'java.lang.Long')), 'Long(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, 'java.lang.Float')), 'Float(12.0)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, 'java.lang.Double')), 'Double(12.0)')

        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, jpy.get_type('byte'))), 'Byte(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, jpy.get_type('short'))), 'Short(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, jpy.get_type('int'))), 'Integer(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, jpy.get_type('long'))), 'Long(12)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, jpy.get_type('float'))), 'Float(12.0)')
        self.assertEqual(fixture.stringifyObjectArg(jpy.as_jobj(12, jpy.get_type('double'))), 'Double(12.0)')

        with self.assertRaises(ValueError) as e:
            jpy.as_jobj(12, jpy.get_type('java.lang.String'))
        actual_message = str(e.exception)
        expected_message = "cannot convert a Python 'int' to a Java 'java.lang.String'"
        self.assertEquals(actual_message, expected_message)

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
