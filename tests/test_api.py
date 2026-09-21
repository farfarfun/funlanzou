import unittest

from funlanzou.api.models import FileList
from funlanzou.api.parser import parse_file_name, parse_file_size, parse_sign


class ParserTests(unittest.TestCase):
    def test_parse_file_metadata(self):
        html = "<title>demo.txt - 蓝奏云</title> 大小 12 K<"
        self.assertEqual(parse_file_name(html), "demo.txt")
        self.assertEqual(parse_file_size(html), "12 K")

    def test_parse_sign_does_not_log_secret(self):
        self.assertEqual(parse_sign("'sign':'secret-sign-value-1234567890',"), "secret-sign-value-1234567890")


class FileListTests(unittest.TestCase):
    def test_find_and_remove_by_id(self):
        item = type("Item", (), {"name": "demo", "id": 1})()
        items = FileList()
        items.append(item)
        self.assertIs(items.find_by_name("demo"), item)
        self.assertIs(items.pop_by_id(1), item)
        self.assertEqual(len(items), 0)


if __name__ == "__main__":
    unittest.main()
