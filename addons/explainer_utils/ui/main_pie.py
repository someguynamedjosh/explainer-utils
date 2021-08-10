import bpy
from bpy.types import Menu, Operator
from bpy.utils import register_class, unregister_class
from explainer_utils import bootstrap_utils
from explainer_utils.exclude_from_render import ExcludeFromRender
from explainer_utils.latex import AddLatex
from explainer_utils.storage.instantiate import OT_InstantiateMenu


class VIEW3D_MT_PIE_explainer_utils(Menu):
    bl_label = 'Explainer Utils'

    def draw(self, context):
        l = self.layout
        p = l.menu_pie()

        # Go home layout engine, you're drunk.

        p.operator(OT_InstantiateMenu.bl_idname)
        p.operator(AddLatex.bl_idname)
        p.separator()
        p.operator(ExcludeFromRender.bl_idname)
        p.prop(context.scene, "hide_transparent")
        p.prop(context.scene, "ignore_group_with_children")


class OpenExplainerUtils(Operator):
    """Quick access to explainer util's most common operators and settings"""
    bl_idname = "object.open_explainer_utils"
    bl_label = "Explainer Utils"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_PIE_explainer_utils")
        return {'FINISHED'}


keymap = None
keymap_item = None


def register():
    global keymap, keymap_item
    register_class(VIEW3D_MT_PIE_explainer_utils)
    register_class(OpenExplainerUtils)

    keyconfigs = bpy.context.window_manager.keyconfigs
    keymap = keyconfigs.addon.keymaps.new(
        name='Object Mode', space_type='EMPTY')
    keymap_item = keymap.keymap_items.new(
        OpenExplainerUtils.bl_idname, 'E', 'PRESS')


def unregister():
    global keymap, keymap_item
    unregister_class(VIEW3D_MT_PIE_explainer_utils)
    unregister_class(OpenExplainerUtils)

    keymap.keymap_items.remove(keymap_item)

bootstrap_utils.register_listeners.append(register)
bootstrap_utils.unregister_listeners.append(unregister)
