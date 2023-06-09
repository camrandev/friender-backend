#!/bin/bash

# Check if a command line argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: ./seed.sh <database_name>"
    exit 1
fi

# Store the database name
DATABASE_NAME=$1

# Ask for confirmation
read -p "Are you sure you want to drop the users table from the $DATABASE_NAME database? This cannot be undone. (y/n) " -n 1 -r
echo    # move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Connect to psql and run commands
    psql -d $DATABASE_NAME -c "DROP TABLE IF EXISTS users CASCADE;"

    # Run the seed.py script
    python3 seed.py
else
    echo "Operation cancelled."
fi