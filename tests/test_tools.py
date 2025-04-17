import sys
import os

# Add the root directory of the project to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from server.main import run_kql_query

class TestMCPTools(unittest.TestCase):
    def test_run_kql_query(self):
        # Mock a valid query
        query = "StormEvents | count"
        database = "SampleDatabase"
        result = run_kql_query(query, database)
        self.assertIsInstance(result, list)

    def test_run_kql_query_error(self):
        # Mock an invalid query
        query = "INVALID QUERY"
        database = "SampleDatabase"
        result = run_kql_query(query, database)
        self.assertIn("error", result)

if __name__ == "__main__":
    unittest.main()