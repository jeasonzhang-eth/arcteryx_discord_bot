import unittest
from tools.redis_handler import RedisHandler

class test_db(unittest.TestCase):
    def test_redis(self):
        rh = RedisHandler(host='localhost', port=16379, db=0, max_connections=5)
        rh.set('test', 'test')
        self.assertEqual(rh.get('test'), 'test')
        rh.delete('test')
        self.assertEqual(rh.get('test'), None)
