# Blender and animation tools

These scripts locate the repository root from their own paths, so asset locations do not depend on your working directory. Authoring and rendering scripts overwrite assets; work on a branch.

## Tool index

| Task | Scripts |
| --- | --- |
| Neutral character | `build_pip.py`, `verify_model.py` |
| Standing/walking authoring | `animate_pip.py`, `assemble_motions.py`, `polish_viewports.py` |
| Seated authoring | `animate_seated.py`, `assemble_seated.py` |
| Rendering | `render_motions.py` |
| Video encoding | `encode_motions.py`, `encode_seated.py` |
| Geometry and loops | `validate_motions.py`, `validate_seated.py`, `check_contacts.py` |
| Combined scene isolation | `verify_master.py`, `verify_seated_master.py` |
| Export integrity | `verify_exports.py`, `verify_seated_exports.py` |
| Step inspection | `inspect_steps.py` |

## Example commands

From the repository root, using Blender 5.1.2 on macOS:

```sh
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender

# Check both combined scene libraries without regenerating them.
"$BLENDER" --background --python tools/blender/verify_master.py
"$BLENDER" --background --python tools/blender/verify_seated_master.py

# Render the complete transparent standing stretch sequence (Cycles/Metal).
"$BLENDER" --background --python tools/blender/render_motions.py -- --clips Stretch

# Render all seated movements.
"$BLENDER" --background --python tools/blender/render_motions.py -- \
  --library seated --clips Side-reaches,Gentle-turns,Shoulder-rolls,Seated-breathe
```

The renderer also accepts `--review` for selected poses and `--range START:END` for a subset. It skips existing frame files unless `--overwrite` is supplied. Its GPU configuration currently targets Metal; see the [character guide](../../docs/CHARACTERS.md) before using another platform.

The ordinary Python encoding/export tools require Pillow and FFmpeg (`ffmpeg` and `ffprobe` on PATH). The encoders wait for all expected frames; complete the render first. They currently use the macOS Arial font for video labels.

```sh
python3 tools/blender/verify_exports.py
python3 tools/blender/verify_seated_exports.py
```

Export verification reads all frames/videos and updates the corresponding validation JSON report. Geometry validation can take longer because it steps through every frame.
