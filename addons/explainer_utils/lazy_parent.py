from bpy.types import Context, UILayout, Operator, Object, VIEW3D_MT_object_parent
from bpy.utils import register_class, unregister_class
from explainer_utils import bootstrap_utils


class LazyParent(Operator):
    """
    Sets the parent of the selected objects to the active object, 
    but only when the object is not the child of another selected
    object.
    """
    bl_idname = "object.lazy_parent"
    bl_label = "Lazy Parent"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: Context):
        old_igwc = context.scene.ignore_group_with_children
        context.scene.ignore_group_with_children = True

        new_parent: Object = context.active_object
        selected_objects_copy = list(context.selected_objects)
        for obj in selected_objects_copy:
            obj.select_set(False)
        new_parent.select_set(True)

        for obj in selected_objects_copy:
            if obj is new_parent:
                continue
            allow_changing_parent = True
            old_parent: Object = obj.parent
            while old_parent is not None:
                if old_parent.select_get() and old_parent is not new_parent:
                    allow_changing_parent = False
                    break
                old_parent = old_parent.parent
            if allow_changing_parent:
                obj.select_set(True)

        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        for obj in selected_objects_copy:
            obj.select_set(True)
        context.scene.ignore_group_with_children = False
        return {'FINISHED'}


def menu_entry(this: VIEW3D_MT_object_parent, context: Context):
    this.layout.operator(LazyParent.bl_idname)


def register():
    register_class(LazyParent)
    VIEW3D_MT_object_parent.append(menu_entry)


def unregister():
    unregister_class(LazyParent)
    VIEW3D_MT_object_parent.remove(menu_entry)


bootstrap_utils.register_listeners.append(register)
bootstrap_utils.unregister_listeners.append(unregister)
