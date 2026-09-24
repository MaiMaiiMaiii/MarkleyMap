import json,io,zipfile,os,numpy as np,rasterio
from PIL import Image
from scipy.ndimage import map_coordinates,spline_filter
Image.MAX_IMAGE_PIXELS=None
m=json.load(open('lookup.json')); w,h=m['width'],m['height'];v=np.fromfile('lookup.bin',dtype=np.float64).reshape(h,w,3)
def pad(a,axis,n=4):
 a=np.moveaxis(a,axis,0); r=np.empty((len(a)+2*n,)+a.shape[1:]);r[n:-n]=a
 for j in range(n):
  t=-j-1; ww=[np.prod([(t-k)/(i-k) for k in range(4) if k!=i]) for i in range(4)]
  r[n-1-j]=np.einsum('i,i...->...',ww,a[:4]);r[-n+j]=np.einsum('i,i...->...',ww,a[-4:][::-1])
 return np.moveaxis(r,0,axis)
coef=[spline_filter(c,order=3) for c in np.moveaxis(pad(pad(v,0),1),2,0)]
with rasterio.open('etopo.tif') as f:
 print('DEM',f.shape,f.bounds,f.transform,f.nodata,flush=True)
 dem=f.read(1,out_dtype='float32')
 print('elevation range',float(dem.min()),float(dem.max()),flush=True)
z=zipfile.ZipFile('land-color.zip');name=next(n for n in z.namelist() if n.endswith('.tif'))
im=Image.open(io.BytesIO(z.read(name))).convert('RGB');base=np.array(im);del im,z
print('albedo',base.shape,flush=True)
W=15360;H=round(W*np.sqrt(3)/4)
for y in range(0,H,64):
 try:
  with np.load(f"relief-cache/{y//64:03}.npz") as old:
   assert old["elevation"].shape==(min(64,H-y),W); assert old["color"].shape==(min(64,H-y),W,3)
  continue
 except Exception: pass
 stop=min(y+64,H); yy,xx=np.meshgrid((np.arange(y,stop)+.5)*h/H-.5+4,(np.arange(W)+.5)*w/W-.5+4,indexing='ij')
 p=np.array([map_coordinates(c,[yy,xx],order=3,prefilter=False) for c in coef]);p/=np.linalg.norm(p,axis=0)
 lon=np.arctan2(p[1],p[0]);lat=np.arcsin(np.clip(p[2],-1,1));u=((lon/(2*np.pi)+.5)*21600-.5)%21600;vv=np.clip((.5-lat/np.pi)*10800-.5,0,10799)
 elev=map_coordinates(dem,[vv,u],order=1,prefilter=False,mode='nearest')
 rgb=np.stack([map_coordinates(base[:,:,c],[vv,u],order=1,prefilter=False,mode='nearest') for c in range(3)],axis=-1)
 np.savez_compressed(f'relief-cache/{y//64:03}.npz',elevation=elev.astype(np.float32),color=rgb)
 if y%512==0:print('projected',y,'/',H,flush=True)
json.dump({'width':W,'height':H,'tiles':(H+63)//64},open('relief-cache/info.json','w'))
print('projection complete',flush=True)
