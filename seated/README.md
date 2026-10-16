# Pip — seated movement set

Four seated companion loops built around Pip, with a padded sage chair, bent knees and planted feet.

Open **Pip-seated-movements.blend**, choose a movement from Blender's Scene dropdown and press Space. Each scene has its own editable controls and actions. The standing movement project remains in `../animations/`.

| Movement | Frames at 30 fps | Duration | Beats |
| --- | --- | --- | --- |
| Side reaches | 1–300 | 10 s | One hand on the knee, opposite arm overhead, small side bend; return and swap sides |
| Gentle turns | 1–240 | 8 s | Hands on lap, torso turns one way, centre, other way, centre |
| Shoulder rolls | 1–180 | 6 s | Two small, slow shoulder circles and a relaxed release |
| Seated breathe | 1–240 | 8 s | Hands settle at the belly, inhale, exhale, hands return to lap |

**Pip-seated-preview.mp4** shows all four at normal speed. **Pip-seated-side-reaches-two-loops.mp4** repeats the reach loop for checking the seam. Each movement folder also contains its own `Pip.blend`, H.264 MP4 and `alpha/` sequence of 600 × 720 RGBA PNGs. The review videos use a warm ivory background; the transparent assets include the chair.

**Pip-seated-neutral.png** is the studio still, and **Pip-seated-neutral-alpha.png** is the reusable transparent resting pose.

## Editing

`CTRL • placement` moves Pip and the chair together. `CTRL • body lean and stretch` moves the trunk and face; the hips stay near the cushion. Shoulder, elbow and wrist controls drive the smooth arm curves. Hip, knee and ankle controls drive the bent legs. Feet are fixed throughout all four clips. Mitten objects have their own keyed transforms. `CTRL • eyes and expression` has a keyed `blink` property.

Enable **Viewport Overlays → Extras** to see the control empties. Keys are densely baked at 30 fps. End frame +1 is the boundary key; render only through the listed end frame. Each scene loops back to its resting pose. There are no external playback handlers or texture dependencies. The chair is editable geometry in its own collection.

## Source and checks

Created with Blender 5.1.2. Source scripts are [`animate_seated.py`](../tools/blender/animate_seated.py), [`render_motions.py`](../tools/blender/render_motions.py), [`assemble_seated.py`](../tools/blender/assemble_seated.py) and [`encode_seated.py`](../tools/blender/encode_seated.py). The shared renderer accepts `--library seated --clips Side-reaches,Gentle-turns,Shoulder-rolls,Seated-breathe`.

The Cycles/Metal renderer on this Mac required kernel optimisation and MetalRT to be disabled. The rendering script applies those settings for its process. Normal playback of the saved Blender scenes needs no script.

Checks cover loop boundaries, fixed feet and chair, seat contact, curve drivers, sampled arm intersections, the unchanged approved body mesh and the final PNG/video exports. The arms remain flexible mascot limbs, and the body uses modest whole-body lean, turn and scale. These short loops are designed as companion reminders.
