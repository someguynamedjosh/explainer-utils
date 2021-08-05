import bpy
from bpy.types import Menu, Operator

from explainer_utils import bootstrap_utils
from explainer_utils.fade.operator import FadeOperator

LONG_DURATION = 89
MED_DURATION = 50
SHORT_DURATION = 23


class VIEW3D_MT_PIE_fades(Menu):
    bl_label = 'Preset Fades'

    def draw(self, context):
        l = self.layout
        p = l.menu_pie()

        # Go home layout engine, you're drunk.

        p.separator()
        p.separator()

        o = p.operator(FadeOperator.bl_idname, text="Med Fade Out",
                       icon="TRACKING_CLEAR_BACKWARDS")
        o.mode, o.duration = "fade_out", MED_DURATION
        o = p.operator(FadeOperator.bl_idname,
                       text="Med Fade In", icon="TRACKING_FORWARDS")
        o.mode, o.duration = "fade_in", MED_DURATION
        o = p.operator(FadeOperator.bl_idname,
                       text="Short Fade In", icon="TRACKING_FORWARDS")
        o.mode, o.duration = "fade_in", SHORT_DURATION

        o = p.operator(FadeOperator.bl_idname,
                       text="Long Fade In", icon="TRACKING_FORWARDS")
        o.mode, o.duration = "fade_in", LONG_DURATION
        o = p.operator(FadeOperator.bl_idname,
                       text="Short Fade Out", icon="TRACKING_CLEAR_BACKWARDS")
        o.mode, o.duration = "fade_out", SHORT_DURATION
        o = p.operator(FadeOperator.bl_idname, text="Long Fade Out",
                       icon="TRACKING_CLEAR_BACKWARDS")
        o.mode, o.duration = "fade_out", LONG_DURATION


class OpenFadePresets(Operator):
    """Apply a preset fade to selected objects"""
    bl_idname = "object.explainer_fade_presets"
    bl_label = "Apply Preset Fade"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_PIE_fades")
        return {'FINISHED'}


keymap = None
keymap_item = None


def register():
    global keymap, keymap_item
    bpy.utils.register_class(VIEW3D_MT_PIE_fades)
    bpy.utils.register_class(OpenFadePresets)

    keyconfigs = bpy.context.window_manager.keyconfigs
    keymap = keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    keymap_item = keymap.keymap_items.new(OpenFadePresets.bl_idname, 'F', 'PRESS')


def unregister():
    global keymap, keymap_item
    bpy.utils.unregister_class(VIEW3D_MT_PIE_fades)
    bpy.utils.unregister_class(OpenFadePresets)

    keymap.keymap_items.remove(keymap_item)
    keyconfigs = bpy.context.window_manager.keyconfigs
    keyconfigs.remove(keymap)


bootstrap_utils.register_listeners.append(register)
bootstrap_utils.unregister_listeners.append(unregister)
