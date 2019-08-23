#!/bin/bash
test -d venv || for i in _; do 
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
done
source venv/bin/activate
python -m vaporwave $@
