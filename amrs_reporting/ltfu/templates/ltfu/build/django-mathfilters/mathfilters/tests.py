import unittest
from decimal import Decimal
from templatetags import mathfilters


class NumericConverterTest(unittest.TestCase):

    def test_string(self):
        self.assertEqual(13, mathfilters.valid_numeric('13'))
        self.assertEqual(-13, mathfilters.valid_numeric('-13'))
        self.assertEqual(13.3, mathfilters.valid_numeric('13.3'))
        self.assertEqual(-13.3, mathfilters.valid_numeric('-13.3'))

    def test_int(self):
        self.assertEqual(13, mathfilters.valid_numeric(13))
        self.assertEqual(-13, mathfilters.valid_numeric(-13))

    def test_float(self):
        self.assertEqual(13.3, mathfilters.valid_numeric(13.3))
        self.assertEqual(-13.3, mathfilters.valid_numeric(-13.3))

    def test_decimal(self):
        self.assertEqual(Decimal('2.3'), mathfilters.valid_numeric(Decimal('2.3')))
        self.assertEqual(Decimal('-2.3'), mathfilters.valid_numeric(Decimal('-2.3')))


class SubtractionTest(unittest.TestCase):

    def test_positive(self):
        self.assertEqual(3, mathfilters.sub('7', '4'))

    def test_negative_result(self):
        self.assertEqual(-20, mathfilters.sub('13', '33'))

    def test_negative_minuend(self):
        self.assertEqual(-42, mathfilters.sub('-23', '19'))

    def test_negative_subtrahend(self):
        self.assertEqual(6, mathfilters.sub('5', '-1'))

    def test_float(self):
        self.assertEqual(1.5, mathfilters.sub('-0.5', '-2'))

    def test_decimal_decimal(self):
        val1 = Decimal('9.9')
        val2 = Decimal('6.6')
        self.assertEqual(Decimal('3.3'), mathfilters.sub(val1, val2))

    def test_decimal_int(self):
        val1 = Decimal('9.999')
        val2 = 9
        self.assertEqual(Decimal('0.999'), mathfilters.sub(val1, val2))


class MultiplicationTest(unittest.TestCase):

    def test_positive(self):
        self.assertEqual(12, mathfilters.mul('3', '4'))

    def test_negative1(self):
        self.assertEqual(-10, mathfilters.mul('2', '-5'))

    def test_negative2(self):
        self.assertEqual(-10, mathfilters.mul('-2', '5'))

    def test_negative3(self):
        self.assertEqual(10, mathfilters.mul('-2', '-5'))

    def test_float(self):
        self.assertEqual(4.2, mathfilters.mul('2.1', '2'))

    def test_decimal_decimal(self):
        val1 = Decimal('3.3')
        val2 = Decimal('3')
        self.assertEqual(Decimal('9.9'), mathfilters.mul(val1, val2))

    def test_decimal_int(self):
        val1 = Decimal('3.3')
        val2 = 3
        self.assertEqual(Decimal('9.9'), mathfilters.mul(val1, val2))


class DivisionTest(unittest.TestCase):

    def test_positive(self):
        self.assertEqual(3, mathfilters.div('12', '4'))

    def test_negative1(self):
        self.assertEqual(-2, mathfilters.div('10', '-5'))

    def test_negative2(self):
        self.assertEqual(-2, mathfilters.div('-10', '5'))

    def test_negative3(self):
        self.assertEqual(2, mathfilters.div('-10', '-5'))

    def test_float1(self):
        self.assertEqual(8.5, mathfilters.div('27.2', '3.2'))

    def test_decimal_decimal(self):
        val1 = Decimal('9.9')
        val2 = Decimal('3.3')
        self.assertEqual(Decimal('3'), mathfilters.div(val1, val2))

    def test_decimal_decimal(self):
        val1 = Decimal('9.9')
        val2 = 3
        self.assertEqual(Decimal('3.3'), mathfilters.div(val1, val2))


class AbsoluteTest(unittest.TestCase):

    def test_positive(self):
        self.assertEqual(21, mathfilters.absolute('21'))

    def test_negative(self):
        self.assertEqual(21, mathfilters.absolute('-21'))

    def test_positive_float(self):
        self.assertEqual(2.3, mathfilters.absolute('2.3'))

    def test_negative_float(self):
        self.assertEqual(2.3, mathfilters.absolute('-2.3'))

    def test_positive_decimal(self):
        self.assertEqual(Decimal('9.99'), mathfilters.absolute(Decimal('9.99')))

    def test_negative_decimal(self):
        self.assertEqual(Decimal('9.99'), mathfilters.absolute(Decimal('-9.99')))


if __name__ == '__main__':
    unittest.main()
