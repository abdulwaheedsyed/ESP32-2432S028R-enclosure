"""
Rugged 45-degree desk wedge enclosure for the ESP32-2432S028R "Cheap Yellow Display",
dual-USB (micro-USB + USB-C, a.k.a. CYD2USB) revision.

Two parts, both print without supports in PLA:
  * front bezel  - prints face-down on the bed
  * rear wedge   - prints standing on its flat base

Fastening: 4x M3x16 socket-head screws inserted from the back/bottom of the wedge,
through the CYD mounting holes, into 4x M3 heat-set inserts (short, 4 mm long)
in the bezel. Self-tapping variant of the bezel is also exported.

Coordinate frame used for all board features ("board frame"):
  x : along the long (86 mm) edge, USB ports at -x
  y : along the short (50 mm) edge, microSD slot at +y
  z : out of the display; PCB back face at z = 0, PCB front at z = 1.6
Origin = centre of the PCB. Sources: manufacturer drawings (Shenzhen Jingcai
ESP32-2432S028R spec + JC2432A028N LCD drawing) cross-checked against a
known-good USB-C CYD case.

Run:  python3 cyd_wedge_case.py   (needs cadquery)
"""
import math
import os
import cadquery as cq

OUT = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ board
PCB_X0, PCB_X1 = -43.0, 43.0
PCB_Y = 25.0
PCB_T = 1.6
HOLE_X, HOLE_Y = 39.0, 21.0             # 78 x 42 mm hole pitch
DISP_TOP = 5.2                          # touch-panel surface above PCB back
AA_CX = 2.6                             # active-area centre (offset away from USB end)
VA_W, VA_H = 60.9, 46.2                 # LCD viewing area -> bezel window
LDR = (36.15, 40.15, 10.4, 16.9)        # light-sensor window x0,x1,y0,y1

# USB end: one generous slot that clears both plugs (USB-C + micro-USB overmolds).
# Port positions on the dual-USB board are not in any drawing, so the slot is sized
# to cover the plausible layouts; print the fit-test piece first.
USB_Y0, USB_Y1 = -9.5, 17.3
USB_Z0, USB_Z1 = -5.8, 2.7
# microSD card slot in the +y wall
SD_X0, SD_X1 = -11.5, 4.0
SD_Z0, SD_Z1 = -2.6, 0.4

# ------------------------------------------------------------------ case
FACE_IN = DISP_TOP + 1.0                # 1 mm air gap over the touch panel
FACE_T = 2.5
FACE_OUT = FACE_IN + FACE_T             # bezel lip 3.5 mm above the glass
RIM_Z = -7.5                            # bezel / wedge split plane
CAV_X0, CAV_X1 = -44.3, 43.6            # extra room at the USB end for protruding receptacles
CAV_Y = 25.5
WALL = 3.5
OUT_X = 47.8
OUT_Y = CAV_Y + WALL                    # 29.0
CORNER_R = 5.2                          # plan-view corner radius (drop bumpers)
FACE_CHAMFER = 1.5
WIN_CHAMFER = 1.5

BOSS_D = 7.4                            # bezel boss around heat-set insert
INSERT_D = 4.1                          # hole for M3 heat-set insert (4 mm or 5.7 mm long)
SELFTAP_D = 2.6                         # pilot hole if screwing straight into PLA
INSERT_TOP = 7.4                        # blind hole top (1.3 mm skin left on the face)
POST_D = 6.4                            # wedge post under PCB
POST_D_NEAR_BUTTONS = 5.4               # slimmer post next to the BOOT/RST switches
SCREW_CLR_D = 3.4
HEAD_D = 6.4                            # bore for M3 socket head (5.5) + hex key
SEAT_Z = -9.3                           # head seat -> M3x16 tip ends at z=6.7 inside the insert

RIDGE_H = 2.0                           # locating ridge on wedge, keys into the bezel
RIDGE_W = 2.0
RIDGE_CLR = 0.25

HEEL_Y = 66.0                           # base length; long heel stops it tipping when touched
HEEL_H = 4.0                            # blunt heel end
KNEE_Z = 17.0                           # where the vertical back turns into the heel ramp
FOOT_D, FOOT_DEPTH = 10.5, 0.8          # recesses for stick-on rubber bumpers

S2 = math.sqrt(0.5)


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane().box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def rbox(x0, x1, y0, y1, z0, z1, r, axis="|Z"):
    b = box(x0, x1, y0, y1, z0, z1)
    return b.edges(axis).fillet(r) if r > 0 else b


def cyl(x, y, z0, z1, d):
    return cq.Workplane().circle(d / 2).extrude(z1 - z0).translate((x, y, z0))


def to_world(wp):
    """board frame -> desk frame (base on Z=0, screen facing -Y and up at 45 deg)."""
    return wp.translate((0, OUT_Y, -RIM_Z)).rotate((0, 0, 0), (1, 0, 0), 45)


def to_board(wp):
    return wp.rotate((0, 0, 0), (1, 0, 0), -45).translate((0, -OUT_Y, RIM_Z))


