# Stretch — a little pause

A small Mac app with a growing cast of companions. **Pip** is the first character: a warm, orange bean who appears at the top right of the screen with a gentle invitation to pause, stretch or breathe. Includes the native app prototype, the approved bean-shaped character, editable Blender files, standing and seated animation libraries, transparent renders, and an interactive browser preview.

## Try the app

On an Apple Silicon Mac with macOS 13+ and Apple Command Line Tools:

```sh
cd mac-app
./build.sh
./Stretch.app/Contents/MacOS/Stretch --self-test
open Stretch.app
```

Automatic nudges start off. Use the menu-bar icon to try a seated or standing pause, snooze, or open Settings. See [the app README](mac-app/README.md) for controls and prototype scope.

For the interactive browser demo, open `mac-app/preview.html`. All animation assets are included. To regenerate resized app or browser assets, install Pillow with `python3 -m pip install -r mac-app/requirements.txt`, then run `mac-app/package_assets.py` or `mac-app/make_web_assets.py`.

## App and characters

**Stretch** is the product. **Pip** is one of its characters. Product identity and character metadata are separate in the native app; the prototype currently includes Pip only. His Blender files and animation exports keep their character-specific names.

## Project layout

- `mac-app/`: native AppKit application, transparent playback assets and browser preview.
- `model/`: editable approved neutral character.
- `animations/`: seven standing and walking movements, Blender scenes, MP4s and transparent PNG sequences.
- `seated/`: four chair-based movements, Blender scenes, MP4s and transparent PNG sequences.
- `references/` and `renders/`: character references and approved neutral renders.
- Root Python scripts: model generation, animation authoring, rendering and validation.

The project contains the complete approved asset library; generated caches, build logs, Blender backups and local app executables/signatures are excluded from version control.

## Review files

- `model/Pip.blend` — editable neutral model with studio camera and lighting.
- `renders/Pip-neutral.png` — neutral three-quarter preview.
- `renders/Pip-front.png` and `renders/Pip-side.png` — proportion and silhouette checks.
- `renders/Pip-neutral-alpha.png` — transparent version of the neutral preview.

The body is an elongated bean with rounded ends, a restrained belly and a broad gentle bend through the waist. It is a smooth quad mesh with subdivision and shallow clay displacement. Arms and legs are editable Bezier curves. Hands and feet are separate meshes. The body, face and limbs are grouped under `Pip • placement` for moving the whole character. Materials are procedural, so the model has no external texture dependencies.

The neutral design is approved. The movement library is in `animations/Pip-movements.blend`; see `animations/README.md` for the seven scenes, controls and exports. The neutral file in `model/` remains the approved modelling baseline.

## Rebuild

Run Blender in background mode with `--python build_pip.py` from this directory. This regenerates the model and the four renders. The script currently selects Metal for rendering on this Mac.

Primary identity reference: `references/pip-character-sheet.png`. Additional pose reference: `references/stretch-pose-reference.png`.

## Seated movements

`seated/Pip-seated-movements.blend` contains four chair-based loops: side reaches, gentle turns, shoulder rolls and seated breathing. `seated/Pip-seated-preview.mp4` shows them together. See `seated/README.md` for scene controls, individual clips and transparent exports.
