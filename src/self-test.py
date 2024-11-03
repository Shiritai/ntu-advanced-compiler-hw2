from unittest import TextTestRunner, TestSuite, defaultTestLoader
from logger.test import LoggerTest
from instruction.test import InstTest

if __name__ == '__main__':
    cases = (LoggerTest, InstTest)
    suites = TestSuite(defaultTestLoader.loadTestsFromTestCase(t)
                       for t in cases)
    TextTestRunner().run(suites)
