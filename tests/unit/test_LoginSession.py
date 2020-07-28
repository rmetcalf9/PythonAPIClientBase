import TestHelperSuperClass
import unittest
import PythonAPIClientBase

@TestHelperSuperClass.wipd
class test_loginSession(unittest.TestCase):
  def test_init(self):
    session = PythonAPIClientBase.NullLoginSession()
