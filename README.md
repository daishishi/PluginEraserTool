
# Plugin as Eraser Tool (PET)

PET is a plugin for Krita 5.2.0 or higher.

## What is PET?

PET is a Python Plugin. It serves as prototype for an 'Eraser Tool' into Krita.

This plugin intents to add a shortcut for *Non-Eraser* brushes, and another for *Eraser* brushes. Thus mimicking the behaviour of an dedicated Eraser Tool.
## Functionality

Krita start-up time will increase drastically the **First Time** the plugin run. That is due the process which the plugin access, analyses and categorize the brushes. Following sessions should have a normal start-up time, as long your brushes remains the same.

This plugin scan all available brushes in Krita, and creates two (2) list out of them. The first list of all *Non-Erasers* brushes (list 1) and the other of all the *Erasers* brushes (list 2).

By default this plugin has two (2) shortcuts, both activate the Free Hand Brush Tool. The first one 'remember' the last selected *Non-Eraser* brush. The second one 'remember' the last selected *Eraser* brush.

## How to


The default shortcuts are defined as:
* Brush slot -> Ctrl+Alt+Shift+P
* Eraser slot -> Ctrl+Alt+Shift+O
* Update Brush List -> Ctrl+Alt+Shift+A

The plugin should capture the current brush selected and assign it to the proper slot. This behavior was tested using the *Brush Preset Docker*, the *Brush Preset* in the Tool Bar, the *Popup Palette* and the shortcuts *Previous Favorite Preset* / *Next Favorite Preset*.

Using others plugins (Ten Brushes, BuliBrushSwitch) for changing presets weren't tested.
## Updating the Brush List

Under specific circumstances, the plugin can update the list of brushes either automatically or manually, these being:

**- Automatically**:
* The plugin is being ran for the first time
* The name or number of brushes have changed
* After installing or deactivating bundles
* Something is wrong with the Brush List save file

**- Manually**:
* Via the shortcut *Update Brush List*

**ATTENTION!**

The save file only has a reference to the preset *names*. So changing a **brush** to an **eraser** (or vice-versa), and saving it with the same name will **not update** the brush list when Krita start-up. In this case update the brush list manually.

## Download & Install

# Download

* [ZIP PET - v0.1](https://github.com/daishishi/PluginEraserTool/releases/download/v0.1.1/kritaPET-v.0.1.1.zip)

# Installation

Plugin installation in Krita is not intuitive and needs some manipulation:

1. Open Krita and go to Tools -> Scripts -> Import Python Plugins... and select the kritaPET.zip archive and let the software handle it.
2. Restart Krita
3. To enable Eraser Tool go to Settings -> Configure Krita... -> Python Plugin Manager and click the checkbox to the left of the field that says Eraser Tool.
4. Restart Krita

*Installation steps adapted from [BuliBrushSwitch](https://github.com/Grum999/BuliBrushSwitch)*
