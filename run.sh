#!/usr/bin/env bash

echo "Installing requirements..."
pip install -r requirements.txt

echo "Running the house-finder every ~5 minutes..."
while [ true ]
do
    python -u main.py
    sleep 300
done