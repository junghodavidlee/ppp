#!/bin/bash
source venv/bin/activate
export PATH="/home/user/ppp/venv/bin:$PATH"
jupyter notebook main.ipynb --no-browser --port=8888
