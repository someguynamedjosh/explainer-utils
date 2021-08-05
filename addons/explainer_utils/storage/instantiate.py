import bpy
from bpy.types import Collection, Context, Object, Scene


def instantiate(context: Context, objects: list[Object], into: Collection):
    old_selection = list(context.selected_objects)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        pass
