sudo /etc/init.d/mosquitto start
mosquitto_sub -t test/topic in one terminal
mosquitto_pub -t test/topic -m "Hello, World!" in other terminal: prints to first terminal
 