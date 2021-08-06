import bpy
from bpy.props import StringProperty
from bpy.types import Collection, Context, Event, Object, Operator, Scene, UIPopupMenu
from bpy.utils import register_class, unregister_class
from explainer_utils import bootstrap_utils


def instantiate(context: Context, root: Object, objects: list[Object], into: Collection):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        into.objects.link(obj)
        obj.select_set(True)
    bpy.ops.object.duplicate(linked=True, mode='INIT')
    new_objects = list(context.selected_objects)
    for obj in new_objects:
        if obj.parent == root.parent:
            obj.parent = None
        if not obj.instantiate_linked:
            obj.data = obj.data.copy()
        obj.update_tag()
    for obj in objects:
        into.objects.unlink(obj)


class OT_Instantiate(Operator):
    bl_idname = "object.instantiate"
    bl_label = "Instantiate"
    bl_options = {'UNDO'}

    object_to_instantiate: StringProperty()

    def execute(self, context: Context):
        obj = context.blend_data.objects[self.object_to_instantiate]
        everything = [obj]
        unexplored = [obj]
        while len(unexplored) > 0:
            nex = unexplored.pop()
            everything += nex.children
            unexplored += nex.children
        instantiate(context, obj, everything, context.collection)
        return {'FINISHED'}


class OT_InstantiateMenu(Operator):
    bl_description = "Instantiates a hierarchy of objects from a preset storage scene"
    bl_idname = "object.instantiate_menu"
    bl_label = "Instantiate"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: Context):
        return not context.scene.is_instantiation_source

    def invoke(self, context: Context, event: Event):
        wm = context.window_manager
        wm.popup_menu(test_menu)
        return {'CANCELLED'}


COL_SEP = '|  '
PARENT_SEP = '>'


def look_for_grouped_children(seps: str, this: UIPopupMenu, obj: Object):
    if obj.group_with_children:
        add_object_entries(seps, this, obj)
    else:
        for child in obj.children:
            look_for_grouped_children(seps, this, obj)


def add_object_entries(seps: str, this: UIPopupMenu, object: Object):
    op = this.layout.operator(
        OT_Instantiate.bl_idname,
        text=seps + object.name,
        icon='OBJECT_DATA'
    )
    op.object_to_instantiate = object.name_full
    for child in object.children:
        look_for_grouped_children(seps + PARENT_SEP, this, child)


def add_collection_entries(seps: str, this: UIPopupMenu, collection: Collection):
    this.layout.label(text=seps + collection.name,
                      icon='OUTLINER_COLLECTION')
    new_seps = seps + COL_SEP
    for object in collection.objects:
        if object.parent is not None:
            continue
        add_object_entries(new_seps, this, object)
    for child in collection.children:
        add_collection_entries(new_seps, this, child)


def test_menu(this: UIPopupMenu, context: Context):
    layout = this.layout
    for collection in context.scene.instantiation_source.collection.children:
        add_collection_entries('', this, collection)


def register():
    register_class(OT_Instantiate)
    register_class(OT_InstantiateMenu)


def unregister():
    unregister_class(OT_Instantiate)
    unregister_class(OT_InstantiateMenu)


bootstrap_utils.register_listeners.append(register)
bootstrap_utils.unregister_listeners.append(unregister)