HOLES = [(sx * HOLE_X, sy * HOLE_Y) for sx in (-1, 1) for sy in (-1, 1)]

# ------------------------------------------------------------------ outer body (desk frame)
# Side profile (Y, Z): A = bottom of split line, T = top of split line,
# B/F = bottom/top edge of the bezel face, K = knee of the back, H1/H2 = heel.
# The back is vertical where the upper screws come out so they exit at a clean 45 deg.
depth = FACE_OUT - RIM_Z
L = 2 * OUT_Y
A = (0.0, 0.0)
T = (L * S2, L * S2)
B = (-depth * S2, depth * S2)
F = (T[0] - depth * S2, T[1] + depth * S2)
K = (T[0], KNEE_Z)
H2 = (HEEL_Y, HEEL_H)
H1 = (HEEL_Y, 0.0)

profile = [A, H1, H2, K, T, F, B]
body = cq.Workplane("YZ").workplane(offset=-OUT_X).polyline(profile).close().extrude(2 * OUT_X)


def long_edge(p):
    def f(e):
        a, b = e.startPoint(), e.endPoint()
        return (abs(a.y - p[0]) < 1e-3 and abs(a.z - p[1]) < 1e-3 and
                abs(b.y - p[0]) < 1e-3 and abs(b.z - p[1]) < 1e-3)
    return f


def side_edge_except(*skip, heel=False):
    """edges on the two flat side faces, except the ones running between given point pairs.
    heel=False leaves out the short heel step, heel=True selects only that step."""
    skip = [{(round(p[0], 3), round(p[1], 3)), (round(q[0], 3), round(q[1], 3))} for p, q in skip]

    def f(e):
        a, b = e.startPoint(), e.endPoint()
        if abs(abs(a.x) - OUT_X) > 1e-3 or abs(a.x - b.x) > 1e-3:
            return False
        ends = {(round(a.y, 3), round(a.z, 3)), (round(b.y, 3), round(b.z, 3))}
        on_heel = min(a.y, b.y) > HEEL_Y - 3
        return ends not in skip and on_heel == heel
    return f


def pick(wp, *preds):
    edges = [e for e in wp.val().Edges() if any(pr(e) for pr in preds)]
    return wp.newObject(edges)


body = pick(body, long_edge(T), long_edge(K)).fillet(8.0)
body = pick(body, long_edge(H2)).fillet(3.0)
# round every side edge (bezel plan corners + wedge flanks) except the bed edges:
# the bezel face (chamfered below) and the wedge base
body = pick(body, side_edge_except((B, F), (A, H1))).fillet(CORNER_R)
# chamfer around the bezel face (bed-friendly, and a crumple edge for drops)
body_b = to_board(body)
body_b = body_b.faces(">Z").edges().chamfer(FACE_CHAMFER)

# ------------------------------------------------------------------ split
BIG = 300
front_half = body_b.intersect(box(-BIG, BIG, -BIG, BIG, RIM_Z, BIG))
rear_half = body_b.intersect(box(-BIG, BIG, -BIG, BIG, -BIG, RIM_Z))

# ------------------------------------------------------------------ front bezel
def make_bezel(hole_d):
    bz = front_half.cut(rbox(CAV_X0, CAV_X1, -CAV_Y, CAV_Y, RIM_Z - 1, FACE_IN, 2.5))

    # screen window = LCD viewing area, chamfered outward for finger/stylus reach
    wx0, wx1 = AA_CX - VA_W / 2, AA_CX + VA_W / 2
    bz = bz.cut(rbox(wx0, wx1, -VA_H / 2, VA_H / 2, FACE_IN - 1, FACE_OUT + 1, 1.0))
    bz = bz.edges(cq.selectors.BoxSelector((wx0 - 0.5, -VA_H / 2 - 0.5, FACE_OUT - 0.1),
                                           (wx1 + 0.5, VA_H / 2 + 0.5, FACE_OUT + 0.1))
                  ).chamfer(WIN_CHAMFER)

    # light sensor: window + light barrier so the backlight doesn't leak into the LDR
    lx0, lx1, ly0, ly1 = LDR
    barrier = box(34.7, CAV_X1 + 0.5, ly0 - 1.8, ly1 + 1.3, 3.0, FACE_IN + 0.1)
    bz = bz.union(barrier)
    bz = bz.cut(box(lx0 - 0.65, lx1 + 0.65, ly0 - 1.0, ly1 + 0.3, 2.9, FACE_IN + 0.01))
    bz = bz.cut(rbox(lx0, lx1, ly0, ly1, FACE_IN - 1, FACE_OUT + 1, 0.5))

    # insert bosses, tied into the corners with gussets
    for hx, hy in HOLES:
        sx, sy = math.copysign(1, hx), math.copysign(1, hy)
        cx = CAV_X1 + 0.5 if sx > 0 else CAV_X0 - 0.5
        cy = sy * (CAV_Y + 0.5)
        bz = bz.union(cyl(hx, hy, PCB_T, FACE_IN + 0.1, BOSS_D))
        bz = bz.union(box(min(hx, cx), max(hx, cx), min(hy, cy), max(hy, cy), PCB_T, FACE_IN + 0.1))
    for hx, hy in HOLES:
        bz = bz.cut(cyl(hx, hy, PCB_T - 0.1, INSERT_TOP, hole_d))

    # USB-C + micro-USB slot (USB end wall)
    usb = (cq.Workplane().box(10, USB_Y1 - USB_Y0, USB_Z1 - USB_Z0, centered=False)
           .translate((-OUT_X - 2, USB_Y0, USB_Z0)).edges("|X").fillet(2.5))
    bz = bz.cut(usb)

    # microSD slot + fingernail pocket
    bz = bz.cut(rbox(SD_X0, SD_X1, CAV_Y - 1, OUT_Y + 2, SD_Z0, SD_Z1, 0.8, "|Y"))
    bz = bz.cut(rbox(SD_X0 - 3, SD_X1 + 3, OUT_Y - 1.4, OUT_Y + 2, SD_Z0 - 2.4, SD_Z1 + 2.2, 2.0, "|Y"))
    return bz


