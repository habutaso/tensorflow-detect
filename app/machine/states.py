from enum import Enum


class States(Enum):
    initial = "Initial"
    search = "Search"
    tracking = "Tracking"
    shooting = "Shooting"
    quit = "Quit"

    @classmethod
    @property
    def states_list(cls):
        return [state for state in cls]


if __name__ == "__main__":
    print(States.states_list)
