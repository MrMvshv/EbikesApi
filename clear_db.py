import os
import django

# Set up Django settings (replace 'your_project' with your actual project name)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EBARestAPIServer.settings')
django.setup()

# Import your utility functions
from EBApi.db_utils import clear_riders, clear_orders, clear_all_tables, clear_messages, clear_users

# Optionally, you can interact with other models or add logging

def main():
    # Call the utility functions to clear the tables
    clear_users()   #clear users
    #clear_riders()  # Clears the Rider table
    #clear_orders()  # Clears the Order table
    #clear_messages()
    # Alternatively, call the function to clear all tables
    #clear_all_tables()

if __name__ == '__main__':
    main()
