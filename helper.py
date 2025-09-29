from random import randint
import os
import csv

HARD_CSV_LIMIT = 20
LOBBY_FOLDER = "lobbies"

def derangement_shuffle(items):
    n = len(items)
    arr = list(items)
    for i in range(n-1):
        j = randint(i + 1, n-1)
        arr[i],arr[j] = arr[j],arr[i]
    if arr[-1] == items[-1]:
        arr[-1], arr[-2] = arr[-2], arr[-1]
    return arr

def read_from_csv(path) -> list:
    data = []
    try:
        with open(path, newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        pass

    return data

def rewrite_csv(path, data : list[list]):
    with open(path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)

def add_to_csv(path, data : list):
    with open(path, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(data)

def rows_in_csv(path):
    row_count = 0
    try:
        with open(path, newline="") as file:
            reader = csv.reader(file)
            row_count = sum(1 for _ in reader)
    except FileNotFoundError:
        pass
    return row_count

def lobby_file_path(code, folder=LOBBY_FOLDER):
    return os.path.join(folder, f"{code}.csv")

def lobby_exists(code):
    print(os.path.isfile(lobby_file_path(code)))
    return os.path.isfile(lobby_file_path(code))
