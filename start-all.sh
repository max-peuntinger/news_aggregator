#!/bin/bash

# Start Mosquitto
sudo /etc/init.d/mosquitto start

# Start MongoDB
sudo mongod --config /etc/mongod.conf &

# Start FastAPI
uvicorn app:app --reload &

# Start Publisher
python publisher.py &

# Start Subscriber
python subscriber.py &

# Start Svelte
cd svelte-app
npm run dev &
