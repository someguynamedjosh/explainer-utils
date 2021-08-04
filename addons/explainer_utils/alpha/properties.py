from bpy.props import FloatProperty
from bpy.types import Context, Object, UILayout
from explainer_utils import bootstrap_utils


def layout_properties(layout: UILayout, context: Context):
    row = layout.row()
    row.use_property_decorate = True
    row.use_property_split = True
    row.prop(context.object, "alpha", slider=True)

    row = layout.row()
    row.use_property_decorate = True
    row.use_property_split = True
    row.prop(context.object, "composite_alpha", slider=True)


bootstrap_utils.object_panel_layouts.append((500, layout_properties))


def register_properties():
    Object.alpha = FloatProperty(
        name="Alpha",
        description="Transparency of the object.\nUse composite alpha instead "
        + "of this when making materials.\nDoes nothing without an "
        + "appropriate material.\nWhen interaction helpers are enabled, "
        + "transparent objects will be hidden",
        default=1.0,
        min=0.0,
        max=1.0,
        soft_min=0.0,
        soft_max=1.0,
        precision=2,
        options={'ANIMATABLE', 'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'}
    )
    Object.composite_alpha = FloatProperty(
        name="Composite Alpha",
        description="This object's alpha, multiplied with the alpha of all "
        + "its parents.\nUse this in shaders by adding an attribute node "
        + "with the name set to `composite_alpha`",
        default=1.0,
        min=0.0,
        max=1.0,
        soft_min=0.0,
        soft_max=1.0,
        precision=2,
        options=set(),
        override=set()
    )


bootstrap_utils.register_listeners.append(register_properties)


def unregister_properties():
    Object.alpha = None
    Object.composite_alpha = None


bootstrap_utils.unregister_listeners.append(unregister_properties)
