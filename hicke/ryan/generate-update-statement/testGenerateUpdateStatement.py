import unittest
from generateUpdateStatement import generateUpdateStatement


class TestGenerateUpdateStatement(unittest.TestCase):
    test_document = {
        '_id': 1,
        'name': "Johnny Content Creator",
        'posts': [
            {
                '_id': 2,
                'value': "one",
                "mentions": []
            },
            {
                '_id': 3,
                'value': "two",
                'mentions': [
                    {
                        '_id': 5,
                        'text': "apple",
                    },
                    {
                        '_id': 6,
                        'text': "orange",
                    }
                ]
            },
            {
                '_id': 4,
                'value': "three",
                'mentions': []
            }
        ]
    }

    def test_update_value_in_post(self):
        changes = {
            'posts': [{'_id': 2, 'value': "too"}]
        }
        expected = {
            '$update': {'posts.0.value': "too"}
        }
        output = generateUpdateStatement(self.test_document, changes)
        self.assertEqual(expected, output)

    def test_update_text_in_mention(self):
        changes = {'posts': [{'_id': 3, 'mentions': [{'_id': 5, 'text': "pear"}]}]}
        expected = {'$update': {'posts.1.mentions.0.text': "pear"}}
        output = generateUpdateStatement(self.test_document, changes)
        self.assertEqual(expected, output)

    def test_add_post(self):
        changes = {"posts": [{"value": "four"}]}
        expected = {"$add": {"posts": [{"value": "four"}]}}
        output = generateUpdateStatement(self.test_document, changes)
        self.assertEqual(expected, output)

    def test_add_mention_to_post(self):
        changes = {"posts": [{"_id": 3, "mentions": [{"_id": 5, "text": "pear"}]}]}
        expected = {"$update": {"posts.1.mentions.0.text": "pear"}}
        output = generateUpdateStatement(self.test_document, changes)
        self.assertEqual(expected, output)

    def test_remove_post(self):
        changes = {"posts": [{"_id": 2, "_delete": True}]}
        expected = {"$remove": {"posts.0": True}}
        output = generateUpdateStatement(self.test_document, changes)
        self.assertEqual(expected, output)

    def test_remove_mention(self):
        changes = {"posts": [{"_id": 3, "mentions": [{"_id": 6, "_delete": True}]}]}
        expected = {"$remove": {"posts.1.mentions.1": True}}
        output = generateUpdateStatement(self.test_document, changes)
        self.assertEqual(expected, output)

    def update_add_and_remove(self):
        changes = {
            "posts": [
                {"_id": 2, "value": "too"},
                {"value": "four"},
                {"_id": 4, "_delete": True}
            ]
        }
        expected = {
            "$update": {"posts.0.value": "too"},
            "$add": {"posts": [{"value": "four"}]},
            "$remove": {"posts.2": True}
        }
        output = generateUpdateStatement(self.test_document, changes)
        self.assertEqual(expected, output)

    def test_multiple_update_statements(self):
        changes = {
            "posts": [
                {"_id": 2, "value": "too"},
                {"_id": 3, "mentions": [{"_id": 5, "text": "pear"}]},
                {"_id": 4, "value": "four"}
            ]
        }
        expected = {
            "$update": [
                {"posts.0.value": "too"},
                {"posts.1.mentions.0.text": "pear"},
                {"posts.2.value": "four"}
            ]
        }
        output = generateUpdateStatement(self.test_document, changes)
        self.assertEqual(expected, output)

    def test_multiple_add_statements(self):
        changes = {
            "posts": [
                {"value": "four"},
                {"_id": 3, "mentions": [{"text": "pear"}]},
                {"value": "five"},
                {"_id": 3, "mentions": [{"text": "fig"}]},
            ]
        }
        expected = {
            "$add": [
                {"posts": [{"value": "four"}, {"value": "five"}]},
                {"posts.1.mentions": [{'text': 'pear'}, {"text": "fig"}]}
            ]
        }
        output = generateUpdateStatement(self.test_document, changes)
        self.assertEqual(expected, output)

    def test_multiple_remove_statements(self):
        changes = {
            "posts": [
                {"_id": 2, "_delete": True},
                {"_id": 4, "_delete": True},
                {"_id": 3, "mentions": [{"_id": 5, "_delete": True}, {"_id": 6, "_delete": True}]}
            ]
        }
        expected = {
            "$remove": [
                {"posts.0": True},
                {"posts.2": True},
                {"posts.1.mentions.0": True},
                {"posts.1.mentions.1": True}
            ]
        }
        output = generateUpdateStatement(self.test_document, changes)
        self.assertEqual(expected, output)


if __name__ == '__main__':
    unittest.main()
