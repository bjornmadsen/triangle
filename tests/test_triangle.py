import numpy as np
import pytest

from triangle import triangulate, convex_hull, voronoi, delaunay


def test_triangulate():
    v = [[0, 0], [0, 1], [1, 1], [1, 0]]
    t = triangulate({"vertices": v}, "a0.2")
    assert np.allclose(
        t["vertices"],
        [
            [0.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0],
            [1.0, 0.0],
            [0.5, 0.5],
            [0.0, 0.5],
            [0.5, 0.0],
            [1.0, 0.5],
            [0.5, 1.0],
        ],
    )
    assert np.allclose(
        t["vertex_markers"],
        [[1], [1], [1], [1], [0], [1], [1], [1], [1]],
    )
    assert np.allclose(
        t["triangles"],
        [
            [7, 2, 4],
            [5, 0, 4],
            [4, 8, 1],
            [4, 1, 5],
            [4, 0, 6],
            [6, 3, 4],
            [4, 3, 7],
            [4, 2, 8],
        ],
    )


def test_delaunay():
    pts = [[0, 0], [0, 1], [0.5, 0.5], [1, 1], [1, 0]]
    tri = delaunay(pts)
    assert np.allclose(
        tri,
        [
            [1, 0, 2],
            [2, 4, 3],
            [4, 2, 0],
            [2, 3, 1],
        ],
    )


def test_hull():
    pts = [[0, 0], [0, 1], [1, 1], [1, 0]]
    segments = convex_hull(pts)
    assert np.allclose(segments, [[3, 0], [2, 3], [1, 2], [0, 1]])


def test_voronoi():
    pts = [[0, 0], [0, 1], [0.5, 0.5], [1, 1], [1, 0]]
    points, edges, ray_origin, ray_direct = voronoi(pts)
    assert np.allclose(
        points,
        [[0.0, 0.5], [1.0, 0.5], [0.5, 0.0], [0.5, 1.0]],
    )
    assert np.allclose(edges, [[0, 2], [0, 3], [1, 2], [1, 3]])

    assert np.allclose(ray_origin, [0, 1, 2, 3])
    assert np.allclose(
        ray_direct,
        [[-1.0, 0.0], [1.0, 0.0], [0.0, -1.0], [0.0, 1.0]],
    )


# Inputs that used to crash or hang Triangle.  Each runs in a subprocess so a
# regression fails the test instead of killing or hanging the test run.
_RING6 = [[i, (i + 1) % 6] for i in range(6)]
_RING8 = [[i, (i + 1) % 8] for i in range(8)]

_INVALID_INPUTS = {
    # All vertices identical: divide-and-conquer recursed on one vertex.
    "identical_vertices": {"vertices": [[0.5, 0.5]] * 3},
    # Nearly parallel overlapping segments: degenerate split corrupted mesh.
    "parallel_crash": {
        "vertices": [
            [57.54438, 58.89617],
            [58.18274, 58.89638],
            [57.11879, 58.89602],
            [58.35055, 58.89644],
            [57.83629, 58.89626],
            [57.89343, 58.89628],
        ],
        "segments": _RING6,
    },
    # Nearly parallel overlapping segments: finddirection() looped forever.
    "parallel_hang": {
        "vertices": [
            [3.88, 36.26],
            [4.15, 35.01],
            [3.68, 37.14],
            [3.74, 36.88],
            [3.89, 36.19],
            [3.59, 37.54],
            [3.85, 36.37],
            [3.63, 37.4],
        ],
        "segments": _RING8,
    },
    # Collinear vertex outside the segment: scoutsegment() recursed forever.
    "collinear_overshoot": {
        "vertices": [
            [55.23, 64.57],
            [55.47, 64.45],
            [55.05, 64.66],
            [56.85, 63.76],
            [55.37, 64.5],
            [56.91, 63.73],
        ],
        "segments": _RING6,
    },
    # Intersection vertex rounded off its segment left an inverted triangle.
    "parallel_inverted": {
        "vertices": [
            [22.14, 74.93],
            [24.26, 74.12],
            [22.02, 74.96],
            [23.42, 74.44],
            [25.37, 73.69],
            [25.94, 73.49],
            [24.18, 74.15],
            [23.59, 74.37],
        ],
        "segments": _RING8,
    },
    # Intersection 1e-13 from an unrelated vertex: flips inverted a triangle.
    "intersection_near_vertex": {
        "vertices": [
            [89.14, 59.49],
            [88.42, 58.85],
            [89.13, 59.49],
            [88.25, 58.69],
            [89.14, 59.5],
            [88.08, 58.54],
            [88.69, 59.09],
        ],
        "segments": [[i, (i + 1) % 7] for i in range(7)],
    },
}

_RUNNER = """
import json, sys
import triangle
tri, opts = json.loads(sys.argv[1])
try:
    out = triangle.triangulate(tri, opts)
except RuntimeError:
    print("RESULT", json.dumps("RuntimeError"))
else:
    print("RESULT", json.dumps(out["triangle_attributes"].ravel().tolist()))
"""


def _run_isolated(tri, opts):
    import json
    import subprocess
    import sys

    proc = subprocess.run(
        [sys.executable, "-c", _RUNNER, json.dumps([tri, opts])],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    # Triangle's own diagnostics share stdout, so pick out the tagged line.
    (result,) = [ln for ln in proc.stdout.splitlines() if ln.startswith("RESULT ")]
    return json.loads(result[len("RESULT ") :])


def test_region_point_outside_boundary():
    # Region point beyond a boundary edge of a sliver made locate() walk into
    # the dummy triangle and crash.
    tri = {
        "vertices": [[0.023, 0], [0.98, 0.001], [0, 0]],
        "segments": [[0, 1], [0, 2], [1, 2]],
        "regions": [[0.94757, 0.00097, 1, 0]],
    }
    assert _run_isolated(tri, "pA") == [0.0]


@pytest.mark.parametrize("name", sorted(_INVALID_INPUTS))
def test_invalid_input_raises(name):
    assert _run_isolated(_INVALID_INPUTS[name], "p") == "RuntimeError"
