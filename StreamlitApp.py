import streamlit as st 
import threading 
from libraries.sessionController import sessionController 
import time 
 
controller = sessionController() 
 
# @st.cache_data
def fetch_table(selected_table):
    return controller.get_table_data(selected_table)
                
@st.cache_data
def update_row(selected_table, col_to_update, new_value, condition):                
    controller.update_row(selected_table, col_to_update, new_value, condition) 


def main(): 
    st.title("MySQL Table Viewer & CRUD Operations") 
     
    # Sidebar
    with st.sidebar:
        st.header("Table Management")
        
        # Add new table 
        if st.checkbox("Add a New Table"): 
            table_id = st.text_input("Enter table ID") 
            
            if st.button("Add Table"): 
                if table_id:
                    controller.add_table(table_id) 
                    st.success(f"Table '{table_id}' added successfully!")
                    st.experimental_rerun()  # Refresh the table list after adding 
            else: 
                st.warning("Please enter a table name.") 
        
        # Table selection
        tables = controller.get_table_names() 
        if tables:
            selected_table = st.selectbox("Select a Table", tables)
        else:
            # st.warning("No tables found in the database.")
            selected_table = None
     
    # Main content area
    if selected_table: 
        table_data = fetch_table(selected_table) 
        st.write(f"Displaying data from: {selected_table}") 
        st.dataframe(table_data) 
        
        # Add new row 
        if st.checkbox("Add a New Row"): 
            row_data = [] 
            print("new row")
            for col in table_data.columns: 
                row_data.append(st.text_input(f"Enter value for {col}", key=f"add_{col}")) 
            print("cols done")
            if st.button("Add Row"): 
                controller.add_row(selected_table, tuple(row_data)) 
                st.success("Row added successfully!") 
                st.experimental_rerun()  # Refresh the table 

        # Update existing row 
        if st.checkbox("Update a Row"): 
            col_to_update = st.selectbox("Select column to update", table_data.columns) 
            new_value = st.text_input(f"Enter new value for {col_to_update}") 
            condition = st.text_input("Enter condition (e.g., id=1)") 
            if st.button("Update Row"): 
                update_row(selected_table, col_to_update, new_value, condition) 
                st.success("Row updated successfully!") 
                st.experimental_rerun() 

        # Delete row 
        if st.checkbox("Delete a Row"): 
            condition = st.text_input("Enter condition for row to delete (e.g., id=1)") 
            if st.button("Delete Row"): 
                controller.delete_row(selected_table, condition) 
                st.success("Row deleted successfully!") 
                st.experimental_rerun() 

# def sync(): 
#     while True: 
#         try: 
#             controller.sync()     
#             time.sleep(30)
#         except KeyboardInterrupt: 
#             print("Synchronization stopped") 
#             break 
#         except Exception as e: 
#             print(f"An error occurred: {e}") 
#             time.sleep(60)  # Wait a bit before retrying 
 
if __name__ == '__main__': 
    # Create a thread for the sync function 
    # sync_thread = threading.Thread(target=sync, daemon=True) 
    # sync_thread.start()  # Start the background sync thread 
 
    main()  # Run the Streamlit app