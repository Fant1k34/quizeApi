import unittest
import json

from app import *

class TestStringMethods(unittest.TestCase):
    def test_feedback_structure_check(self):
        cases = []
        # Всё хорошо
        cases.append(({
              "1020304": {
                  "raticate": {
                      "translation": "крыса",
                      "result": 0
                  }
              }
          }, True))
        # Всё хорошо
        cases.append(({
              "1020304": {
                  "raticate": {
                      "translation": "крыса",
                      "result": 0
                  }
              },
            "1020305": {
                "rat": {
                    "translation": "мышь",
                    "result": 0
                }
            }
          }, True))
        # Плохо, так как два одинаковых айди пользователя
        cases.append(({
              "1020304": {
                  "raticate": {
                      "translation": "крыса",
                      "result": 0
                  }
              },
              "1020304": {
                  "raticate": {
                      "translation": "крыса",
                      "result": 0
                  },
                  "raticate": {
                      "translation": "не крыса",
                      "result": 0
                  }
              }
          }, False))
        # Плохо, так как совпадают названия слов
        cases.append((          {
              "1020304": {
                  "raticate": {
                      "translation": "крыса",
                      "result": 0
                  }
              },
              "1020305": {
                  "raticate": {
                      "translation": "крыса",
                      "result": 0
                  },
                  "raticate": {
                      "translation": "не крыса",
                      "result": 0
                  }
              }
          }, False))
        # Плохо, так как не корректен тип
        cases.append((          {
            "1020304": {
                "raticate": {
                  "translation": "крыса",
                  "result": 4
                }
            }
          }, False))
        cases.append((          {
            "1020304": {
                "raticate": {
                  "fffff": "",
                  "result": 0
                }
            }
          }, False))
        cases.append((          {
            "1020304": {
                "raticate": {
                  "translation": "",
                  "result": 0
                }
            }
          }, False))

        for pair in cases:
            json_test = json.dumps(pair[0])
            try:
                self.assertEqual(feedback_structure_check(pair[0]), pair[1])
            except:
                raise AssertionError("Test {} failed".format(pair))

    def test_get_all_tags_by_word(self):
        self.assertEqual(get_all_tags_by_word("milk", "молоко"), ['noun', 'sing', 'молочная продукция'])
        self.assertEqual(get_all_tags_by_word("cream", "сливки"), ['noun', 'sing', 'молочная продукция'])
        self.assertEqual(get_all_tags_by_word("###", "###"), [])
        self.assertEqual(get_all_tags_by_word("###", 5), [])
        self.assertEqual(get_all_tags_by_word(9, []), [])
        self.assertEqual(get_all_tags_by_word(9, ""), [])
        self.assertEqual(get_all_tags_by_word("no translation", ""), [])
        self.assertEqual(get_all_tags_by_word("", "без слов"), ['noun', 'plur'])
        self.assertEqual(get_all_tags_by_word("###", 'englush'), ['latn'])

    def test_get_best_word(self):
        self.assertEqual(get_best_word(None, "", ""), {})
        self.assertEqual(get_best_word("", None, ""), {})
        self.assertEqual(get_best_word("", "", None), {})
        self.assertEqual(get_best_word([], "", ""), {})
        self.assertEqual(get_best_word("", [], ""), {})
        self.assertEqual(get_best_word("", "", []), {})
        self.assertEqual(get_best_word({}, "", ""), {})
        self.assertEqual(get_best_word("", {}, ""), {})
        self.assertEqual(get_best_word("", "", {}), {})

if __name__ == '__main__':
    unittest.main()