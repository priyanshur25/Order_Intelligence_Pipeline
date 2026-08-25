import json
import os
from datetime import datetime
from src import config


class MockPubSubClient:
    """Fakes Pub/Sub by appending events to a local JSON-lines file."""

    def __init__(self, log_path="mock_pubsub_events.jsonl"):
        self.log_path = log_path

    def publish(self, topic, message: dict):
        event = {
            "topic": topic,
            "message": message,
            "published_at": datetime.utcnow().isoformat(),
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(event) + "\n")
        print(f"[MOCK] Published to '{topic}': {message}")

    def read_events(self):
        if not os.path.exists(self.log_path):
            return []
        with open(self.log_path) as f:
            return [json.loads(line) for line in f]


class RealPubSubClient:
    """Wraps the actual google-cloud-pubsub publisher."""

    def __init__(self, project_id):
        from google.cloud import pubsub_v1
        self.publisher = pubsub_v1.PublisherClient()
        self.project_id = project_id

    def _ensure_topic(self, topic):
        topic_path = self.publisher.topic_path(self.project_id, topic)
        try:
            self.publisher.get_topic(request={"topic": topic_path})
        except Exception:
            self.publisher.create_topic(request={"name": topic_path})
            print(f"[LIVE] Created topic {topic_path}")
        return topic_path

    def publish(self, topic, message: dict):
        topic_path = self._ensure_topic(topic)
        data = json.dumps(message).encode("utf-8")
        future = self.publisher.publish(topic_path, data)
        message_id = future.result()
        print(f"[LIVE] Published to '{topic}' (message_id={message_id}): {message}")


def get_pubsub_client():
    if config.IS_LIVE:
        return RealPubSubClient(config.GCP_PROJECT_ID)
    return MockPubSubClient()