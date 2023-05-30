import csv

def getWeightToKeyword(file_name:str):
    weight_to_keyword = {}
    with open(file_name, mode="r", encoding="utf-8") as rf:
        file_matrix = csv.reader(rf)
        for row in file_matrix:
            weight_to_keyword[row[0].replace(' ', '').replace('\t', '')] = int(row[1].replace(' ', '').replace('\t', ''))
    return weight_to_keyword