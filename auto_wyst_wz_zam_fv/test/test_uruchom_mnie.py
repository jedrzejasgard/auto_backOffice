import sys
import unittest
from assets.api_vendo.config import API_CONFIG

class MainTest(unittest.TestCase):

    def setUp(self):
        self.api_config = API_CONFIG


if __name__ == '__main__':
    unittest.main()
