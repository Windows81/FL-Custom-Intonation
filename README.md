I've created a Patcher preset that allows music producers to use their own intonation schemes without having to pitch-shift each individual note. The default setting is tuned to C-Major Just with a Styrus set likewise to the default preset.

## Setup

Download and place `CustomIntonation.fst` in the directory shown below to allow custom intonation in FL Studio (for Windows users). Replace Sytrus with your own stock plugins; VSTs do not work correctly under this setup. Fruity plugins that use a dedicated audio-sample tab are not supported by Patcher. Also make sure the final VFX envelope and 'To FL Studio' are both linked. Pitch-correction knobs can each go up to 100 cents in both direction, whereas the global pitch-shift knob goes ±1200 cents.

```console
%userprofile%\Documents\Image-Line\FL Studio\Presets\Plugin presets\Generators\Patcher
```

## Add your own presets!

If you have Python 3.X installed, use the supplied `add_scale.py` script to generate a compatible pitch profile from the contents of a `.scl` file. Use the `--fst` flag to add that new profile to the preset list; for that option to work properly, the `_template.fst` file must also be in the same directory.
