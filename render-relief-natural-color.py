import json

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


DEFAULT_WIDTH = 15360

m = json.load(open("relief-cache/info.json"))
tiles = [np.load(f"relief-cache/{i:03}.npz") for i in range(m["tiles"])]
z = np.concatenate([tile["elevation"] for tile in tiles])
rgb = np.concatenate([tile["color"] for tile in tiles])
del tiles

W = DEFAULT_WIDTH
H = round(W * np.sqrt(3) / 4)
if m["width"] != W or z.shape != (H, W) or rgb.shape != (H, W, 3):
    raise ValueError(
        "The relief cache is not 16K. Run project-relief.py to build the 15360-pixel cache first."
    )

scale = 1.0

# Apply restrained contrast and saturation so the land colors stay rich
# without becoming too dark.
land = np.clip(rgb.astype(np.float32) / 255, 0, 1)
land = np.clip((land - 0.12) / 0.88, 0, 1) ** 1.38
land_luma = land @ np.array([0.2126, 0.7152, 0.0722], np.float32)
color = np.clip(land_luma[:, :, None] + (land - land_luma[:, :, None]) * 1.30, 0, 1) ** 1.06
color *= np.array([1.015, 1.0, 0.97], np.float32)

# Lift the ocean tones while keeping a gradual depth-based teal-to-navy scale.
depth = np.maximum(-z, 0)
levels = [0, 200, 1000, 2500, 4000, 6000, 11000]
palette = np.array(
    [[53, 116, 129], [39, 94, 116], [27, 76, 104], [20, 59, 88],
     [15, 46, 73], [11, 34, 58], [8, 25, 44]],
    np.float32,
) / 255
ocean = np.stack(
    [np.interp(depth, levels, palette[:, c]) for c in range(3)], axis=-1
).astype(np.float32)
water = np.clip(-z / 60, 0, 1).astype(np.float32)
color = color * (1 - water[:, :, None]) + ocean * water[:, :, None]

# Preserve the relief lighting so the elevation remains visible. This changes
# pixel brightness locally but does not grade the underlying land-color palette.
smooth = gaussian_filter(z, max(0.55, 0.7 * scale))
gy, gx = np.gradient(smooth)
factor = (0.0038 * (1 - water) + 0.0055 * water) * scale
gx *= factor
gy *= factor
length = np.sqrt(1 + gx * gx + gy * gy)

az = np.deg2rad(38)
light = np.array([-0.62, -0.785, 0.0])
light[:2] *= np.cos(az)
light[2] = np.sin(az)
diff = np.clip((-gx * light[0] - gy * light[1] + light[2]) / length, 0, 1)
fill = np.clip((gx * 0.36 + gy * 0.30 + 0.88) / length, 0, 1)
shade = np.clip(0.33 + diff * 0.88 + fill * 0.13, 0.26, 1.35)

broad = gaussian_filter(z, max(0.8, 9 * scale))
by, bx = np.gradient(broad)
broadshade = np.clip(1 + (0.62 * bx + 0.785 * by) * scale * 0.0014, 0.75, 1.2)
shade *= broadshade
color *= shade[:, :, None]
color = np.clip(color, 0, 1)

# Save only the complete projected map at its native 16K width. The image
# keeps the projection's sqrt(3)/4 aspect ratio, with no canvas or edge fade.
image = Image.fromarray(np.rint(color * 255).astype(np.uint8))
image.save("markley-natural-color-16k.png")

print(
    "rendered", W, H,
    "height range", float(z.min()), float(z.max()),
    "finite", bool(np.isfinite(z).all()),
    flush=True,
)
