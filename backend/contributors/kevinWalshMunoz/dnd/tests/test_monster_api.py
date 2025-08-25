# Basic test for the monster API
import unittest

class TestMonsterAPI(unittest.TestCase):
    """Test cases for Monster API"""
    
    def test_get_all_monsters(self):
        """Test retrieving all monsters"""
        from app.services.monster_service import get_all_monsters
        monsters = get_all_monsters()
        self.assertIsInstance(monsters, list)
        self.assertTrue(len(monsters) > 0)
        
    def test_get_monster_by_index(self):
        """Test retrieving a monster by index"""
        from app.services.monster_service import get_monster_by_index
        monster = get_monster_by_index('monster1')
        self.assertIsInstance(monster, dict)
        self.assertEqual(monster['name'], 'Goblin')
        
if __name__ == '__main__':
    unittest.main()
