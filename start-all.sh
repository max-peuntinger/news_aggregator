#!/bin/bash

# Define the ports you want to free up
ports=(8000 8080) # Add the ports used by your services

# Kill any processes using those ports
for port in "${ports[@]}"; do
  pid=$(lsof -t -i:$port)
  if [ -n "$pid" ]; then
    echo "Killing process on port $port (PID: $pid)"
    kill -9 $pid
  fi
done


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
