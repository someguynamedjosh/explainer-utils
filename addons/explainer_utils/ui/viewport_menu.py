from bpy.types import Menu, VIEW3D_MT_object
from bpy.utils import register_class, unregister_class

from explainer_utils import bootstrap_utils
from explainer_utils.exclude_from_render import ExcludeFromRender
from explainer_utils.fade.operator import FadeOperator
from explainer_utils.fade.presets import OpenFadePresets
from explainer_utils.latex import AddLatex
from explainer_utils.lazy_parent import LazyParent
from explainer_utils.ui.main_pie import OpenExplainerUtils


class ExplainerMenu(Menu):
    bl_idname = "VIEW3D_MT_explainer_utils"
    bl_label = "Explainer Utils"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        layout.operator(OpenExplainerUtils.bl_idname)
        layout.separator()
        layout.operator(FadeOperator.bl_idname)
        layout.operator(OpenFadePresets.bl_idname)
        layout.separator()
        layout.operator(AddLatex.bl_idname)
        layout.operator(ExcludeFromRender.bl_idname)
        layout.operator(LazyParent.bl_idname)


def draw_menu(self, context):
    self.layout.menu(ExplainerMenu.bl_idname)
    self.layout.separator()


def register():
    register_class(ExplainerMenu)
    VIEW3D_MT_object.prepend(draw_menu)


def unregister():
    unregister_class(ExplainerMenu)
    VIEW3D_MT_object.remove(draw_menu)


bootstrap_utils.register_listeners.append(register)
bootstrap_utils.unregister_listeners.append(unregister)
