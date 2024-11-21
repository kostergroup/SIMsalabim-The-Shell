#!/bin/bash
# CHeck for non-standard Python modules needed for the get_SIMsalabim.py script
python3 -c "import requests"

if [ "$?" -eq 1 ]; then
    pip install requests
fi

python3 -c "import packaging"

if [ "$?" -eq 1 ]; then
    pip install packaging
fi

python3 get_pySIMsalabim.py
python3 get_SIMsalabim.py

if [ "$?" -eq 0 ]; then
    echo -e "\nCompile SimSS and ZimT"
    fpc SIMsalabim/SimSS/simss
    fpc SIMsalabim/ZimT/zimt
fi

if [ "$?" -eq 0 ] || [ "$?" -eq 1 ]; then
    # Check whether pip/pipenv is installed
    if ! command pip -V >& /dev/null 
    then
        sudo apt-get install python3-pip
        pip3 install pipenv
    fi

    # Check if a Pipfile / pipenv already exists. If not, create a new one and install packages in requirements.txt
    FILE=Pipfile
    if ! test -f "$FILE"; then 
        pipenv install -r requirements.txt
    fi

    # Run a pip env shell and start streamlit app 
    pipenv run streamlit run SIMsalabim.py
elif [ "$?" -eq 2 ]; then
    echo "Script Failed"
elif [ "$?" -eq 3 ]; then
    echo "Script terminated manually"
else
     echo "Failed"
fi
