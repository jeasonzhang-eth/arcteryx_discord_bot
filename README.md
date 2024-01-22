项目业务逻辑

本项目包括以下业务逻辑：

1. 每天自动扫描arcteryx网站当前有多少个product，扫描完成后，可以获取到每个product的link以及sku。根据link和sku，就可以构建product的link到sku映射（build_link_sku_mapping.py）。这一步耗时2秒左右。
2. 上一步中，我们拿到了所有product的link。第二步就是遍历所有link，获取单个product的详细信息。包括该product有几个颜色，几个尺码，对应颜色尺码的product的库存。variant代表子型号，举个例子，某件夹克有5个颜色，每个颜色有5个尺码。那么这个夹克有5*5=25个子型号。红色s码是一个子型号，黄色xl码也是一个子型号(get_next_data.py)。这一步非常耗时，每个product耗时3秒左右，如果400个product就是1200秒，所以适合日更。
3. 经过上面两步后，我们已经获取到了arcteryx网站的所有商品、所有子型号的库存。但是product的库存是时刻在发生变化的。（get_next_data.py）这个文件虽然也可以获取到库存，但是速度太慢了。所以我找了一个新方法来快速获取库存，此方法主要用于针对客户请求。（get_price.py）

redis数据库设计

1. product的link-sku映射表

| 变量名称    | link_sku_mapping |
| ----------- | ---------------- |
| 类型        | hash             |
| 数据项key   | product的链接    |
| 数据项value | product的sku号码 |

举例

```
link_sku_mapping
    https://arcteryx.com/us/en/shop/womens/practitioner-ar-hoody  X000004614
    https://arcteryx.com/us/en/shop/womens/ski-guide-bib-pant  X000004670
```

2. 每个product的详细信息

|               |                    | 解释                                                                                                 |
| ------------- | ------------------ | ---------------------------------------------------------------------------------------------------- |
| 变量名称      |                    | 商品的sku号码                                                                                        |
| 类型          |                    | hash                                                                                                 |
|               | 数据类型           |                                                                                                      |
| link          | string             | 该商品的链接                                                                                         |
| slug          | string             | 该商品的名称                                                                                         |
| market        | string             | 该商品所属的市场                                                                                     |
| variants_list | json序列化后的列表 | 该商品所拥有的子型号的具体信息,子型号的数量等于颜色数量*尺码数量，比如3种颜色5个尺码，就是15个子型号 |
| color_mapping | json序列化后的字典 | 该商品的颜色-编号映射表                                                                              |
| size_mapping  | json序列化后的字典 | 该商品的尺寸-编号映射表                                                                              |
| last_update   | 时间字符串         | 该数据最后更新时间                                                                                   |

举例

```plaintext
X000004670
    link  https://arcteryx.com/us/en/shop/womens/ski-guide-bib-pant
    slug  'womens/ski-guide-bib-pant'
    market  'outdoor'
    variants  [{'variant_sku': 'X000004670004', 'upc': '686487613768', 'color_id': '1836', 'size_id': '5995', 'color': 'Black', 'size': 'L', 'inventory': 1, 'price': 800, 'discount_price': None}, {'variant_sku': 'X000004670005', 'upc': '686487613782', 'color_id': '1836', 'size_id': '6020', 'color': 'Black', 'size': 'S', 'inventory': 1, 'price': 800, 'discount_price': None}, {'variant_sku': 'X000004670003', 'upc': '686487613799', 'color_id': '1836', 'size_id': '6035', 'color': 'Black', 'size': 'XL', 'inventory': 0, 'price': 800, 'discount_price': None}, {'variant_sku': 'X000004670002', 'upc': '686487613805', 'color_id': '1836', 'size_id': '6042', 'color': 'Black', 'size': 'XS', 'inventory': 1, 'price': 800, 'discount_price': None}, {'variant_sku': 'X000004670001', 'upc': '686487613775', 'color_id': '1836', 'size_id': '6004', 'color': 'Black', 'size': 'M', 'inventory': 0, 'price': 800, 'discount_price': None}]
    color_mapping  {'1836': 'Black'}
    size_mapping  {'5995': 'L', '6004': 'M', '6020': 'S', '6035': 'XL', '6042': 'XS'}
    last_update  
```

3. 颜色-编号映射表（color_mapping）

| color_mapping | 解释           |
| ------------- | -------------- |
| 类型          | 字典           |
| 数据key       | 颜色编号       |
| 数据value     | 编号对应的颜色 |

举例

```json
{
   '1836': ''black
}
```

4. 型号-编号映射表(size_mapping)

举例

| size_mapping | 解释         |
| ------------ | ------------ |
| 类型         | 字典         |
| 数据key      | 尺码编号     |
| 数据value    | 编号对应尺码 |

```json
{
    '5995': 'L', 
    '6004': 'M', 
    '6020': 'S', 
    '6035': 'XL', 
    '6042': 'XS'
}
```

5. 子型号的各项数据

| variant        | 解释         |
| -------------- | ------------ |
| 类型           | 字典         |
| variant_sku    | 子型号的sku  |
| upc            | 货号         |
| color_id       | 颜色编号     |
| size_id        | 尺码编号     |
| color          | 子型号的颜色 |
| size           | 子型号的尺码 |
| inventory      | 库存         |
| price          | 价格         |
| discount_price | 折扣价       |

举例

```json
{
    'variant_sku': 'X000004670004',
    'upc': '686487613768',
    'color_id': '1836',
    'size_id': '5995',
    'color': 'Black',
    'size': 'L',
    'inventory': 1,
    'price': 800,
    'discount_price': None
}
```

part1：每天自动扫描商品信息，比对




### bot自动管理

本项目使用一个linux脚本来对机器人进行管理，bot_manager.sh

使用以下命令赋予脚本执行权限：

1. ```bash
   chmod +x bot_manager.sh
   ```

### 使用说明

- **启动机器人：**

  ```bash
  ./bot_manager.sh start
  ```
- **关闭机器人：**

  ```bash
  ./bot_manager.sh stop
  ```
- **重启机器人：**

  ```bash
  ./bot_manager.sh restart
  ```

### 注意事项

1. 请确保脚本和 `bot.py` 文件在相同的目录下。
2. 请确保已正确安装并配置 Conda，并且 `conda` 命令位于系统的 `PATH` 中。
3. 请确保 Conda 环境的名称正确，可以在脚本中修改 `CONDA_ENV` 变量。
