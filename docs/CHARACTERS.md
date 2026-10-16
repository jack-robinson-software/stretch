# Pip and the character workflow

Pip is Stretch’s first companion: a warm terracotta bean, with thin cocoa limbs, mitten hands and a small expressive face. The editable sources and complete exports are included so contributors can understand both the character and the animation pipeline.

## Open the assets

- [`model/Pip.blend`](../model/Pip.blend): neutral character, procedural materials, studio and camera.
- [`animations/Pip-movements.blend`](../animations/Pip-movements.blend): seven independent standing and walking scenes. [Movement guide](../animations/README.md).
- [`seated/Pip-seated-movements.blend`](../seated/Pip-seated-movements.blend): four chair-based loops. [Seated guide](../seated/README.md).

Choose a scene in Blender and press Space. Materials are procedural; external textures and playback scripts are not needed. Enable **Viewport Overlays → Extras** to see the control empties.

Pip’s bean body uses a subdivided quad mesh and shallow clay displacement. The face sits on its surface. Arms and legs are editable Bezier curves driven by authored controls; mittens and feet are separate meshes. Motion is densely keyed at 30 fps. Looping scenes include a boundary key at the next frame; export only through the listed end frame.

## Source tools

The pipeline was authored with **Blender 5.1.2** on an Apple Silicon Mac. Rendering currently selects Cycles/Metal; adapting it to other GPUs is separate work. Open/playback of saved scenes does not require Metal.

Run Blender commands from the repository root. For example, to verify the neutral model without changing it:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background model/Pip.blend \
  --python tools/blender/verify_model.py
```

To regenerate the neutral model and studio renders:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background \
  --python tools/blender/build_pip.py
```

**Generation scripts overwrite their output assets.** Use a branch and keep the original files available when experimenting. See the [tool index](../tools/blender/README.md) for authoring, rendering and validation commands.

To regenerate packaged app or browser assets, use a virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r mac-app/requirements.txt
python3 mac-app/package_assets.py
python3 mac-app/make_web_assets.py
```

These packaging scripts skip existing outputs. Remove only the corresponding generated output when deliberately replacing a clip, then rebuild. The app uses ten clips; Walk-back is included in the source library but is not currently played by the app.

## New companions

New characters are welcome. Start with an issue describing the personality, appearance and movement ideas before producing a large asset set. Include editable sources and assets you have permission to license under MIT. Preserve both seated and standing options, smooth loop boundaries, clear silhouettes and comfortable movement pacing.

A picker and shared character asset format are planned; naming a profile in code alone does not yet load a new library.
