
class dataholder:
    def __init__(self,data):
        self.id = data["id"]
        self.lastUpdate = data["lastUpdate"]
        self.dbHash = data["dbHash"]
        self.sheetHash = data["streetHash"]