import unittest

from scheme_on import SExp, Interpreter


class ReadTestCase(unittest.TestCase):
    def test_read_empty(self):
        self.assertEqual(SExp.read('()'), [])

    def test_read_int(self):
        self.assertEqual(SExp.read('1'), 1)

    def test_read_symbol(self):
        self.assertEqual(SExp.read('foo'), 'foo')

    def test_read_list(self):
        self.assertEqual(SExp.read('(1 2 3)'), [1,2,3])

    def test_read_nested(self):
        self.assertEqual(SExp.read('((1 2 3) (foo bar goo))'), [[1,2,3], ["foo","bar","goo"]])

    def test_read_error_unmatched(self):
        self.assertRaises(Exception, SExp.read, '(')
        self.assertRaises(Exception, SExp.read, ')')
        self.assertRaises(Exception, SExp.read, ') ((1 2 3) 4)')

class EvalInternalsTestCase(unittest.TestCase):
    def setUp(self):
        self.interpreter = Interpreter()

    def test_is_atom(self):
        self.assertTrue(self.interpreter.is_atom('a'))
        self.assertTrue(self.interpreter.is_atom(1))
        self.assertFalse(self.interpreter.is_atom([1,2,3]))
        self.assertFalse(self.interpreter.is_atom(["a", "b", "c"]))

    def test_expression_to_action(self):
        self.assertEqual(self.interpreter.expression_to_action(1).__func__, self.interpreter._const.__func__)
        self.assertEqual(self.interpreter.expression_to_action("cons"), self.interpreter._const)
        self.assertEqual(self.interpreter.expression_to_action("car"), self.interpreter._const)
        self.assertEqual(self.interpreter.expression_to_action("cdr"), self.interpreter._const)
        self.assertEqual(self.interpreter.expression_to_action("empty?"), self.interpreter._const)
        self.assertEqual(self.interpreter.expression_to_action("atom?"), self.interpreter._const)
        self.assertEqual(self.interpreter.expression_to_action("eq?"), self.interpreter._const)
        self.assertEqual(self.interpreter.expression_to_action("#t"), self.interpreter._const)
        self.assertEqual(self.interpreter.expression_to_action("#f"), self.interpreter._const)
        self.assertEqual(self.interpreter.expression_to_action("random_string"), self.interpreter._identifier)

class EvalTestCase(unittest.TestCase):
    def setUp(self):
        self.interpreter = Interpreter()

    def test_quote(self):
        self.assertEqual(self.interpreter.eval("(quote 1)"), 1)
        self.assertEqual(self.interpreter.eval("(quote abc)"), "abc")
        self.assertEqual(self.interpreter.eval("(quote ())"), [])
        self.assertEqual(self.interpreter.eval("(quote (1 2 3))"), [1, 2, 3])

    def test_cons(self):
        self.assertEqual(self.interpreter.eval("(cons 1 (quote ()))"), [1])
        self.assertEqual(self.interpreter.eval("(cons 1 (quote (2 3)))"), [1,2,3])

    def test_car(self):
        self.assertEqual(self.interpreter.eval("(car (quote (1 2 3)))"), 1)
        self.assertEqual(self.interpreter.eval("(car (quote (3)))"), 3)

    def test_cdr(self):
        self.assertEqual(self.interpreter.eval("(cdr (quote (1 2 3)))"), [2,3])
        self.assertEqual(self.interpreter.eval("(cdr (quote (3)))"), [])

    def test_add1(self):
        self.assertEqual(self.interpreter.eval("(add1 0)"), 1)
        self.assertEqual(self.interpreter.eval("(add1 10)"), 11)

    def test_sub1(self):
        self.assertEqual(self.interpreter.eval("(sub1 0)"), -1)
        self.assertEqual(self.interpreter.eval("(sub1 10)"), 9)

    def test_zero(self):
        self.assertTrue(self.interpreter.eval("(zero? 0)"))
        self.assertFalse(self.interpreter.eval("(zero? 1)"))
        self.assertFalse(self.interpreter.eval("(zero? -1)"))

    def test_number(self):
        self.assertTrue(self.interpreter.eval("(number? 0)"))
        self.assertTrue(self.interpreter.eval("(number? 1)"))
        self.assertTrue(self.interpreter.eval("(number? (quote 1))"))
        self.assertFalse(self.interpreter.eval("(number? (quote abc))"))
        self.assertFalse(self.interpreter.eval("(number? (quote (abc)))"))


    def test_atom(self):
        self.assertTrue(self.interpreter.eval("(atom? (quote a))"))
        self.assertTrue(self.interpreter.eval("(atom? 1)"))
        self.assertFalse(self.interpreter.eval("(atom? (quote ()))"))
        self.assertFalse(self.interpreter.eval("(atom? (quote (2 3)))"))

    def test_eq(self):
        self.assertTrue(self.interpreter.eval("(eq? 1 1)"))
        self.assertFalse(self.interpreter.eval("(eq? 1 2)"))
        self.assertFalse(self.interpreter.eval("(eq? 1 (quote a))"))
        self.assertFalse(self.interpreter.eval("(eq? 1 (quote (a b)))"))

        self.assertTrue(self.interpreter.eval("(eq? (quote a) (quote a))"))
        self.assertFalse(self.interpreter.eval("(eq? (quote a) (quote b))"))
        self.assertFalse(self.interpreter.eval("(eq? (quote a) (quote (b c)))"))

        self.assertTrue(self.interpreter.eval("(eq? (quote (a b c)) (quote (a b c)))"))
        self.assertFalse(self.interpreter.eval("(eq? (quote (a b c)) (quote (a b d)))"))






if __name__ == '__main__':
    unittest.main()


