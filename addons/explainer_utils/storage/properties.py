from bpy.props import BoolProperty, PointerProperty
from bpy.types import Context, Object, Scene, UILayout
from explainer_utils import bootstrap_utils


def layout_properties(layout: UILayout, context: Context):
    if context.scene.is_instantiation_source:
        row = layout.row()
        row.use_property_decorate = True
        row.use_property_split = True
        row.prop(context.object, "instantiate_linked")


bootstrap_utils.object_panel_layouts.append((50, layout_properties))


chill = False


def on_set_instantiation_source(scene: Scene, context: Context):
    global chill
    new_value = scene.instantiation_source
    if chill:
        return
    chill = True
    for scene in context.blend_data.scenes:
        scene.instantiation_source = new_value
        scene.is_instantiation_source = scene == new_value
    chill = False


def register_properties():
    Scene.is_instantiation_source = BoolProperty(
        name="Is Instantiation Source?",
        description="True if this scene is the instantiation source "
        + "for the entire file",
        default=False,
        options=set()
    )
    Scene.instantiation_source = PointerProperty(
        type=Scene,
        name="Instantiation Source",
        description="The scene objects will be instantiated from",
        options=set(),
        update=on_set_instantiation_source
    )
    Object.instantiate_linked = BoolProperty(
        name="Instantiate Linked",
        description="When checked, instantiating this object will cause "
        + "the instantiated object to share the same datablock as this "
        + "object (e.g. it will have the same mesh/curve/text datablock), "
        + "equivalent to cloning this object with Alt+D. Uncheck to use "
        + "the behavior of Shift+D instead",
        default=True,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'}
    )


bootstrap_utils.register_listeners.append(register_properties)


def unregister_properties():
    Scene.is_instantiation_source = None
    Scene.instantiation_source = None
    Object.instantiate_linked = None


bootstrap_utils.unregister_listeners.append(unregister_properties)