# ------------------------------------------------------------------ rear wedge
def make_wedge():
    wd = rear_half

    # locating ridge that keys inside the bezel walls (takes side impacts off the screws)
    ox0, ox1, oy = CAV_X0 + RIDGE_CLR, CAV_X1 - RIDGE_CLR, CAV_Y - RIDGE_CLR
    ring = rbox(ox0, ox1, -oy, oy, RIM_Z - 0.1, RIM_Z + RIDGE_H, 2.25).cut(
        rbox(ox0 + RIDGE_W, ox1 - RIDGE_W, -oy + RIDGE_W, oy - RIDGE_W,
             RIM_Z - 1, RIM_Z + RIDGE_H + 1, 0.5))
    ring = ring.cut(box(CAV_X0 - 1, CAV_X0 + RIDGE_W + 2, USB_Y0 - 1, USB_Y1 + 1, -BIG, BIG))
    wd = wd.union(ring)

    # posts that clamp the PCB at its 4 mounting holes
    for hx, hy in HOLES:
        d = POST_D_NEAR_BUTTONS if (hx > 0 and hy < 0) else POST_D
        wd = wd.union(cyl(hx, hy, RIM_Z - 0.1, 0.0, d))
    for hx, hy in HOLES:
        wd = wd.cut(cyl(hx, hy, SEAT_Z - 0.01, 0.1, SCREW_CLR_D))
        wd = wd.cut(cyl(hx, hy, -BIG, SEAT_Z, HEAD_D))

    wd = to_world(wd)

    # stick-on rubber feet recesses (stop it sliding when you tap the screen)
    for fx, fy in [(-27, 7.0), (27, 7.0), (-36, HEEL_Y - 10), (36, HEEL_Y - 10)]:
        wd = wd.cut(cyl(fx, fy, -1, FOOT_DEPTH, FOOT_D))
    return wd


def bezel_print_pose(bz):
    # face down on the bed
    return bz.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, FACE_OUT))


if __name__ == "__main__":
    bezel = make_bezel(INSERT_D)
    bezel_st = make_bezel(SELFTAP_D)
    wedge = make_wedge()

    # quick print to check the USB slot against your board before the full bezel
    fit_test = bezel.intersect(box(-BIG, -33.0, -BIG, BIG, -BIG, BIG))

    exports = {
        "CYD2USB_wedge_front_bezel_heatset.stl": bezel_print_pose(bezel),
        "CYD2USB_wedge_front_bezel_selftap.stl": bezel_print_pose(bezel_st),
        "CYD2USB_wedge_rear_wedge.stl": wedge,
        "CYD2USB_wedge_fit_test_usb_end.stl": bezel_print_pose(fit_test),
    }
    for name, part in exports.items():
        path = os.path.join(OUT, name)
        cq.exporters.export(part, path, tolerance=0.01, angularTolerance=0.1)
        try:  # drop zero-area slivers from the tessellation so the mesh is watertight
            import trimesh
            m = trimesh.load(path)
            m.update_faces(m.nondegenerate_faces(height=1e-4))
            m.merge_vertices(digits_vertex=4)
            m.remove_unreferenced_vertices()
            m.export(path)
        except ImportError:
            pass
        bb = part.val().BoundingBox()
        print(f"{name}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, "
              f"vol {part.val().Volume() / 1000:.1f} cm3, valid={part.val().isValid()}")

    # assembled (desk pose) STEP for checking fit in CAD
    asm = cq.Assembly()
    asm.add(to_world(bezel), name="front_bezel", color=cq.Color(0.15, 0.15, 0.17))
    asm.add(wedge, name="rear_wedge", color=cq.Color(0.95, 0.75, 0.1))
    asm.save(os.path.join(OUT, "CYD2USB_wedge_assembly.step"))
