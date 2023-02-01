# Import standard python modules
import time
import json
import paho.mqtt.client as mqtt
from Adafruit_IO import Client, Feed, RequestError


CONFIG_FILE_PATH = "config.json"

ADAFRUIT_IO_KEY = ""
ADAFRUIT_IO_USERNAME = ""

MQTT_HOST_NAME = ""
DEVICE_ID = ""
MQTT_PUBLISH_TOPIC = ""

ADAFRUIT_FEED_COOLING = ""
ADAFRUIT_FEED_FAN = ""
ADAFRUIT_FEED_SET_TEMPERATURE = ""


def read_config_file():
    try:
        f = open(CONFIG_FILE_PATH, "r")
        data = json.load(f)
        global ADAFRUIT_IO_KEY
        ADAFRUIT_IO_KEY = data["adafruit_io_key"]
        global ADAFRUIT_IO_USERNAME
        ADAFRUIT_IO_USERNAME = data["adafruit_io_username"]
        global MQTT_HOST_NAME
        MQTT_HOST_NAME = data["mqtt_host_name"]
        global DEVICE_ID
        DEVICE_ID = data["device_name"]
        global MQTT_PUBLISH_TOPIC
        MQTT_PUBLISH_TOPIC = f"{DEVICE_ID}/CMD"
    except Exception as e:
        print(f"Error reading config file{e}")


def adafruit_connection():
    try:
        # Create an instance of the REST client.
        aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
        return aio
    except Exception as e:
        print(f"Exception Connecting Adafruit-IO {e}")
        return None


def mqtt_connection():
    try:
        client = mqtt.Client()
        client.connect(host=MQTT_HOST_NAME)
        return client
    except Exception as e:
        print(f"Error connecting MQTT Client {e}")
        return None


def adafruit_feed_connection(aio):
    try:  # if we have a 'digital' feed
        global ADAFRUIT_FEED_COOLING
        ADAFRUIT_FEED_COOLING = aio.feeds('hvac-controller.cooling')
    except RequestError:  # create a digital feed
        feed = Feed(name="hvac-controller.cooling")
        ADAFRUIT_FEED_COOLING = aio.create_feed(feed)

    try:  # if we have a 'digital' feed
        global ADAFRUIT_FEED_FAN
        ADAFRUIT_FEED_FAN = aio.feeds('hvac-controller.fan')
    except RequestError:  # create a digital feed
        feed = Feed(name="hvac-controller.fan")
        ADAFRUIT_FEED_FAN = aio.create_feed(feed)

    try:  # if we have a 'digital' feed
        global ADAFRUIT_FEED_SET_TEMPERATURE
        ADAFRUIT_FEED_SET_TEMPERATURE = aio.feeds('hvac-controller.set-temperature')
    except RequestError:  # create a digital feed
        feed = Feed(name="hvac-controller.set-temperature")
        ADAFRUIT_FEED_SET_TEMPERATURE = aio.create_feed(feed)


def main():
    previous_cooling_data_value = ""
    previous_fan_data_value = ""
    previous_set_temperature_data_value = ""

    read_config_file()

    aio = adafruit_connection()
    while aio is None:
        print("Retrying connecting adafruit-io in 30 sec")
        time.sleep(30)
        aio = adafruit_connection()

    client = mqtt_connection()
    while client is None:
        print("Retrying connecting mqtt client in 30 sec")
        time.sleep(30)
        client = mqtt_connection()

    adafruit_feed_connection(aio)
    while True:
        command = ""
        seq = 0
        json_data = {"Command": command, "Seq": seq}

        try:
            cooling_data = aio.receive(ADAFRUIT_FEED_COOLING.key)
            cooling_data_value = int(cooling_data.value)
            if cooling_data_value != previous_cooling_data_value:
                if int(cooling_data.value) == 1:
                    command = "enable-cooling"
                    seq = 4001
                    json_data["Command"] = command
                    json_data["Seq"] = seq
                    json_load = json.dumps(json_data, indent=4)
                    print('Cooling <- Enable')
                    print(json_load)
                    print(type(json_load))
                    print(MQTT_PUBLISH_TOPIC, "\n")
                    out = client.publish(MQTT_PUBLISH_TOPIC, json_load)
                    if out.is_published():
                        print("Cooling Enable Success", "\n")
                elif int(cooling_data.value) == 0:
                    command = "enable-heating"
                    seq = 4002
                    json_data["Command"] = command
                    json_data["Seq"] = seq
                    json_load = json.dumps(json_data, indent=4)
                    print('Heating <- Enable')
                    print(json_load)
                    print(type(json_load), "\n")
                    out = client.publish(MQTT_PUBLISH_TOPIC, json_load)
                    if out.is_published():
                        print("Heating Enable Success", "\n")
                previous_cooling_data_value = int(cooling_data_value)
            else:
                print("cooling state not changed")
        except Exception as e:
            print(f"Error getting COOLING BUTTON data {e}")

        try:
            fan_data = aio.receive(ADAFRUIT_FEED_FAN.key)
            fan_data_value = fan_data.value
            if int(fan_data_value) != previous_fan_data_value:
                if int(fan_data.value) == 1:
                    print('Fan <- Enable')
                    command = "enable-fan"
                    seq = 4003
                    json_data["Command"] = command
                    json_data["Seq"] = seq
                    json_load = json.dumps(json_data, indent=4)
                    # aio.send_data(fan.key, "0")
                    print(json_load)
                    print(type(json_load), "\n")
                    out = client.publish(MQTT_PUBLISH_TOPIC, json_load)
                    if out.is_published():
                        print("Fan Enable Success", "\n")
                elif int(fan_data.value) == 0:
                    print('Fan <- Disable\n')
                previous_fan_data_value = int(fan_data_value)
            else:
                print("fan state not changed")
        except Exception as e:
            print(f"Error getting FAN BUTTON data {e}")

        try:
            set_temperature_data = aio.receive(ADAFRUIT_FEED_SET_TEMPERATURE.key)
            set_temperature_data_value = set_temperature_data.value
            if int(set_temperature_data_value) != previous_set_temperature_data_value:
                command = "set_temperature"
                seq = 4004
                json_data["Command"] = command
                json_data["Seq"] = seq
                json_data["Params"] = {"temperature": int(set_temperature_data.value)}
                json_load = json.dumps(json_data, indent=4)
                print(f"Set Temperature to {set_temperature_data.value}")
                print(json_load)
                print(type(json_load), "\n")
                out = client.publish(MQTT_PUBLISH_TOPIC, json_load)
                if out.is_published():
                    print("Set Temperature Success")
                previous_set_temperature_data_value = int(set_temperature_data_value)
            else:
                print("temperature does not changed", "\n")
        except Exception as e:
            print(f"Error getting SET TEMPERATURE SLIDER data {e}")

        time.sleep(10)


if __name__ == '__main__':
    main()
