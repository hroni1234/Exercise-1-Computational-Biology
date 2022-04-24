from Person import Person
from typing import List

class Cell:
    def __init__(self):
        self.persons: List[Person] = []

    def is_empty(self):
        return len(self.persons) == 0

    def clean_cell(self):
        self.persons = []

    def set_persons(self, person: Person):
        self.persons.append(person)

    def is_conflict(self):
        return len(self.persons) > 1

