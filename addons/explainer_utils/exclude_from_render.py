from bpy.types import Operator
from bpy.utils import register_class, unregister_class
from explainer_utils import bootstrap_utils


class ExcludeFromRender(Operator):
    """Thoroughly prevents all selected objects from showing up 
    in any render, also sets the viewport display to wireframe"""
    bl_idname = "object.exclude_from_render"
    bl_label = "Exclude From Render"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for o in context.selected_objects:
            o.hide_render = True
            o.display_type = 'WIRE'
            for key in ['camera', 'diffuse', 'glossy', 'transmission', 'scatter', 'shadow']:
                setattr(o.cycles_visibility, key, False)
                print(key, getattr(o.cycles_visibility, key))
        return {'FINISHED'}


def register():
    register_class(ExcludeFromRender)


def unregister():
    unregister_class(ExcludeFromRender)


bootstrap_utils.register_listeners.append(register)
bootstrap_utils.unregister_listeners.append(unregister)
