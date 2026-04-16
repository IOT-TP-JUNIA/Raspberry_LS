import grovepi
import time
import json
import uuid
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
import math


sound_sensor = 0
light_sensor = 1
last_sound = 0
BROKER = "10.33.14.83"
PORT = 1883
topic = "device/LS"


def connect_to_broker(ip, port, mac):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"sensor-{mac}")
    try:
        client.connect(ip, port)
        print(f"Connecté au broker {ip}:{port}")
    except Exception as e:
        print(e)

    return client


def get_Value():
    light_intensity = []
    sound_level = []
    for i in range(5):
        light_intensity.append(grovepi.analogRead(light_sensor))
        sound_level.append(grovepi.analogRead(sound_sensor))
        time.sleep(1)

    avg_light_raw = sum(light_intensity) / len(light_intensity)
    avg_sound_raw = sum(sound_level) / len(sound_level)
    light = round(avg_light_raw * (1000 / 1023), 2)
    if avg_sound_raw > 0:
        sound = round(20 * math.log10(avg_sound_raw), 2)
    else:
        sound = 0
    return sound, light


def check_alert(sound, light):
    def put_parity(metric, parity):
        if parity == 0:
            metric = metric & ~1
        else:
            metric = metric | 1
        return metric

    checked_sound = (
        put_parity(int(round(sound)), 1)
        if sound >= 55
        else put_parity(int(round(sound)), 0)
    )
    checked_light = (
        put_parity(int(round(light)), 1)
        if light >= 700
        else put_parity(int(round(light)), 0)
    )

    return checked_sound, checked_light


def main():
    mac_int = uuid.getnode()
    mac_address = ":".join(
        ["{:02x}".format((mac_int >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]
    )
    print(f"Adresse MAC : {mac_address}")
    client = connect_to_broker(BROKER, PORT, mac_address)
    while True:
        try:
            sound_1, light_1 = get_Value()
            print(f"Last sound: {sound_1} \nLight level: {light_1}")
        except Exception as e:
            print(e)

        sound, light = check_alert(sound_1, light_1)
        payload_dict = {
            "MAC_ADDRESS": mac_address,
            "TIMESTAMP": datetime.now(timezone.utc).isoformat(),
            "METRICS": {"LIGHT": light, "SOUND": sound},
        }
        payload = json.dumps(payload_dict)
        client.publish(topic, payload)
        time.sleep(1)


main()
