import json

data_json = json.load(open("data2.json", "r"))

for i, breakpoint in enumerate(data_json):
    best_stocks = breakpoint["best_stocks"]
    worst_stocks = breakpoint["worst_stocks"]

    total = len(best_stocks) + len(worst_stocks)

    data_json[i]["weights"] = {}

    for ticker in best_stocks:
        data_json[i]["weights"][ticker] = -1 / total

    for ticker in worst_stocks:
        data_json[i]["weights"][ticker] = 1 / total


json.dump(data_json, open("data_modified.json", "w"), indent=4)
