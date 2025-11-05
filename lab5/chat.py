import argparse
import sys
import time
import uuid
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
except Exception as e:
    print("paho-mqtt is not installed. Please run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

def make_client(client_id, userdata=None):
    try:
        client = mqtt.Client(client_id=client_id, userdata=userdata, protocol=mqtt.MQTTv311, callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
    except Exception:
        client = mqtt.Client(client_id=client_id, userdata=userdata, protocol=mqtt.MQTTv311)
    return client

def build_args(argv):
    p = argparse.ArgumentParser(description="SCD Lab 5 - MQTT chat client")
    p.add_argument("--broker", default="localhost", help="MQTT broker hostname or IP (default: localhost)")
    p.add_argument("--port", type=int, default=1883, help="MQTT broker port (default: 1883)")
    p.add_argument("--name", required=True, help="Your acronym/name to publish under (used as topic suffix)")
    p.add_argument("--topic-prefix", default="scd/chat", help="Topic prefix for chat (default: scd/chat)")
    p.add_argument("--qos", type=int, default=0, choices=[0, 1, 2], help="QoS level for publish/subscribe (default: 0)")
    p.add_argument("--keepalive", type=int, default=60, help="Keepalive seconds (default: 60)")
    p.add_argument("--debug", action="store_true", help="Enable verbose logging")
    return p.parse_args(argv)

def main(argv=None):
    args = build_args(argv or sys.argv[1:])
    client_id = f"scd-chat-{args.name}-{uuid.uuid4().hex[:8]}"
    topic_sub = f"{args.topic_prefix}/#"
    topic_pub = f"{args.topic_prefix}/{args.name}"

    state = {"connected": False, "qos": args.qos}
    client = make_client(client_id, userdata=state)

    if args.debug:
        client.enable_logger()

    def on_connect(client, userdata, flags, rc):
        userdata["connected"] = (rc == 0)
        if rc == 0:
            print(f"[OK] Connected to {args.broker}:{args.port} as {client_id}")
            client.subscribe(topic_sub, qos=args.qos)
            print(f"[OK] Subscribed to '{topic_sub}' (QoS={args.qos})")
            print("Type your message and press Enter. Use /exit to quit.\n")
        else:
            print(f"[ERR] Connection failed with result code {rc}", file=sys.stderr)

    def on_message(client, userdata, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload = msg.payload.decode(errors="replace")
        print(f"[{ts}] {msg.topic}: {payload}")

    def on_disconnect(client, userdata, rc):
        userdata["connected"] = False
        if rc != 0:
            print("[WARN] Unexpected disconnect. Reconnecting...")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    try:
        client.connect(args.broker, args.port, keepalive=args.keepalive)
    except Exception as e:
        print(f"[ERR] Could not connect to {args.broker}:{args.port} -> {e}", file=sys.stderr)
        return 2

    client.loop_start()
    try:
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line is None:
                time.sleep(0.05)
                continue
            line = line.strip()
            if not line:
                continue
            if line == "/exit":
                break
            info = client.publish(f"{topic_pub}", payload=line, qos=args.qos, retain=False)
            if info.rc != mqtt.MQTT_ERR_SUCCESS:
                print(f"[WARN] Publish failed: rc={info.rc}", file=sys.stderr)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()
        print("[OK] Disconnected. Bye!")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
