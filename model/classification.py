from dataclasses import dataclass

@dataclass
class Classification:
    GeneID: str
    Localization: str
    Essential: str


    def __str__(self):
        return f"{self.GeneID} | Loc.: {self.Localization}"

    def __hash__(self):
        return hash(self.GeneID)
