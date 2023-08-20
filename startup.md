sudo /etc/init.d/mosquitto start
mosquitto_sub -t test/topic in one terminal
mosquitto_pub -t test/topic -m "Hello, World!" in other terminal: prints to first terminal
 
start mongodb
sudo mongod --config /etc/mongod.conf

start fastapi: $uvicorn app:app --reload

start svelte: $cd svelte-app  $npm run dev
