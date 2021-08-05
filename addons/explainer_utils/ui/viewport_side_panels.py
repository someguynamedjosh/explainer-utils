import bpy
from bpy.types import Panel
from explainer_utils import bootstrap_utils


class OBJECT_PT_explainer_settings(Panel):
    bl_idname = "OBJECT_PT_explainer_settings"
    bl_label = "Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ExUtil"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "ignore_group_with_children")
        layout.prop(context.scene, "hide_transparent")
        layout.prop(context.scene, "visibility_range")

# class OBJECT_PT_latex(bpy.types.Panel):
#     bl_idname = "OBJECT_PT_explainer_latex"
#     bl_label = "LaTeX"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "ExUtil"
#     bl_context = "objectmode"

#     def draw(self, context):
#         layout = self.layout
#         scene = context.scene
#         latex2blender_tool = scene.explainer_latex_settings

#         layout.prop(latex2blender_tool, "source_type", text="Source")
#         if latex2blender_tool.source_type == "inline":
#             layout.prop(latex2blender_tool, "inline_source", text="")
#         else:
#             layout.prop(latex2blender_tool, "resource_source", text="")
#         layout.prop(latex2blender_tool, "material")
#         layout.prop(latex2blender_tool, "scale")
#         layout.operator(AddLatex.bl_idname, icon="ADD")


def register():
    bpy.utils.register_class(OBJECT_PT_explainer_settings)
    # bpy.utils.register_class(OBJECT_PT_latex)


def unregister():
    bpy.utils.unregister_class(OBJECT_PT_explainer_settings)
    # bpy.utils.unregister_class(OBJECT_PT_latex)


bootstrap_utils.register_listeners.append(register)
bootstrap_utils.unregister_listeners.append(unregister)
