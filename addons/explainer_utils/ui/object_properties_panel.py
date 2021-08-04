from bpy.types import Panel
from bpy.utils import register_class, unregister_class
from explainer_utils import bootstrap_utils


class ExplainerPanel(Panel):
    """Displays properties added by explainer utils"""
    bl_label = "Explainer Utils"
    bl_idname = "OBJECT_PT_explainer_utils"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout

        for (priority, sub_layout) in bootstrap_utils.object_panel_layouts:
            sub_layout(layout, context)


def register():
    register_class(ExplainerPanel)
    bootstrap_utils.object_panel_layouts.sort(key=lambda e: e[0])


def unregister():
    unregister_class(ExplainerPanel)


bootstrap_utils.register_listeners.append(register)
bootstrap_utils.unregister_listeners.append(unregister)
