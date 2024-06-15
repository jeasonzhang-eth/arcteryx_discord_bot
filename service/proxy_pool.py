import random


def main():
    proxy_list = []
    with open('proxy.txt') as f:
        for line in f:
            proxy_info = line.split(':')
            ip = proxy_info[0]
            prot = proxy_info[1]
            username = proxy_info[2]
            password = proxy_info[3]
    proxy = random.choice(proxy_list)


if __name__ == '__main__':
    main()