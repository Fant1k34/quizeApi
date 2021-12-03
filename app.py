from flask import Flask, request
import json
import time
import pymorphy2

app = Flask(__name__)


def get_best_word(options, core_object, amount):
    metrics = {}
    dict_to_return_words = {}

    for tag in core_object.get("tags").keys():
        if tag != options:
            continue
        for word in core_object.get("tags").get(tag):
            core_object.get("words").get(word)
            value = int(core_object.get("words").get(word)["failed_calls"]) / (
                        int(core_object.get("words").get(word)["failed_calls"]) + int(
                    core_object.get("words").get(word)["success_calls"])) \
                    * 1 / (int(core_object.get("words").get(word)["success_calls"] + 1))
            metrics[(word, core_object["words"][word]["translation"])] = value
    to_return = sorted(metrics.items(), key=lambda x: - x[1])[:min(amount, len(metrics))]
    to_return = [cort[0] for cort in to_return]

    for el in to_return:
        dict_to_return_words[el[0]] = el[1]

    return {"words": dict_to_return_words}


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
        return str(words)
    except ValueError:
        return "Error. Incorrect value for amount"
    except TypeError:
        return "Error. Incorrect code value"
    except Exception:
        return "Error"

def get_all_tags_by_word(word, translation):
    morph = pymorphy2.MorphAnalyzer()
    all_tags = ["NOUN", "LATN", "VERB", "plur", "sing", "ADJF", "ADJS"]
    to_add = []
    for el in all_tags:
        if el in morph.parse(translation)[0].tag:
            to_add.append(el.lower())
    return to_add


@app.route('/update', methods=['POST'])
def feedback():
    update = request.get_json(force=True, silent=False, cache=True)
    with open("data1.json", "r") as file:
        data = json.load(file)

    elements = 0
    for user in update.keys():
        all_words = update.get(user)
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

if __name__ == '__main__':
    app.run()
