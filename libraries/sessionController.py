from libraries.handlers.FileHandler import FileHandler
from oauth2client.service_account import ServiceAccountCredentials
from libraries.handlers.MysqlHandler import MysqlHandler
# from handlers.SheetsHandler import SheetsHandler
import gspread
import hashlib
from datetime import datetime
import time 
class sessionController:
    def __init__(self,):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('secret.json', scope)
        self.client = gspread.authorize(creds)

        self.collection = {}
        self.sheets = {}
        self.sqlHandler = MysqlHandler()
        # self.sheetsHandler = SheetsHandler()
        self.fileHandler = FileHandler()
        self.fileHandler.load_sync_data(self.collection)
        self.loadSheets()
        # self.sync()
            
    def loadSheets(self):
        for ID in list(self.collection.keys()):
            if ID not in list(self.sheets.keys()):
                print("loading sheets")
                self.sheets[ID] = self.client.open_by_key(ID).sheet1

    def add_table(self,ID):
        sheet = self.sheets[ID]
        self.sync_sheet_to_db(ID,sheet)
        hash = self.sqlHandler.get_db_hash(ID,sheet)
        sheethash = self.get_sheet_hash(ID,sheet)
        self.fileHandler.append_data({"id":ID,"lastUpdate":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"dbHash":hash,"streetHash":sheethash})
        self.fileHandler.write_log(f"Table {ID} added Successfully")


    def sync(self):
        for ID in list(self.collection.keys()):
            sheet = self.client.open_by_key(ID).sheet1
            current_sheet_hash = self.get_sheet_hash(ID,sheet)
            current_db_hash = self.sqlHandler.get_db_hash(ID,sheet)
            if current_db_hash == "Created":
                continue
            if current_sheet_hash != self.collection[ID].sheetHash:
                print("Changes detected in Google Sheet")
                self.sync_sheet_to_db(ID,sheet)
                self.collection[ID].sheethash = current_sheet_hash
                self.collection[ID].dbHash = self.sqlHandler.get_db_hash(ID,sheet)  # Update db_hash after syncing
            elif current_db_hash != self.collection[ID].dbHash:
                print("Changes detected in Database")
                self.sync_db_to_sheet(ID,sheet)
                self.collection[ID].dbHash = current_db_hash
                self.collection[ID].sheethash = self.get_sheet_hash(ID,sheet) 

    def sync_db_to_sheet(self,ID,sheet): #fix
        sheet_data = self.sqlHandler.get_sheet(ID)
        sheet.clear()
        sheet.update('A1', sheet_data)
        self.fileHandler.write_log(f"ID {ID} synchronized to Google Sheet")


    def sync_sheet_to_db(self,ID,sheet):
        values = sheet.get_all_values()
        success = self.sqlHandler.SyncDataAndTable(ID,values,sheet)
        if(success):
            self.fileHandler.write_log(f"ID {ID} synchronized to Database")
        else:
            self.fileHandler.write_log(f"ID {ID} synchronization to Database failed")
        

    def create_table_from_sheet(self,ID):
        sheet = self.sheets[ID]
        success = self.sqlHandler.create_table_from_sheet(ID,sheet)
        self.fileHandler.write_log(f"Table '{ID}' created or updated based on Google Sheet structure.")

    def get_table_names(self):
        return list(self.collection.keys())
    
    def get_table_data(self,ID):
        sheet = self.sheets[ID]
        self.sync_sheet_to_db(ID,sheet)
        data = self.sqlHandler.get_table_data(ID)
        print("loaded")
        return data
    
    def add_row(self,ID,data):
        sheet = self.sheets[ID]
        self.collection[ID].lastUpdate =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sqlHandler.add_row(ID,data)
        self.fileHandler.write_log(f"Table '{ID}' updated Using UI.")
        self.sync_db_to_sheet(ID,sheet)

    def update_row(self,ID, col_to_update, new_value, condition):
        sheet = self.sheets[ID]
        self.collection[ID].lastUpdate =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sqlHandler.update_row(ID, col_to_update, new_value, condition)
        self.fileHandler.write_log(f"Table '{ID}' Columns: {col_to_update} updated Using UI.")
        self.sync_db_to_sheet(ID,sheet)
    
    def delete_row(self,ID, condition):
        sheet = self.sheets[ID]
        self.collection[ID].lastUpdate =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sqlHandler.delete_row(ID, condition)
        self.sync_db_to_sheet(ID,sheet)
        self.fileHandler.write_log(f"Table '{ID}' Condition: {condition} deletion Using UI.")

    def get_sheet_hash(self,ID,sheet = None):
        if(sheet is None):
            sheet = self.sheets[ID]
        values = sheet.get_all_values()
        return hashlib.md5(str(values).encode()).hexdigest()
        
