
def build_mapping():
    from service.build_link_sku_mapping import main
    main()


def get_product_information():
    from tools.redis_handler import RedisHandler
    from service.get_next_data import run
    rh = RedisHandler(host='localhost', port=6379, db=0, max_connections=5)
    hash_all_result = rh.hgetall('link_sku_mapping')
    for link, sku in hash_all_result.items():
        while run(link, rh):
            break


def main():
    """
    本文件用来每天自动更新全部数据
    :return:
    """
    # build_mapping()
    get_product_information()


if __name__ == '__main__':
    main()

