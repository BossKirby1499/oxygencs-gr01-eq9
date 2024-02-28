from signalrcore.hub_connection_builder import HubConnectionBuilder
import logging
import requests
import json
import time
import psycopg2


class App:
    def __init__(self):
        self._hub_connection = None
        self.TICKS = 10

        # To be configured by your team
        self.HOST = "http://159.203.50.162"  # Setup your host here
        self.TOKEN = "56ec01e496604e98ddef"  # Setup your token here
        self.T_MAX = 50  # Setup your max temperature here
        self.T_MIN = 20  # Setup your min temperature here
        self.DATABASE_URL = "Host=157.230.69.113;Database=db01eq9;Username=user01eq9;Password=1uv3yED3Us7E0flg"  # Setup your database here

    def __del__(self):
        if self._hub_connection != None:
            self._hub_connection.stop()

    def start(self):
        """Start Oxygen CS."""
        self.setup_sensor_hub()
        self._hub_connection.start()
        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setup_sensor_hub(self):
        """Configure hub connection and subscribe to sensor data events."""
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.HOST}/SensorHub?token={self.TOKEN}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )
        self._hub_connection.on("ReceiveSensorData", self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown closed: {data.error}")
        )

    def on_sensor_data_received(self, data):
        """Callback method to handle sensor data on reception."""
        try:
            print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
            timestamp = data[0]["date"]
            temperature = float(data[0]["data"])
            self.take_action(temperature,timestamp)
            self.save_event_to_database(timestamp, temperature)
        except Exception as err:
            print(err)

    def take_action(self, temperature, timestamp):
        """Take action to HVAC depending on current temperature."""
        if float(temperature) >= float(self.T_MAX):
            self.send_action_to_hvac("TurnOnAc")
            self.save_action_to_database(timestamp, "TurnOnAc")
        elif float(temperature) <= float(self.T_MIN):
            self.send_action_to_hvac("TurnOnHeater")
            self.save_action_to_database(timestamp, "TurnOnHeater")

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        r = requests.get(f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{self.TICKS}")
        details = json.loads(r.text)
        print(details, flush=True)

    def save_event_to_database(self, timestamp, temperature):
        """Save sensor data into the database."""
        try:
        # Parse the database URL
            db_params = self.DATABASE_URL.split(';')
            db_config = {param.split('=')[0]: param.split('=')[1] for param in db_params}

        # Connect to your database
            conn = psycopg2.connect(
                dbname=db_config['Database'],
                user=db_config['Username'],
                password=db_config['Password'],
                host=db_config['Host']
            )

            # Create a cursor object
            cur = conn.cursor()

            # SQL query to insert data
            insert_query = 'INSERT INTO sensor_data (timestamp, temperature) VALUES (%s, %s);'

            # Execute the query
            cur.execute(insert_query, (timestamp, temperature))

            # Commit the transaction
            conn.commit()

            # Close the cursor and connection
            cur.close()
            conn.close()

            print("Data saved successfully.")
            pass
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            pass
    def save_action_to_database(self, timestamp, action):
        """Save action data into the database."""
        try:
        # Parse the database URL
            db_params = self.DATABASE_URL.split(';')
            db_config = {param.split('=')[0]: param.split('=')[1] for param in db_params}

        # Connect to your database
            conn = psycopg2.connect(
                dbname=db_config['Database'],
                user=db_config['Username'],
                password=db_config['Password'],
                host=db_config['Host']
            )

            # Create a cursor object
            cur = conn.cursor()

            # SQL query to insert data
            insert_query = 'INSERT INTO action_data (timestamp, action) VALUES (%s, %s);'

            # Execute the query
            cur.execute(insert_query, (timestamp, action))

            # Commit the transaction
            conn.commit()

            # Close the cursor and connection
            cur.close()
            conn.close()

            print("Data saved successfully.")
            pass
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            pass

if __name__ == "__main__":
    app = App()
    app.start()
