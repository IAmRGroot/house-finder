#!/usr/bin/env bash

echo "Waiting for the VPN to be up..."
sleep 5

echo "Running the house-finder every minute..."
while [ true ]
do
    pip install -r requirements.txt && python -u main.py
    sleep 300
done