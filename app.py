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

    # for word in core_object.get("words").keys():
    #    if options not in core_object.get("tags"):
    #        continue
    #    value = int(core_object["words"][word]["failed_calls"]) / (int(core_object["words"][word]["failed_calls"]) + int(core_object["words"][word]["success_calls"]))\
    #            * 1 / (int(core_object["words"][word]["success_calls"] + 1))
    #    metrics[(word, core_object["words"][word]["translation"])] = value
    print(metrics)
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


@app.route('/update', methods=['POST'])
def feedback():
    update = request.get_json(force=True, silent=False, cache=True)
    print(update)
    with open("data.json", "r") as file:
        data = json.load(file)

    elements = 0
    for key in update.keys():
        all_words = update.get(key)
        for word in all_words.keys():
            result = all_words.get(word)

            if word not in data[key].keys():
                morph = pymorphy2.MorphAnalyzer()
                all_tags = ["NOUN", "LATN", "VERB", "plur", "sing", "ADJF", "ADJS"]
                to_add = []
                for el in all_tags:
                    if el in morph.parse(word)[0].tag:
                        to_add.append(el.lower())
                dict_to_add = {"date": time.time(), "success_calls": 0, "failed_calls": 1, "tags": to_add}
                data[key][word] = dict_to_add
                continue
            try:
                if int(result) == 1:
                    data[key][word]["success_calls"] = data.get(key).get(word).get("success_calls") + 1
                else:
                    data[key][word]["failed_calls"] = data.get(key).get(word).get("failed_calls") + 1
            except:
                elements += 1
                continue

    with open("data.json", "w") as file:
        file = json.dump(data, file)

    return "Success with {} failed".format(elements)



if __name__ == '__main__':
    app.run()
