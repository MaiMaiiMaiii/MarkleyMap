# Markley 四面体地图投影

MarkleyMap 是一个用于实验和研究 Markley 四面体地图投影的开源项目。

本项目提供投影实现、逆投影查找表，以及将全球栅格地形数据重新投影到 Markley 四面体布局的本地处理流程。当前 Python 流程可以读取 ETOPO 2022 全球地形数据和 Natural Earth I 地表颜色数据，并在用户本地生成自然地形渲染结果。

本仓库不分发预生成的完整世界地图图片。

## 投影方法

地图布局采用 F. Landis Markley 描述的四面体地图投影方案：

F. Landis Markley, *Tetrahedral Map Projection*, 24 October 2020.

仓库附带 `lookup.bin` 和 `lookup.json`，它们是当前 Python 投影流程使用的 480 × 208 逆投影查找表。

当前处理流程直接读取这些查找表，因此不需要运行 Node.js。仓库目前没有包含重新生成查找表的脚本。

## 数据来源

### 地形与海底深度：ETOPO 2022

处理流程使用 NOAA National Centers for Environmental Information（NCEI）发布的 ETOPO 2022 全球地形与海底地形数据。

当前脚本使用：

`ETOPO 2022 Ice Surface, 60 arc-second GeoTIFF`

本地输入文件名：

`etopo.tif`

该数据同时包含陆地高程、冰面高程以及海底深度信息。

数据 DOI：

`10.25921/fd45-gt74`

请从 NOAA/NCEI 官方渠道获取数据，并参阅其数据说明和许可条件。

### 陆地颜色：Natural Earth I

陆地颜色使用 Natural Earth I 栅格数据：

`NE1_HR_LC`

当前流程使用版本：

`3.2.0`

本地输入归档文件名：

`land-color.zip`

该图层用于提供自然地表颜色。海洋颜色不直接来自 Natural Earth，而是在渲染过程中根据 ETOPO 海底深度生成。

Natural Earth 名称中的 `1:10m` 表示约 1:10,000,000 的地图比例尺，不表示 10 米地面分辨率。

请从 Natural Earth 官方渠道获取数据并查看其使用条款。

## 使用方法

需要 Python 3。

安装 Python 处理流程所需依赖：

```bash
python -m pip install numpy scipy Pillow rasterio
```

然后依次运行：

```bash
python download-relief-data.py
python project-relief.py
python render-relief-natural-color.py
```

### 1. 下载输入数据

```bash
python download-relief-data.py
```

脚本下载当前处理流程需要的 ETOPO 和 Natural Earth 数据，并创建：

```text
relief-cache/
```

如果对应输入文件已经存在，脚本会跳过下载。

如果下载中断或文件损坏，请删除相应输入文件后重新运行。

### 2. 执行投影

```bash
python project-relief.py
```

该脚本使用输入数据以及仓库中的逆投影查找表，对高程和地表颜色数据进行投影和采样。

生成的中间数据保存在：

```text
relief-cache/
```

当前投影栅格主体尺寸为：

```text
15360 × 6651
```

处理采用分块缓存方式。已经完成且尺寸匹配的分块会被重复利用，因此任务中断后通常可以重新运行脚本继续处理。

### 3. 本地渲染

```bash
python render-relief-natural-color.py
```

该脚本读取投影后的缓存数据，在本地生成：

```text
markley-natural-color-16k.png
```

当前脚本只生成最大尺寸输出，不接受输出尺寸参数。

完整流程需要下载约数百 MB 的输入数据，并产生额外的投影缓存和输出文件。高分辨率投影及渲染可能消耗数 GB 内存和较大的磁盘空间。

## 输出说明

默认输出尺寸为：

```text
15360 × 6651
```

这里的“16K”仅表示图像宽度约为 16K 像素。

图片保持 Markley 四面体投影布局自身的长宽比例，因此不是 15360 × 8640 的 16:9 图像。

输出像素数量不会提高上游数据本身的空间精度。高分辨率栅格主要用于减少投影和渲染过程中的视觉锯齿及采样损失。

生成的地图图片属于本地运行结果，本仓库目前不提供预生成地图成品下载。

## 仓库文件

| 文件                               | 用途                    |
| -------------------------------- | --------------------- |
| `download-relief-data.py`        | 下载处理流程需要的输入数据         |
| `project-relief.py`              | 对高程和地表颜色数据进行投影和采样     |
| `render-relief-natural-color.py` | 从投影缓存生成本地 PNG         |
| `projection.mjs`                 | JavaScript 投影实现       |
| `lookup.bin`                     | Python 流程使用的二进制逆投影查找表 |
| `lookup.json`                    | 逆投影查找表的 JSON 表示       |
| `package.json`                   | JavaScript 依赖和项目配置    |
| `package-lock.json`              | JavaScript 依赖锁定文件     |

以下文件由本地流程下载或生成，通常不提交到源码仓库：

```text
etopo.tif
land-color.zip
relief-cache/
markley-natural-color-16k.png
```

## 数据与生成结果

ETOPO、Natural Earth 等上游数据分别受各自的数据使用条件约束。

本仓库提供的是处理和投影代码；通过这些代码生成的地图或其他地理信息产品是否适合公开发布，应根据发布者所在地以及拟发布地区适用的地图、测绘和地理信息相关规定另行判断。

因此，本仓库目前仅提供代码和本地处理流程，不直接提供预生成的完整地图图片。
