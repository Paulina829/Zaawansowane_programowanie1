import csv
import uuid
import time

TASK_FILE = "tasks.csv"

def add_task():
    task_id = str(uuid.uuid4())  
    task_description = input("Podaj opis zadania: ")  
    status = "pending"  

    with open(TASK_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([task_id, task_description, status])

    print(f"✅ Dodano zadanie: {task_description} (ID: {task_id})")

if __name__ == "__main__":
    while True:
        add_task()
        time.sleep(5)  
