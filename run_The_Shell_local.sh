#!/bin/bash

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 could not be found. Please make sure Python3 is installed and try again."
    exit 1
fi

# Create a local Python virtual environment
echo "Creating a local Python virtual environment..."
python3 -m venv venv_TheShell

if [ "$?" -eq 1 ]; then
    echo "Failed to create a virtual environment. Make sure Python is installed correctly and that you have the necessary permissions."
    exit 1
else
    echo "Local virtual python environment created successfully."
fi

# Activate the virtual environment
source venv_TheShell/bin/activate

if [ "$?" -eq 1 ]; then
    echo "Failed to activate the virtual environment. Make sure the virtual environment was created successfully."
    exit 1
else
    echo "Virtual Python environment activated."
fi

# Install the required packages in the virtual environment
echo "Installing the required packages in the virtual environment..."
pip install -r requirements.txt

if [ "$?" -eq 1 ]; then
    exit 1
else
    echo -e "Finished installing the required packages.\n"
fi

# Get the pySIMsalabim and SIMsalabim
echo "Getting pySIMsalabim and SIMsalabim..."

python3 get_pySIMsalabim.py

# if results does not equal zero, exit
if [ "$?" -ne 0 ]; then
    echo "Failed to get pySIMsalabim"
    exit 1
fi

# pip install the requirements for pySIMsalabim
if [ -f "pySIMsalabim/requirements.txt" ]; then
    echo "Installing the required packages for pySIMsalabim..."
    pip install -r pySIMsalabim/requirements.txt
    if [ "$?" -ne 0 ]; then
        echo "Failed to install the required packages for pySIMsalabim"
        exit 1
    else
        echo
        echo "Finished installing the required packages for pySIMsalabim."
    fi
fi

echo # Add empty line for readability

python3 get_SIMsalabim.py

if [ "$?" -eq 0 ] || [ "$?" -eq 1 ]; then
    if [ "$?" -eq 0 ]; then
        echo -e "\nCompile SimSS and ZimT"
        fpc SIMsalabim/SimSS/simss
        fpc SIMsalabim/ZimT/zimt
        if [ "$?" -ne 0 ]; then
            exit 1
        else
            echo # Add empty line for readability
        fi 
    fi
    # Run a env shell and start streamlit app
    streamlit run SIMsalabim.py
else
    if [ "$?" -eq 2 ]; then
        echo "Script Failed"
    elif [ "$?" -eq 3 ]; then
        echo "Script terminated manually by user"
    else
        echo "Failed"
    fi
    sys.exit 1
fi
