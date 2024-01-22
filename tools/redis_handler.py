import redis
from redis import ConnectionPool


def handle_redis_errors(func):
    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
            return result
        except redis.ConnectionError as e:
            print(f"Error connecting to Redis: {e}")
            return None
        except redis.RedisError as e:
            print(f"Redis operation error: {e}")
            return None
    return wrapper


class RedisHandler:
    _instance = None

    def __new__(cls, host='localhost', port=6379, db=0, max_connections=10):
        if not cls._instance:
            cls._instance = super(RedisHandler, cls).__new__(cls)
            # 创建 Redis 连接池
            cls._instance.connection_pool = ConnectionPool(
                host=host, port=port, db=db, max_connections=max_connections
            )
        return cls._instance

    def __init__(self, host='localhost', port=6379, db=0, max_connections=10):
        pass

    def _get_connection(self):
        return redis.Redis(connection_pool=self.connection_pool)

    @handle_redis_errors
    def set_string_value(self, key, value, expire_time=None):
        redis_conn = self._get_connection()
        if redis_conn:
            redis_conn.set(key, value)
            if expire_time:
                redis_conn.expire(key, expire_time)

    @handle_redis_errors
    def get_string_value(self, key):
        redis_conn = self._get_connection()
        if redis_conn:
            result = redis_conn.get(key)
            return result.decode('utf-8') if result else None

    @handle_redis_errors
    def delete_string_key(self, key):
        redis_conn = self._get_connection()
        if redis_conn:
            redis_conn.delete(key)

    @handle_redis_errors
    def set_hash_value(self, hash_name, field, value):
        redis_conn = self._get_connection()
        if redis_conn:
            redis_conn.hset(hash_name, field, value)

    @handle_redis_errors
    def get_hash_value(self, hash_name, field):
        redis_conn = self._get_connection()
        if redis_conn:
            result = redis_conn.hget(hash_name, field)
            return result.decode('utf-8') if result else None

    @handle_redis_errors
    def delete_hash_field(self, hash_name, field):
        redis_conn = self._get_connection()
        if redis_conn:
            redis_conn.hdel(hash_name, field)

    @handle_redis_errors
    def hgetall(self, hash_name):
        redis_conn = self._get_connection()
        if redis_conn:
            result = redis_conn.hgetall(hash_name)
            return result
            # return {k.decode('utf-8'): v.decode('utf-8') for k, v in result.items()} if result else None

    @handle_redis_errors
    def hmget(self, hash_name, fields):
        redis_conn = self._get_connection()
        if redis_conn:
            result = redis_conn.hmget(hash_name, fields)
            return [item.decode('utf-8') if item else None for item in result] if result else None

    @handle_redis_errors
    def hmset(self, hash_name, mapping):
        redis_conn = self._get_connection()
        if redis_conn:
            redis_conn.hmset(hash_name, mapping)

    @handle_redis_errors
    def push_to_list(self, list_name, value):
        redis_conn = self._get_connection()
        if redis_conn:
            redis_conn.lpush(list_name, value)

    @handle_redis_errors
    def pop_from_list(self, list_name):
        redis_conn = self._get_connection()
        if redis_conn:
            result = redis_conn.rpop(list_name)
            return result.decode('utf-8') if result else None

    @handle_redis_errors
    def add_to_set(self, set_name, value):
        redis_conn = self._get_connection()
        if redis_conn:
            redis_conn.sadd(set_name, value)

    @handle_redis_errors
    def remove_from_set(self, set_name, value):
        redis_conn = self._get_connection()
        if redis_conn:
            redis_conn.srem(set_name, value)

    @handle_redis_errors
    def add_to_sorted_set(self, zset_name, value, score):
        redis_conn = self._get_connection()
        if redis_conn:
            redis_conn.zadd(zset_name, {value: score})

    @handle_redis_errors
    def get_sorted_set_range(self, zset_name, start, end):
        redis_conn = self._get_connection()
        if redis_conn:
            result = redis_conn.zrange(zset_name, start, end)
            return [item.decode('utf-8') for item in result] if result else None

    @handle_redis_errors
    def remove_from_sorted_set(self, zset_name, value):
        redis_conn = self._get_connection()
        if redis_conn:
            redis_conn.zrem(zset_name, value)


# 示例使用
if __name__ == "__main__":
    # 创建 RedisHandler 实例
    redis_handler = RedisHandler(host='localhost', port=6379, db=0, max_connections=5)

    # 操作字符串
    redis_handler.set_string_value('string_key', 'string_value', expire_time=60)
    string_result = redis_handler.get_string_value('string_key')
    print(f"String value: {string_result}")

    # 删除字符串键值对
    redis_handler.delete_string_key('string_key')

    # 操作哈希
    redis_handler.set_hash_value('hash_name', 'field1', 'value1')
    hash_result = redis_handler.get_hash_value('hash_name', 'field1')
    print(f"Hash value: {hash_result}")

    # 删除哈希字段
    redis_handler.delete_hash_field('hash_name', 'field1')

    # 操作哈希 - 获取全部字段值
    hash_all_result = redis_handler.hgetall('hash_name')
    print(f"All Hash values: {hash_all_result}")

    # 操作哈希 - 批量获取字段值
    hash_multi_result = redis_handler.hmget('hash_name', ['field1', 'field2'])
    print(f"Multi Hash values: {hash_multi_result}")

    # 操作哈希 - 批量设置字段值
    redis_handler.hmset('hash_name', {'field1': 'value1', 'field2': 'value2'})

    # 操作列表
    redis_handler.push_to_list('list_name', 'list_value1')
    list_result = redis_handler.pop_from_list('list_name')
    print(f"List value: {list_result}")

    # 操作集合
    redis_handler.add_to_set('set_name', 'set_value1')
    redis_handler.remove_from_set('set_name', 'set_value1')

    # 操作有序集合
    redis_handler.add_to_sorted_set('zset_name', 'zset_value1', 1.0)
    zset_result = redis_handler.get_sorted_set_range('zset_name', 0, -1)
    print(f"Sorted Set values: {zset_result}")

    # 从有序集合中移除值
    redis_handler.remove_from_sorted_set('zset_name', 'zset_value1')
