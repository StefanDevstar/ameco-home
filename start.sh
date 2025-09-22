#!/bin/bash

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="Mac"
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    OS="Windows"
else
    echo "Unsupported OS"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Installing..."
    if [[ "$OS" == "Linux" ]]; then
        sudo apt-get update
        sudo apt-get install python3 -y
    elif [[ "$OS" == "Mac" ]]; then
        brew install python3
    elif [[ "$OS" == "Windows" ]]; then
        echo "Please install Python 3 manually."
        exit 1
    fi
fi

pip3 install -r requirements.txt
python3 gen_config.py
python3 app.py