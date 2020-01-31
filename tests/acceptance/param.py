class Param:
    p: int

    def __init__(self, p: str):
        self.p = p

    def __add__(self, other: "Param"):
        return self.p + other.p
