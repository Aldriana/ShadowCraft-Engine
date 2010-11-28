import unittest
from shadowcraft.core.exceptions import InvalidInputException

class TestInvalidInputException(unittest.TestCase):
    def test(self):
        try:
            raise InvalidInputException("test")
        except InvalidInputException as e:
            self.assertEqual(str(e), "test")
            self.assertEqual(e.error_msg, "test")
