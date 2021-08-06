
# Installing The Addon
- In the top bar, select `Edit` > `Preferences`
- On the left of the new window, select `Add-ons`
- On the top right, select `Install...`
- Navigate to and select `ExplainerUtils.zip`
- A single item `All: Explainer Utils` will now be displayed
- Check the checkbox
- Installation complete!

# Installing The Template (Optional, But Recommended)
The `ExplainerTemplate.zip` contains an "application template", which can
be used as a starting point for a new file. It contains editors and scenes
layed out in a way that works well with the addon. Installation goes as
follows:
- In the top bar, select the Blender icon (all the way on the left)
- Select `Install Application Template...`
- Navigate to and select `ExplainerTemplate.zip`
- Installation complete!
  - You can now access the template either by pressing `ctrl+N` or by 
    selecting it from the splash screen.

# Installing The Midnight Theme (Optional)
Because "Blender dark" isn't dark enough!
- In the top bar, select `Edit` > `Preferences`
- On the left of the new window, select `Themes`
- On the top right, select `Install...`
- Navigate to and select `Midnight.xml`
- Installation complete!
I love how this instantly makes Blender look way more expensive.

# Some Useful Preferences
These settings are optional and don't have anything to do with the addon, I
just find them helpful:

- `Keymap` > `Preferences` > `Pie Menu on Drag`
  - Holding `tab` and dragging now lets you instantly access all modes.
  - Pressing `z` quickly toggles between wire and normal, while holding
    it shows the usual pie.
- `Keymap` > `Preferences` > `Extra Shading Pie Menu Items`
  - `z` now lets you quickly toggle overlays (this used to be a feature
    in the addon before I discovered this setting!)
- Set `System` > `Memory & Limits` > `Undo Steps` to its max
  - it doesn't really slow anything down and is a lifesaver when you 
    realize you need to go 255 steps back.
- Set `Save & Load` > `Blend Files` > `Save Versions` to zero
  - Disables `.blend1` files which I always find useless because it's just
    a version of my file but missing the last 30 seconds of changes. If you
    want to keep some version around, copy it manually!
- Mapping `ctrl+space` to open the `search menu` (instead of f3, which is
  particularly cumbersome on my keyboard)
- If working with python scripts: 
  - enable `interface` > `display` > `developer extras`
  - enable `interface` > `display` > `python tooltips`


# Some Useful Plugins
Same deal as above
- Included with Blender:
  - Development: Icon Viewer
  - Import Images as Planes
  - Node: Node Wrangler
