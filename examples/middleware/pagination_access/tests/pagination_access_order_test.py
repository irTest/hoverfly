''' Unit tests for file main.py

    Run tests using "nosetests --all-modules" under any folder under the middleware folder.
'''

import os
import sys
import unittest

from StringIO import StringIO

import pagination_access_order


class Test_PaginationMiddleware(unittest.TestCase):

    def setUp(self):
        self.originalOut = sys.stdout

    @staticmethod
    def _exampleStdIn(endpointPath, query):
        return '{"response":{"status":0,"body":"","headers":null},"request":{"path":"%s","method":"GET","destination":"readthedocs.org","query":"%s","body":"","remoteAddr":"127.0.0.1:43637","headers":{"Accept":["*/*"],"Accept-Encoding":["gzip, deflate"],"Connection":["keep-alive"],"User-Agent":["python-requests/2.8.1"]}},"id":""}' % (endpointPath, query)

    def _runMiddleware(self, endpointPath, query):

        sys.stdout = StringIO()

        pagination_access_order.main(stdin=StringIO(self._exampleStdIn(endpointPath, query)))

        sys.stdout.seek(0)
        results = sys.stdout.readlines()

        sys.stdout = self.originalOut

        return results

    def test_no_pagination(self):

        results = self._runMiddleware('/api/v1/project/', "?limit=50&amp;offset=0")

        self.assertTrue(True if results and 'No pagination.' in results[0] else False)

    def test_pagination_exists(self):

        results = self._runMiddleware('/api/v1/project/', "?page=2&amp;per_page=100")

        self.assertTrue(True if results and 'Pagination requested page 2.' in results[0] else False)

    def test_pagination_invalid_page_zero(self):

        # Reset the last pagination used.
        results = self._runMiddleware('/reset/', "?page=0&amp;per_page=100")

        self.assertTrue(True if results and 'Invalid page index.' in results[0] else False)

    def test_pagination_random_page(self):

        # Reset the last pagination used.
        self._runMiddleware('/reset/', "?page=1&amp;per_page=100")

        self._runMiddleware('/api/v1/project/', "?page=1&amp;per_page=100")
        results = self._runMiddleware('/api/v1/project/', "?page=3&amp;per_page=100")

        self.assertTrue(True if results and 'Accessed randomly.' in results[0] else False)

    def test_pagination_orderly_pages(self):

        # Reset the last pagination used.
        self._runMiddleware('/reset/', "?page=1&amp;per_page=100")

        self._runMiddleware('/api/v1/project/', "?page=1&amp;per_page=100")
        results = self._runMiddleware('/api/v1/project/', "?page=2&amp;per_page=100")

        self.assertTrue(True if results and 'Accessed orderly.' in results[0] else False)

    def test_pagination_page_not_already_accessed(self):

        # Reset the last pagination used.
        self._runMiddleware('/reset/', "?page=1&amp;per_page=100")

        self._runMiddleware('/api/v1/project/', "?page=1&amp;per_page=100")
        results = self._runMiddleware('/api/v1/project/', "?page=2&amp;per_page=100")

        self.assertTrue(True if results and 'Page not previously accessed.' in results[0] else False)

    def test_pagination_page_not_already_accessed(self):

        # Reset the last pagination used.
        self._runMiddleware('/reset/', "?page=1&amp;per_page=100")

        self._runMiddleware('/api/v1/project/', "?page=1&amp;per_page=100")
        results = self._runMiddleware('/api/v1/project/', "?page=1&amp;per_page=100")

        self.assertTrue(True if results and 'Page accessed.' in results[0] else False)

    def tearDown(self):
        # Even with errors in tests we reverse the replacements of stdout.
        sys.stdout = self.originalOut


if __name__ == '__main__':
    unittest.main()
