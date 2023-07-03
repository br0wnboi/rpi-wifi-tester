#!/bin/bash

# Check if running with sudo
if [ "$EUID" -ne 0 ]
  then echo "Please run this script with sudo."
  exit
fi

# Set the Flask app name
FLASK_APP="app.py"

# Run the Flask app on all interfaces
flask run --host=0.0.0.0
