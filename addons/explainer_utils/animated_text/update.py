from bpy.types import Depsgraph, Object, Scene
from explainer_utils import bootstrap_utils
from explainer_utils.animated_text.utils import split_parts
from math import inf
import string


def update_obj(scene: Scene, depsgraph: Depsgraph, obj: Object):
    if not obj.use_animated_text or obj.type != 'FONT':
        return
    obj.instantiate_linked = False
    evaluated = obj
    if depsgraph is not None:
        evaluated = obj.evaluated_get(depsgraph)
    material_indexes = []
    text = ''
    arg_idx = 0
    for (raw_text, format_spec) in split_parts(obj.template_text):
        text += raw_text
        material_indexes += [0] * len(raw_text)
        if format_spec is not None:
            arg_key = "hacky_format_arg_{}".format(arg_idx)
            formatted = (
                '{:' + format_spec + '}').format(getattr(evaluated, arg_key))
            mat_key = "hacky_format_mat_{}".format(arg_idx)
            text += formatted
            material_indexes += [getattr(evaluated, mat_key)] * len(formatted)
            arg_idx += 1
    obj.data.body = text
    for i, mat_idx in enumerate(material_indexes):
        obj.data.body_format[i].material_index = mat_idx


def update(scene: Scene, depsgraph: Depsgraph):
    for obj in scene.objects:
        update_obj(scene, depsgraph, obj)


bootstrap_utils.update_listeners.append(update)
