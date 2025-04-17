import unittest
from utils.kusto_client import execute_query

class TestKustoClient(unittest.TestCase):
    def test_execute_query_success(self):
        # Mock a successful query response
        query = "StormEvents | count"
        database = "SampleDatabase"
        result = execute_query(query, database)
        self.assertIsInstance(result, list)

    def test_execute_query_error(self):
        # Mock a query that causes an error
        query = "INVALID QUERY"
        database = "SampleDatabase"
        result = execute_query(query, database)
        self.assertIn("error", result)

if __name__ == "__main__":
    unittest.main()