import json
import random
import time
from datetime import datetime
from faker import Faker
from confluent_kafka import Producer

fake = Faker()

# Must be full connection string!
EVENT_HUB_CONNECTION_STRING = (
    "Endpoint=sb://mn-ecommerce-namespace.servicebus.windows.net/;"
    "SharedAccessKeyName=RootManageSharedAccessKey;"
    "SharedAccessKey=gv/dBOsIkgC54k+6Z+nKRFp/D6VwZOSHo+AEhID1xoo=;"
    "EntityPath=ecommerce-orders"
)

BOOTSTRAP_SERVERS = "mn-ecommerce-namespace.servicebus.windows.net:9093"
EVENT_HUB_NAME = "ecommerce-orders"

producer = Producer({
    "bootstrap.servers": BOOTSTRAP_SERVERS,
    "security.protocol": "SASL_SSL",
    "sasl.mechanism": "PLAIN",
    "sasl.username": "$ConnectionString",
    "sasl.password": EVENT_HUB_CONNECTION_STRING
})

categories = ['Electronics', 'Books', 'Clothing', 'Home Decor', 'Toys']
locations = [
    {"city": "New York", "state": "NY", "lat": 40.7128, "lon": -74.0060},
    {"city": "Los Angeles", "state": "CA", "lat": 34.0522, "lon": -118.2437},
    {"city": "Chicago", "state": "IL", "lat": 41.8781, "lon": -87.6298},
    {"city": "Houston", "state": "TX", "lat": 29.7604, "lon": -95.3698},
    {"city": "Phoenix", "state": "AZ", "lat": 33.4484, "lon": -112.0740}
]

def generate_order():
    location = random.choice(locations)
    category = random.choice(categories)
    price = round(random.uniform(10, 2000), 2)
    quantity = random.randint(1, 5)

    return {
        "order_id": fake.uuid4(),
        "timestamp": datetime.utcnow().isoformat(),
        "customer_id": fake.uuid4(),
        "product_id": fake.uuid4(),
        "category": category,
        "price": price,
        "quantity": quantity,
        "total_amount": round(price * quantity, 2),
        "city": location["city"],
        "state": location["state"],
        "country": "USA",
        "latitude": location["lat"],
        "longitude": location["lon"],
        "delivery_status": random.choice(["Processing", "Shipped", "Delivered", "Cancelled"])
    }

def acked(err, msg):
    if err:
        print("❌ Failed:", err)
    else:
        print(f"✔ Sent to {msg.topic()} partition {msg.partition()}")

if __name__ == "__main__":
    print("Streaming fake U.S. e-commerce orders to Azure Event Hub...")

    while True:
        event = generate_order()

        producer.produce(
            topic=EVENT_HUB_NAME,
            value=json.dumps(event).encode("utf-8"),
            callback=acked
        )

        producer.poll(0)
        print("Sent:", event)
        time.sleep(2)

        producer.flush()
