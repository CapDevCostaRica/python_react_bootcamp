import os
import sys
import unittest
import json
from unittest.mock import patch, MagicMock

# Add project root and framework to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../framework')))

from app import create_app


class TestMonsterAPI(unittest.TestCase):
    def setUp(self):
        """Set up the test environment"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    @patch('app.controllers.monster_controller.get_all_monsters')
    @patch('app.controllers.monster_controller.fetch_monsters_from_api')
    @patch('app.controllers.monster_controller.bulk_insert_monsters')
    def test_list_monsters_with_existing_data(self, mock_bulk_insert, mock_fetch_api, mock_get_all):
        """Test the /list endpoint when monsters already exist in the database"""
        # Configure mock data
        mock_monsters_response = {
            'count': 2,
            'results': [
                {'index': 'aboleth', 'name': 'Aboleth'},
                {'index': 'acolyte', 'name': 'Acolyte'}
            ]
        }
        
        mock_get_all.return_value = mock_monsters_response
        
        # Send POST request
        response = self.client.post('/monsters/list', 
                                  json={"resource": "monsters"},
                                  content_type='application/json')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['count'], 2)
        self.assertEqual(len(data['results']), 2)
        
        # Verify that external API and bulk insert were not called
        mock_fetch_api.assert_not_called()
        mock_bulk_insert.assert_not_called()

    @patch('app.controllers.monster_controller.get_all_monsters')
    @patch('app.controllers.monster_controller.fetch_monsters_from_api')
    @patch('app.controllers.monster_controller.bulk_insert_monsters')
    def test_list_monsters_empty_database(self, mock_bulk_insert, mock_fetch_api, mock_get_all):
        """Test the /list endpoint when the database is empty"""
        # Configure mocks - empty database
        mock_get_all.return_value = {'count': 0, 'results': []}
        
        # Mock data de la API externa
        api_response = {
            'count': 3,
            'results': [
                {'index': 'aboleth', 'name': 'Aboleth'},
                {'index': 'acolyte', 'name': 'Acolyte'},
                {'index': 'adult-black-dragon', 'name': 'Adult Black Dragon'}
            ]
        }
        mock_fetch_api.return_value = api_response
        
        # Send POST request
        response = self.client.post('/monsters/list',
                                  json={"resource": "monsters"},
                                  content_type='application/json')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['count'], 3)
        self.assertEqual(len(data['results']), 3)
        
        # Verify that external API and bulk insert were called
        mock_fetch_api.assert_called_once()
        mock_bulk_insert.assert_called_once_with(api_response)

    def test_list_monsters_invalid_json(self):
        """Test the /list endpoint with invalid JSON"""
        response = self.client.post('/monsters/list',
                                  data='invalid json',
                                  content_type='application/json')
        
        # Should handle the error gracefully
        self.assertIn(response.status_code, [400, 500])

    @patch('app.controllers.monster_controller.get_monster_by_index')
    def test_get_monster_existing_in_database(self, mock_get_monster):
        """Test the /get endpoint when the monster already exists in the database"""
        # Configure mock data - monster exists
        mock_monster_data = {
            'index': 'bat',
            'name': 'Bat',
            'size': 'Tiny',
            'type': 'beast',
            'alignment': 'unaligned',
            'hit_points': 1,
            'armor_class': [{'type': 'natural', 'value': 12}]
        }
        mock_get_monster.return_value = mock_monster_data
        
        # Send POST request
        response = self.client.post('/monsters/get',
                                  json={"monster_index": "bat"},
                                  content_type='application/json')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['index'], 'bat')
        self.assertEqual(data['name'], 'Bat')
        
        # Verify that get_monster_by_index was called
        mock_get_monster.assert_called_once_with('bat')

    @patch('app.controllers.monster_controller.get_monster_by_index')
    @patch('app.controllers.monster_controller.fetch_monster_details_from_api')
    @patch('app.controllers.monster_controller.insert_monster_details')
    def test_get_monster_not_in_database(self, mock_insert, mock_fetch_api, mock_get_monster):
        """Test the /get endpoint when the monster does not exist in the database"""
        # Configure mocks - monster does not exist in DB
        mock_get_monster.return_value = None
        
        # Mock data from external API
        api_monster_data = {
            'index': 'dragon',
            'name': 'Dragon',
            'size': 'Huge',
            'type': 'dragon',
            'alignment': 'chaotic evil',
            'hit_points': 200,
            'armor_class': [{'type': 'natural', 'value': 18}]
        }
        mock_fetch_api.return_value = api_monster_data
        
        # Send POST request
        response = self.client.post('/monsters/get',
                                  json={"monster_index": "dragon"},
                                  content_type='application/json')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['index'], 'dragon')
        self.assertEqual(data['name'], 'Dragon')
        
        # Verify that all necessary functions were called
        mock_get_monster.assert_called_once_with('dragon')
        mock_fetch_api.assert_called_once_with('dragon')
        mock_insert.assert_called_once()

    def test_get_monster_missing_monster_index(self):
        """Test the /get endpoint without monster_index"""
        response = self.client.post('/monsters/get',
                                  json={},
                                  content_type='application/json')
        
        # Should return validation error
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Validation error')
        self.assertIn('monster_index', data['details'])

    def test_get_monster_empty_monster_index(self):
        """Test the /get endpoint with empty monster_index"""
        response = self.client.post('/monsters/get',
                                  json={"monster_index": ""},
                                  content_type='application/json')
        
        # Should return validation error
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Validation error')

    def test_get_monster_invalid_monster_index_type(self):
        """Test the /get endpoint with incorrect monster_index type"""
        response = self.client.post('/monsters/get',
                                  json={"monster_index": 123},
                                  content_type='application/json')
        
        # Should return validation error
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Validation error')

    def test_get_monster_invalid_json(self):
        """Test the /get endpoint with invalid JSON"""
        response = self.client.post('/monsters/get',
                                  data='invalid json',
                                  content_type='application/json')
        
        # Should handle the error gracefully
        self.assertIn(response.status_code, [400, 500])


if __name__ == '__main__':
    unittest.main()
