import * as geo from "d3-geo";
import * as poly from "d3-geo-polygon";
function _tetrahedralMarkleyRaw(d3,rotate,sqrt3_4,degrees,radians)
{
  const rawLee = d3
    .geoTetrahedralLee()
    .rotate(rotate)
    .fitExtent([[-4, -1.5 / sqrt3_4], [4, 1.5 / sqrt3_4]], {
      type: "Sphere"
    });

  const forward = (l, p) => {
    let [x, y] = rawLee([l * degrees, p * degrees]);
    if (y < 0) {
      x = -x - 4;
      if (x < -5) x += 8;
      y = -y;
    }
    if (x > 3) x -= 8;
    return [x, -y];
  };

  // see the diagram for colors
  forward.invert = (x, y) => {
    const a =
      rawLee.invert([x, -y]) || // green
      (x > 0 && rawLee.invert([4 - x, y])) || // orange
      (x < 0 && rawLee.invert([-4 - x, y])) || // red
      (x < 0 && rawLee.invert([8 + x, -y])); // blue

    if (a) return [a[0] * radians, a[1] * radians];
  };

  return forward;
}


export const raw = _tetrahedralMarkleyRaw({...geo,...poly},[115,Math.acos(1/3)*90/Math.PI-90,180],Math.sqrt(3)/4,180/Math.PI,Math.PI/180);
