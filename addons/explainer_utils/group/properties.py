from bpy.props import BoolProperty
from bpy.types import Context, Object, UILayout
from explainer_utils import bootstrap_utils


def layout_properties(layout: UILayout, context: Context):
    row = layout.row()
    row.use_property_decorate = True
    row.use_property_split = True
    row.prop(context.object, "group_with_children")


bootstrap_utils.object_panel_layouts.append((100, layout_properties))


def register_properties():
    Object.group_with_children = BoolProperty(
        name="Group With Children",
        description="Enables a variety of behaviors not documented here",
        default=False,
        options={'ANIMATABLE', 'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'}
    )

    Object.xu_breached = BoolProperty(
        name="Breached",
        description="An internal property that explainer utils uses for things",
        options={'HIDDEN', 'SKIP_SAVE'}
    )


bootstrap_utils.register_listeners.append(register_properties)


def unregister_properties():
    Object.group_with_children = None
    Object.xu_breached = None


bootstrap_utils.unregister_listeners.append(unregister_properties)
