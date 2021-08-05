from bpy.types import Depsgraph, Object, Scene
from collections.abc import Callable
from explainer_utils import bootstrap_utils


def compute_composite_alpha(obj: Object, alpha_getter: Callable[[Object], float]) -> float:
    composite_alpha = alpha_getter(obj)
    obj = obj.parent
    while obj is not None:
        if not obj.is_occluder:
            composite_alpha *= alpha_getter(obj)
        elif alpha_getter(obj) < 1e-5:
            composite_alpha = 0.0
        obj = obj.parent
    return composite_alpha


def get_alpha_on_frame(obj: Object, frame: int) -> float:
    if not obj.animation_data or not obj.animation_data.action or not obj.animation_data.action.fcurves:
        return obj.alpha
    for fcurve in obj.animation_data.action.fcurves:
        if fcurve.data_path == 'alpha':
            return fcurve.evaluate(frame)
    return obj.alpha


def compute_composite_alpha_on_frame(obj: Object, frame: int) -> float:
    def alpha_getter(o): return get_alpha_on_frame(o, frame)
    return compute_composite_alpha(obj, alpha_getter)


def get_alpha_via_depsgraph(obj: Object, depsgraph: Depsgraph) -> float:
    if depsgraph is None:
        return obj.alpha
    else:
        return obj.evaluated_get(depsgraph).alpha


def update_composite_alphas(scene: Scene, depsgraph: Depsgraph):
    def alpha_getter(o): return get_alpha_via_depsgraph(o, depsgraph)
    for obj in scene.objects:
        ca = compute_composite_alpha(obj, alpha_getter)
        obj.composite_alpha = ca


bootstrap_utils.update_listeners.append(update_composite_alphas)