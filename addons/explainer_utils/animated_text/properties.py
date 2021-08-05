from bpy.types import Object
from bpy.props import BoolProperty, FloatProperty, IntProperty, StringProperty
from explainer_utils import bootstrap_utils
from math import inf

NUM_HACKY_FORMAT_ARGS = 12


def set_material_idx(key):
    def impl(self, value):
        l = len(self.data.materials)
        self[key] = max(min(value, l-1), 0)
    return impl


def basic_get(key, default):
    # what the fuck
    return lambda s: s.get(key, default)


def set_format_arg(key):
    def impl(self, value):
        self[key] = value
    return impl


def register():
    Object.use_animated_text = BoolProperty(
        name="Use Animated Text",
        description="Enables animated text",
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'}
    )
    Object.template_text = StringProperty(
        name="Template",
        description="Template text for animation, using Python format syntax.\n{} = a value\n{:.2f} = float with 2 decimal places\n{:+} = always show a sign",
        default="",
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE'}
    )

    for i in range(NUM_HACKY_FORMAT_ARGS):
        key = "hacky_format_arg_{}".format(i)
        prop = FloatProperty(
            name="Arg #{}".format(i+1),
            description="A value to insert into the template",
            default=0.0,
            min=-inf,
            max=inf,
            soft_min=-inf,
            soft_max=inf,
            precision=2,
            options={'ANIMATABLE', 'LIBRARY_EDITABLE'},
            override={'LIBRARY_OVERRIDABLE'},
            set=set_format_arg(key),
            get=basic_get(key, 0.0)
        )
        setattr(Object, key, prop)
        key = "hacky_format_mat_{}".format(i)
        prop = IntProperty(
            name="Mat",
            description="The index of the material to apply to this argument",
            default=0,
            min=0,
            max=99,
            options={'ANIMATABLE', 'LIBRARY_EDITABLE'},
            override={'LIBRARY_OVERRIDABLE'},
            set=set_material_idx(key),
            get=basic_get(key, 0)
        )
        setattr(Object, key, prop)


def unregister():
    Object.use_animated_text = None
    Object.template_text = None
    for i in range(NUM_HACKY_FORMAT_ARGS):
        key = "hacky_format_arg_{}".format(i)
        setattr(Object, key, None)
        key = "hacky_format_mat_{}".format(i)
        setattr(Object, key, None)


bootstrap_utils.register_listeners.append(register)
bootstrap_utils.unregister_listeners.append(unregister)
