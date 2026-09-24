# Markley 四面体浮雕地图

本项目将全球地形与地表颜色数据重投影为 Markley 四面体地图，并生成一张高分辨率 PNG。

## 投影方法

地图布局采用 F. Landis Markley 描述的四面体地图方案：

> F. Landis Markley, “Tetrahedral Map Projection,” 24 October 2020. [论文 PDF](https://observablehq.observablehq.cloud/pangea/_file/projections/Tetrahedral-map-projection-with-appendix.5e874c75.pdf)

仓库附带 `lookup.bin` 和 `lookup.json`，是 Python 投影流程使用的 **480 × 208** 逆投影查找表。当前流程直接读取该表，不需要运行 Node.js；本仓库没有重新生成查找表的脚本。

## 地图数据来源

### 地形和海底深度：ETOPO 2022

使用 NOAA 国家环境信息中心（NCEI）的全球地形与海底地形数据：**ETOPO 2022 Ice Surface，60 角秒 GeoTIFF**。输入文件为 `etopo.tif`，同时提供陆地高程、冰面高程和海底深度。

- [NOAA ETOPO Global Relief Model](https://www.ncei.noaa.gov/products/etopo-global-relief-model)
- 数据 DOI：[10.25921/fd45-gt74](https://doi.org/10.25921/fd45-gt74)
- 脚本使用的 GeoTIFF：[ETOPO_2022_v1_60s_N90W180_surface.tif](https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/60s/60s_surface_elev_gtif/ETOPO_2022_v1_60s_N90W180_surface.tif)
- [数据元数据与许可信息](https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.mgg.dem%3Aetopo_2022)

### 陆地颜色：Natural Earth I

使用 Natural Earth I 栅格 **NE1_HR_LC，版本 3.2.0**，输入归档为 `land-color.zip`。该图层提供按地表覆盖着色的陆地底图；本项目的海洋颜色则在渲染时根据 ETOPO 水深生成。

Natural Earth 名称中的 **1:10m** 表示地图比例尺 1:10,000,000，不表示 10 米地面分辨率。

- [Natural Earth I 1:10m 栅格说明与版本](https://www.naturalearthdata.com/downloads/10m-raster-data/10m-natural-earth-1/)
- [本项目使用的 NE1_HR_LC.zip](https://naturalearth.s3.amazonaws.com/10m_raster/NE1_HR_LC.zip)
- [Natural Earth 使用条款](https://www.naturalearthdata.com/about/terms-of-use/)（Natural Earth 网站声明其栅格和矢量地图数据属于公共领域。）

## 使用方法

在项目根目录准备 Python 3，然后安装 Python 渲染流程所需的依赖：

```bash
python -m pip install numpy scipy Pillow rasterio
```

按顺序运行三个脚本：

```bash
python download-relief-data.py
python project-relief.py
python render-relief-natural-color.py
```

1. `download-relief-data.py` 下载 `etopo.tif` 和 `land-color.zip`，并创建缓存目录 `relief-cache/`。如果同名文件已存在，脚本会跳过下载；文件损坏或下载不完整时，请先删除对应文件再运行。
2. `project-relief.py` 使用输入数据和仓库中的查找表，投影并采样高程与地表颜色，生成分块中间文件到 `relief-cache/`。地图主体固定为 **15360 × 6651** 像素。已完成且尺寸匹配的分块会被复用；中断后可重新运行此脚本继续计算。
3. `render-relief-natural-color.py` 读取完整缓存，生成最终图片 `markley-natural-color-16k.png`。该脚本只输出最大分辨率，不接受尺寸参数。

完整流程会下载约 600 MB 的输入数据，并额外生成缓存和 PNG。16K 投影与渲染需要数 GB 内存，运行前请确保磁盘空间和内存充足。

## 输出与文件

最终图片为 **15360 × 6651** 像素。这里的“16K”指宽度约 16K；图片保留投影主体的长宽比，因此不是 15360 × 8640 的 16:9 壁纸画布。输出像素数不会增加上游地图数据中没有的细节。

预生成的 16K PNG 通过本项目的 [GitHub Releases](https://github.com/MaiMaiiMaiii/MarkleyMap/releases) 分发，请前往 Releases 页面下载。

| 文件 | 用途 |
| --- | --- |
| `download-relief-data.py` | 下载两个地图数据源 |
| `project-relief.py` | 生成投影后的高程和地表颜色缓存 |
| `render-relief-natural-color.py` | 从缓存生成最大分辨率 PNG |
| `projection.mjs` | JavaScript 投影实现 |
| `lookup.bin`、`lookup.json` | Python 流程所需的预计算逆投影查找表 |
| `package.json`、`package-lock.json` | JavaScript 依赖清单；Python 主流程不需要运行 `npm install` |
| `etopo.tif`、`land-color.zip` | 下载的原始地图数据；首次运行时由下载脚本获取，通常不提交到源码仓库 |
| `relief-cache/` | 可重新生成的中间缓存 |
| `markley-natural-color-16k.png` | 本地渲染生成的图片；预生成发布版从 GitHub Releases 下载 |
