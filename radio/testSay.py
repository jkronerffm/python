import unittest
import say
from datetime import datetime

class TestSay(unittest.TestCase):
    def setUp(self):
        self._theTime = datetime(2024,2, 22, 14, 18)

    def tearDown(self):
        pass
    
    def test_get_time(self):
        actual = say.get_time(self._theTime, 'de', fuzzy=False, withDate=False)
        expected = "Es ist 14:18."
        self.assertEqual(expected, actual)

    def test_get_timeWithDate(self):
        actual = say.get_time(self._theTime, 'de', fuzzy=False, withDate=True)
        expected = "Es ist der 22.02.2024, 14:18."
        self.assertEqual(expected, actual)

    def test_get_timeWithLongDate(self):
        actual = say.get_time(self._theTime, 'de', fuzzy=False, withDate=True, longDate=True)
        expected = "Es ist Donnerstag der 22. Februar 2024, 14:18."
        self.assertEqual(expected, actual)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestSay('test_get_time'))
    suite.addTest(TestSay('test_get_timeWithDate'))
    suite.addTest(TestSay('test_get_timeWithLongDate'))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(suite())
    print(result)
