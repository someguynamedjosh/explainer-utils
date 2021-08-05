from bpy.types import Context, Object, UILayout
from explainer_utils import bootstrap_utils
from explainer_utils.animated_text.properties import NUM_HACKY_FORMAT_ARGS
from explainer_utils.animated_text.utils import count_parts


def layout_hacky_format_arg(layout: UILayout, context: Context, arg_index: int):
    object = context.object

    mat_names = object.data.materials.keys()
    c = layout.column(align=True)

    r = c.row()
    r.enabled = object.use_animated_text
    r.use_property_decorate = True
    r.use_property_split = True
    r.prop(object, "hacky_format_arg_{}".format(arg_index))

    r = c.row()
    r.enabled = object.use_animated_text
    r.use_property_decorate = True
    r.use_property_split = True
    label = "?"
    mat_idx = getattr(object, "hacky_format_mat_{}".format(arg_index))
    if mat_idx < len(mat_names):
        label = mat_names[mat_idx]
    r.prop(object, "hacky_format_mat_{}".format(arg_index), text="Material")
    r.separator()
    r.label(text=label)


def do_layout(layout: UILayout, context: Context):
    object = context.object
    if object.type != 'FONT':
        return

    r = layout.row()
    r.use_property_decorate = True
    r.use_property_split = True
    r.prop(object, "use_animated_text")

    r = layout.row()
    r.enabled = object.use_animated_text
    r.use_property_decorate = True
    r.use_property_split = True
    r.prop(object, "template_text")

    parts = count_parts(object.template_text)
    for arg_index in range(min(NUM_HACKY_FORMAT_ARGS, parts)):
        layout_hacky_format_arg(layout, context, arg_index)


bootstrap_utils.object_panel_layouts.append((700, do_layout))
