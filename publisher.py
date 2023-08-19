import feedparser
import json
import paho.mqtt.client as mqtt
import time

# RSS Feeds Configuration
RSS_FEEDS = {
    "technology": ("news/technology", "https://www.technologyreview.com/feed/"),
    "golem": ("news/technology", "https://www.golem.de/rss.php?feed=RSS2.0"),
    "tagesschau_technology": ("news/technology", "https://www.tagesschau.de/xml/rss2"),
    "climate_change": ("news/climate_change", "https://www.umweltbundesamt.de/uba-info-presse/feed"),
    "eu_politics_euractiv": ("news/eu_politics", "https://www.euractiv.com/feed/"),
    "eu_politics_tagesschau": ("news/eu_politics", "https://www.tagesschau.de/xml/rss2"),
}

# MQTT Broker Configuration
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883

# Callback when the MQTT client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")

# Parse the RSS feed and publish each entry to the MQTT broker
def publish_rss_feed_to_mqtt():
    for topic_key, (mqtt_topic, rss_url) in RSS_FEEDS.items():
        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            summary = entry.summary

            message = {
                "title": title,
                "link": link,
                "summary": summary
            }

            message_json = json.dumps(message)

            client.publish(mqtt_topic, message_json)
            print(f"Published to {mqtt_topic}: {title}")
            time.sleep(1)


client = mqtt.Client()
client.on_connect = on_connect

client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

client.loop_start()

publish_rss_feed_to_mqtt()

client.loop_stop()
