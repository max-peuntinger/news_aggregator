from bson.objectid import ObjectId
from bson.json_util import dumps
import html
import feedparser
import paho.mqtt.client as mqtt
from pymongo import MongoClient
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

QOS_LEVEL = 1

client = MongoClient('localhost', 27017)
db = client['news_aggregator']
articles_collection = db['articles']

# Callback when the MQTT client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")

def json_encoder(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

# Parse the RSS feed and publish each entry to the MQTT broker
def publish_rss_feed_to_mqtt():
    while True:
        for topic_key, (mqtt_topic, rss_url) in RSS_FEEDS.items():
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                title = html.unescape(entry.title)
                link = entry.link
                summary = html.unescape(entry.summary)

                # Check if the article with the same link already exists in the collection
                existing_article = articles_collection.find_one({"link": link})
                if existing_article:
                    print(f"Article with link {link} already exists. Skipping.")
                    continue

                message = {
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "topic": mqtt_topic,
                    "published_at": entry.published,
                }

                articles_collection.insert_one(message)

                message_json = dumps(message, default=json_encoder)

                client.publish(mqtt_topic, message_json, qos=QOS_LEVEL)
                print(f"Published to {mqtt_topic}: {title}")
                time.sleep(1)
        time.sleep(600) # delay of 10 minutes before looking for new feeds


client = mqtt.Client()
client.on_connect = on_connect

client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

client.loop_start()

publish_rss_feed_to_mqtt()
