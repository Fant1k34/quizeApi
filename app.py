from flask import Flask, request
import json
import time
import pymorphy2

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

def get_best_word(options, words, amount):
    metrics = {}
    for word in words.keys():
        if options not in words[word]["tags"]:
            continue
        value = int(words[word]["failed_calls"]) / (int(words[word]["failed_calls"]) + int(words[word]["success_calls"]))\
                * 1 / (int(words[word]["success_calls"] + 1))
        metrics[word] = value
    print(metrics)
    to_return = sorted(metrics.items(), key=lambda x: - x[1])[:min(amount, len(metrics))]
    return [cort[0] for cort in to_return]


@app.route('/getwords')
def get_current_words_by_code():
    code = request.args.get('code')
    option = request.args.get('option')
    amount = request.args.get('amount')
    # Код - 16 цифр. Первые 8 - id пользователя. Вторые 8 - режим.
    # Если  вектор id скалярно умножить на режим, а потом взять остаток от деления на 71
    # 0 - работа со словами/статистика
    # 1 - добавление слов
    # 2 - добавление слов и работа со словами/статистика

    # 1*2+2*9+0*2+5*5+5*2+0*0+2*3+5*2 % 71 = 0
    # 12055025 - id, 29252032 - код доступа на работу со словами/статистикой
    try:
        id = str(code[:8])
        private = str(code[8:])
        if sum([int(id[i]) * int(private[i]) for i in range(len(id))]) % 71 not in [0, 2]:
            return "Error. No roots"
    except:
        return "Error. No roots"

    with open("data.json", "r") as read_file:
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
