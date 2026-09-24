from pathlib import Path
from urllib.request import urlretrieve
sources={
 'etopo.tif':'https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/60s/60s_surface_elev_gtif/ETOPO_2022_v1_60s_N90W180_surface.tif',
 'land-color.zip':'https://naturalearth.s3.amazonaws.com/10m_raster/NE1_HR_LC.zip'
}
for name,url in sources.items():
 if not Path(name).exists():
  print('Downloading',name,flush=True);urlretrieve(url,name)
Path('relief-cache').mkdir(exist_ok=True)
