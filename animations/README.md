# Pip movement library

Built in Blender 5.1.2 from the approved fresh bean model. The retired model and rig are not used.

## Open and play

Open **Pip-movements.blend**. Choose a movement from Blender's **Scene** dropdown at the top right, then press Space. The project opens on Stretch. A text block named **Pip movement guide** is also included in the file.

| Scene | Frames | Duration | Performance |
| --- | --- | --- | --- |
| Idle | 1–180 | 6 s | Restrained breathing and soft blinks |
| Stretch | 1–300 | 10 s | Neutral, waist preparation, elbows up, reach overhead, hands together, side bend, release and settle |
| Breathe | 1–240 | 8 s | Hands near the belly, slow inhale, exhale and release |
| Wave | 1–120 | 4 s | One-arm greeting with a small forearm wave |
| Celebrate | 1–90 | 3 s | Gentle two-arm cheer |
| Walk-off | 1–165 | 5.5 s | Starts stepping while turning, then walks out to the right |
| Walk-back | 1–165 | 5.5 s | Walks in from the right and settles facing forward |

The first five scenes loop. The walking clips are transitions. A boundary key at end frame +1 matches the opening pose for looped movements; export only through the scene's end frame.

## Review and exports

- **Pip-movements-preview.mp4** shows all seven movements, labelled, at normal speed.
- **Pip-stretch-two-loops.mp4** shows two uninterrupted stretch loops for checking the seam.
- Each movement folder contains a standalone editable **Pip.blend**, its own H.264 MP4 and an **alpha/** sequence of 600 × 720 RGBA PNGs at 30 fps.
- Review videos composite the transparent character over warm ivory. The transparent renders omit the studio floor.
- Original neutral model and renders remain in `../model/` and `../renders/`.

## Controls and editing

**CTRL • placement** moves and turns the whole character. **CTRL • body lean and stretch** controls the body and attached facial features. Shoulder, elbow and wrist controls drive the arm curves, including their smooth handles. Hip, knee and ankle controls drive the leg curves. Mitten and foot objects have keyed position and rotation. **CTRL • eyes and expression** has a keyed `blink` property; the oval eyes flatten while closed-eye curves appear.

The solid viewport uses material colours. Enable **Viewport Overlays → Extras** to show the control empties if you want to edit their positions.

Motion is baked to editable control keys at 30 fps with linear interpolation between the dense keys. There are no external playback handlers. Materials are procedural; no external textures are needed. Each scene has independent objects and action data, so editing one performance does not change another. Timeline markers identify the principal poses.

The source scripts are `../animate_pip.py`, `../render_motions.py`, `../assemble_motions.py` and `../encode_motions.py`.

## Reference and limits

Stretch follows the eight poses in `../references/stretch-pose-reference.png`. The sheet provides the key poses; timing and transitions are newly authored. The shoulders rise and the arms lengthen during the overhead reach to match the stylised proportions. These are flexible curve limbs rather than anatomically fixed-length human arms. The body uses modest whole-body lean and scale; it retains the approved underlying mesh. The hands are simple mittens.

Automated checks cover loop transforms, driver validity and sampled arm centerline penetration. Visual checks cover the principal poses, normal-speed playback, the loop boundary, walk contacts and transparent edges. `validation.json` contains the geometric check results; it is not a guarantee of every surface contact.
