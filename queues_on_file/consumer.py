import csv
import time

TASK_FILE = "tasks.csv"

def read_tasks():
    """Odczytuje wszystkie zadania z pliku"""
    try:
        with open(TASK_FILE, mode="r") as file:
            reader = csv.reader(file)
            return [row for row in reader]
    except FileNotFoundError:
        return []

def write_tasks(tasks):
    """Nadpisuje plik nową listą zadań"""
    with open(TASK_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(tasks)

def process_task():
    tasks = read_tasks()
    for task in tasks:
        if task[2] == "pending":  
            print(f"⏳ Rozpoczynam zadanie: {task[1]} (ID: {task[0]})")
            task[2] = "in_progress"  
            write_tasks(tasks)

            time.sleep(30)  

            task[2] = "done"  
            write_tasks(tasks)
            print(f"✅ Zadanie zakończone: {task[1]} (ID: {task[0]})")
            break  

if __name__ == "__main__":
    while True:
        process_task()
        time.sleep(5)  
