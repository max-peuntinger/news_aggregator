import paho.mqtt.client as mqtt
import json

# MQTT Broker Configuration
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883

QOS_LEVEL = 1

# Predefined Topics
TOPICS = {
    "technology": "news/technology",
    "climate_change": "news/climate_change",
    "german_politics": "news/german_politics",
    "eu_politics": "news/eu_politics",
}

# Callback when the MQTT client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")

# Callback when a message is received from the broker
def on_message(client, userdata, msg):
    news_item = json.loads(msg.payload)

    # Preprocess the data
    title = news_item.get("title")
    summary = news_item.get("summary")
    url = news_item.get("url")
    timestamp = news_item.get("timestamp")

    # print(f"Title: {title}\nSummary: {summary}\nURL: {url}\nTimestamp: {timestamp}\n")

# Create an MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

# Topics User subscribes to
user_interests = ["technology", "climate_change"] # Example
for interest in user_interests:
    topic = TOPICS.get(interest)
    if topic:
        client.subscribe(topic, qos=QOS_LEVEL)
        # print(f"Subscribed to {topic}")

# Start the MQTT client loop
client.loop_forever()
