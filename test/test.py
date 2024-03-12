# pylint: disable=C0413
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '../src')
sys.path.append(src_dir)
# pylint: enable=C0413
from main import App
import json
import unittest
from unittest.mock import patch, MagicMock

class TestApp(unittest.TestCase):
    # Simule le véritable HubConnectionBuilder du paquet signalrcore
    @patch('main.HubConnectionBuilder')
    def test_setup_sensor_hub(self, mock_hub_builder):
        app = App()
        app.setup_sensor_hub()
        mock_hub_builder.assert_called()
    @patch('main.psycopg2.connect')
    def test_save_event_to_database(self, mock_connect):
        # Configuration de la connexion et du curseur simulés
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Supposons que DATABASE_URL est un attribut de la classe App
        instance = App()
        instance.DATABASE_URL = 'Database=db_name;Username=user;Password=pass;Host=localhost'
        # Appel de la méthode à tester
        instance.save_event_to_database('2023-01-01 12:00:00', 25.5)
        # Vérifie que psycopg2.connect a été appelé avec les bons paramètres extraits de DATABASE_URL
        mock_connect.assert_called_with(dbname='db_name', user='user', password='pass', host='localhost')
        # Vérifie que le curseur a exécuté la requête SQL correcte avec les paramètres attendus
        mock_cursor.execute.assert_called_with('INSERT INTO sensor_data (timestamp, temperature) VALUES (%s, %s);', ('2023-01-01 12:00:00', 25.5))
        # Vérifie que les méthodes commit et close de la connexion ont été appelées
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    @patch('main.App.save_event_to_database')
    @patch('main.App.take_action')
    def test_on_sensor_data_received(self, mock_take_action, mock_save_event_to_database):
        app = App()
        mock_data = [{"date": "2021-01-01 00:00:00", "data": "26"}]
        app.on_sensor_data_received(mock_data)

        mock_save_event_to_database.assert_called_once_with("2021-01-01 00:00:00", 26.0)
        mock_take_action.assert_called_once_with(26.0, "2021-01-01 00:00:00")

    @patch('requests.get')
    def test_send_action_to_hvac(self, mock_get):
        # Prépare une fausse réponse JSON sous forme de chaîne
        mock_response_json = json.dumps({"status": "success", "action": "TurnOnAc"})
        # Configure la fausse requête get pour retourner une réponse avec le texte JSON simulé
        mock_get.return_value.text = mock_response_json

        app = App()
        action = "TurnOnAc"
        app.send_action_to_hvac(action)

        mock_get.assert_called_once_with(f"{app.HOST}/api/hvac/{app.TOKEN}/{action}/{app.TICKS}")

if __name__ == '__main__':
    unittest.main()
