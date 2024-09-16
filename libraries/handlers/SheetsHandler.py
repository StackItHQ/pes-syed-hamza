

class SheetsHandler:
    def __init__(self):
        pass

    def get_sheet_hash():
        values = sheet.get_all_values()
        return hashlib.md5(str(values).encode()).hexdigest()