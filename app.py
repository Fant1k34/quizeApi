from flask import Flask, request
import json
import time
import pymorphy2
from ruwordnet import RuWordNet

app = Flask(__name__)


@app.route('/gettags')
def get_tags():
    id = request.args.get("id")
    all_tags = get_all_tags_by_name(id)
    if all_tags != None:
        return {"tags": list(all_tags)}
    else:
        return "Error. No such code"


def get_all_tags_by_name(id):
    try:
        with open("data1.json", "r") as read_file:
            data = json.load(read_file)
        return data.get(str(id)).get("tags").keys()
    except:
        return None



def get_best_word(options, core_object, amount):
    try:
        metrics = {}
        dict_to_return_words = {}
        options = options.lower()

        for tag in core_object.get("tags").keys():
            if tag != options:
                continue
            for word in core_object.get("tags").get(tag):
                core_object.get("words").get(word)
                value = int(core_object.get("words").get(word)["failed_calls"]) / (
                            int(core_object.get("words").get(word)["failed_calls"]) + int(
                        core_object.get("words").get(word)["success_calls"]) + 0.001) \
                        * 1 / (int(core_object.get("words").get(word)["success_calls"] + 1))
                metrics[(word, core_object["words"][word]["translation"])] = value
        to_return = sorted(metrics.items(), key=lambda x: - x[1])[:min(amount, len(metrics))]
        to_return = [cort[0] for cort in to_return]

        for el in to_return:
            dict_to_return_words[el[0]] = el[1]

        print(metrics)
        return {"words": dict_to_return_words}
    except:
        return {}

@app.route('/getwords')
def get_current_words_by_code():
    code = request.args.get('code')
    option = request.args.get('option')
    amount = request.args.get('amount')

    try:
        id = str(code)
    except:
        return "Error. No roots"

    with open("data1.json", "r") as read_file:
        data = json.load(read_file)
    try:
        words = get_best_word(option, data.get(id), int(amount))
        return str(words).replace("\'", "\"")
    except ValueError:
        return "Error. Incorrect value for amount"
    except TypeError:
        return "Error. Incorrect code value"
    except Exception:
        return "Error. This person doesn't exist"

def get_all_tags_by_word(word, translation):
    try:
        morph = pymorphy2.MorphAnalyzer()
        all_tags = ["NOUN", "LATN", "VERB", "plur", "sing", "ADJF", "ADJS"]
        to_add = []
        for el in all_tags:
            if el in morph.parse(translation)[0].tag:
                to_add.append(el.lower())
        wn = RuWordNet(filename_or_session='ruwordnet.db')
        number = 0
        for i, sense in enumerate(wn.get_senses(translation)):
            if i == number:
                to_add.append(sense.synset.hypernyms[i].title.lower())
    except:
        return []
    return to_add


def feedback_structure_check(json):
    # Должен быть словарь и длина не должна быть нулевой
    if type(json) != dict or len(json) == 0:
        return False

    # Все идентификаторы должны быть целыми числами
    for user in json.keys():
        try:
            int(user)
        except:
            return False

    # Все слова должны быть словами и не повторяться! А также пользователи не должны повторяться
    prev_user = set()
    for user in json.keys():
        prev_user_len = len(prev_user)
        prev_user.add(user)
        if prev_user_len == len(prev_user):
            return False

        users_data = json.get(user)
        word_set = set()
        for word in users_data.keys():
            if not word.isalpha():
                return False
            previous = len(word_set)
            word_set.add(word)
            if previous == len(word_set):
                return False

        # Все параметры слов должны быть только такими
        for word in users_data.keys():
            word_description = users_data.get(word)
            for description in word_description.keys():
                if description not in ["translation", "result"]:
                    return False

            for description in ["translation", "result"]:
                if description not in word_description.keys():
                    return False

            # Проверяем, что в translation находится перевод, а в result - 0 или 1
            if not users_data.get(word).get("translation").isalpha():
                return False
            print(users_data.get(word).get("result"))
            if type(users_data.get(word).get("result")) != int:
                return False
            try:
                if int(users_data.get(word).get("result")) not in [0, 1]:
                    return False
            except:
                return False

    return True



@app.route('/feedback', methods=['POST'])
def feedback():
    update = request.get_json(force=True, silent=False, cache=True)

    try:
        if not feedback_structure_check(dict(update)):
            return "Error with json format"
    except:
        return "Error with parsing json"

    with open("data1.json", "r") as file:
        data = json.load(file)

    elements = 0
    for user in update.keys():
        all_words = update.get(user)
        # Проверка, что такой пользователь есть в массиве
        if user not in data.keys():
            data[user] = {"words": {},
                          "tags": {}}
        # Добавляем слова/делаем фидбек
        for word in all_words.keys():
            result = update.get(user).get(word).get("result")
            if word not in data[user]["words"].keys(): # Если неизвестное слово - анализируем его
                tags_for_word = get_all_tags_by_word(word, update.get(user).get(word).get("translation"))
                dict_to_add = {"translation": update.get(user).get(word).get("translation"), "date": time.time(),
                               "success_calls": 0, "failed_calls": 1}
                data[user]["words"][word] = dict_to_add

                # Добавляем теги по словам
                for tag in tags_for_word:
                    if tag in data[user]["tags"]:
                        data[user]["tags"][tag].append(word)
                    else:
                        data[user]["tags"][tag] = []
                        data[user]["tags"][tag].append(word)
                continue
            try:
                if int(result) == 1:
                    data[user]["words"][word]["success_calls"] = \
                        data.get(user).get("words").get(word).get("success_calls") + 1
                else:
                    data[user]["words"][word]["failed_calls"] = \
                        data.get(user).get("words").get(word).get("failed_calls") + 1
            except:
                elements += 1
                continue

    with open("data1.json", "w") as file:
        file = json.dump(data, file)
    return "Success with {} failed".format(elements)

def returning_true():
    return True


if __name__ == '__main__':
    app.run()
