# Rugged 45° desk wedge for the ESP32-2432S028R (dual-USB / CYD2USB)

![preview](preview.png)

Two-part enclosure. The screen sits in landscape at 45°. There are no thin stands, clips or tabs that can snap off. Both parts print in PLA with **no supports**.

| File | What it is | Print orientation |
|---|---|---|
| `CYD2USB_wedge_front_bezel_heatset.stl` | Front bezel, for M3 heat-set inserts (recommended) | As exported: face down |
| `CYD2USB_wedge_front_bezel_selftap.stl` | Same bezel with 2.6 mm pilot holes, for screwing straight into PLA | As exported: face down |
| `CYD2USB_wedge_rear_wedge.stl` | Rear wedge / stand | As exported: on its flat base |
| `CYD2USB_wedge_fit_test_usb_end.stl` | 15 × 58 mm slice of the bezel's USB end, for checking the ports | Face down |
| `CYD2USB_wedge_assembly.step` | Assembled model, for checking or modifying in CAD | — |
| `cyd_wedge_case.py` | Parametric CadQuery source that generates everything above | — |

Outside size: **96 W × 76 D × 51 H mm**, about 130 g with the board.

## Hardware

- 4 × **M3 × 16 socket-head screws** (ISO 4762 / DIN 912). M3 × 14 also works. **Don't use anything longer than 16 mm**, or the screw will push through the bezel face.
- 4 × **M3 heat-set inserts**, 4 mm or 5.7 mm long, OD 4.5–5 mm (hole is 4.1 mm). You don't need these if you print the self-tap bezel.
- 4 × **stick-on rubber bumper feet, Ø10 mm**. Don't skip them: on bare PLA the wedge slides when you tap the screen (≈80 gf), and with rubber feet it takes ≈750 gf.

## Print settings (PLA)

| Setting | Value | Why |
|---|---|---|
| Layer height | 0.2 mm | |
| Walls / perimeters | **6** (≥ 2.4 mm) | The bezel's 3.5 mm walls come out effectively solid |
| Top / bottom layers | 6 / 6 | |
| Infill (wedge) | **35 % gyroid** | Tough core that absorbs energy; the wedge is ~55–65 g |
| Nozzle temp | Upper end of your PLA's range (≈215–220 °C) | Better layer bonding = better drop strength |
| Part cooling fan | 50–70 % | Same reason |
| Supports | **None** | Every overhang is ≤ 45° or a short bridge |

PLA+, "Tough PLA", PETG or ASA all print from the same files and handle impacts much better than standard PLA. Use one of them if you can.

## Fit-check first (15 minutes)

There is no published drawing that gives the USB-C and micro-USB positions on the dual-USB board. To cover the likely layouts, the USB end of the bezel has one long rounded slot: 26.8 mm along the edge × 8.5 mm. Before printing the full case:

1. Print `CYD2USB_wedge_fit_test_usb_end.stl`.
2. Set the USB end of the board into it, screen side down. The two holes should line up with the two bosses.
3. Plug in both cables. They should go in fully without the plug body hitting the slot edges.

If they don't fit, change `USB_Y0`, `USB_Y1`, `USB_Z0` and `USB_Z1` at the top of `cyd_wedge_case.py` and rerun it. You need `pip install cadquery trimesh`, then `python3 cyd_wedge_case.py`.

## Assembly

1. **Inserts:** press the 4 heat-set inserts into the bezel bosses with a soldering iron (~220 °C) until they're flush with the boss face. Skip this for the self-tap bezel.
2. **Board:** lay the bezel face down. Drop the CYD in screen first: the **USB end goes to the slot end**, and the microSD slot faces the wall with the fingernail pocket. The light sensor (LDR) sits under the small rectangular window and its light baffle.
3. **Wedge:** lower the wedge onto the back of the board. The thin ridge slides inside the bezel walls, and the 4 posts land on the PCB mounting holes.
4. **Screws:** put two screws in from **underneath** and two from the **vertical back face**. Each goes through its post and the PCB hole into an insert. Tighten until snug and stop. The PCB is clamped between the posts and the bezel bosses, so over-tightening only stresses the board.
5. **Feet:** stick the rubber feet into the 4 shallow recesses on the base.

On the desk, the USB ports are on the **left** and the microSD card is reached from the **top-back** edge. If your UI comes out upside down, swap `setRotation(1)` ↔ `setRotation(3)`.

## Drop-resistance features

- **Raised bezel:** the face sits 3.5 mm proud of the glass, so a flat face-down landing hits plastic, not the screen. The 1 mm air gap means the bezel never presses the resistive touch panel, which avoids phantom touches.
- **PCB clamped at all 4 holes**, between bezel bosses and posts on the wedge. In a fall, the board's mass goes straight into the case instead of hanging on the screws.
- **Interlocking ridge** between the two parts. Side impacts are carried by the plastic, not by the screws.
- **Screws loaded in the safe direction:** the heads sit inside the wedge and thread into brass inserts.
- **Thick walls:** 3.5 mm everywhere, 5.2 mm rounded corners, a chamfered face edge and a mostly solid wedge core.
- **Recessed openings:** the screw heads, USB slot and microSD slot are all set back, and there are no projecting tabs or kickstand legs.
- **Hard to knock over:** the wedge only tips when the top edge of the screen is pressed with ≈1 kgf.

## Honest limits

- **Not drop-tested yet.** 5 m onto concrete is well beyond what most commercial rugged handhelds are rated for (typically 1.2–2 m). The case is designed to survive it, but **the LCD glass is the weakest part**: a hard corner impact can crack it from shock alone, however strong the case. Try a few drops with the empty case first, ideally with a ~50 g weight inside.
- **Standard PLA turns brittle in the cold and softens above ~55 °C,** for example in a car in summer.
- **Not reachable once assembled:**
  - the BOOT / RESET buttons. They aren't needed for normal USB flashing because the CYD auto-resets; unplug USB to power-cycle.
  - the side JST connectors (P1 serial/power, P3, CN1, speaker).
  - the back RGB LED. If you need any of these, a variant with a cable exit is easy to add in the script.

## Design data used

- PCB 86 × 50 mm, M3 holes 4 mm from each edge (78 × 42 mm pitch), from the manufacturer's ESP32-2432S028R spec.
- LCD 69.2 × 50 × 2.3 mm with a 60.9 × 46.2 mm viewing area, from the JC2432A028N datasheet. The window is offset 2.6 mm away from the USB end; the window and LDR positions were cross-checked against an existing USB-C CYD case known to fit.
- Component heights on the back are ≤ 4.7 mm; the cavity behind the PCB is 7.5 mm deep.
