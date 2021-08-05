import bpy
from bpy.app import handlers
from bpy.app.handlers import persistent
from bpy.props import BoolProperty, IntProperty
from bpy.types import Depsgraph, Object, Scene
from collections.abc import Callable
from explainer_utils import bootstrap_utils
from explainer_utils.alpha.composite import compute_composite_alpha_on_frame


def register_properties():
    Scene.hide_transparent = BoolProperty(
        name="Hide Transparent",
        description="When checked, transparent objects will be hidden in the viewport",
        default=True,
        options=set()
    )
    Scene.visibility_range = IntProperty(
        name="Visibility Range",
        description="How long an object should remain visible in the viewport after it has become transparent",
        default=1,
        min=1,
        soft_min=1,
        options=set(),
    )
    Object.xu_hidden = BoolProperty(
        name="Hidden Due To Transparency",
        description="Internal property used by explainer utils",
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'}
    )


def unregister_properties():
    Object.xu_hidden = None


def max_alpha_in_time_window(obj: Object, window_start: int, window_end: int) -> float:
    ma = 0.0
    for frame in range(window_start, window_end):
        ma = max(ma, compute_composite_alpha_on_frame(obj, frame))
    return ma


# Hide an object based on its transparency.
def update_object_visibility(scene: Scene, obj: Object):
    if not scene.hide_transparent or obj.select_get():
        reset_object_visibility(obj)
        return

    window_start = scene.frame_current - scene.visibility_range
    window_end = scene.frame_current + scene.visibility_range
    ma = max_alpha_in_time_window(obj, window_start, window_end)
    alpha_now = obj.composite_alpha

    should_hide = False
    if obj.is_occluder:
        if alpha_now > 1 - 1e-5:
            # Occluders should be hidden when they are not occluding anything.
            should_hide = True
        if len(obj.children) > 0 and alpha_now < 1e-5:
            # Occluders hiding only their children should hide themselves
            # regardless of the time window.
            should_hide = True
    elif ma < 1e-5:
        should_hide = True

    if should_hide and not obj.hide_get():
        obj.xu_hidden = True
        obj.hide_set(True)
    elif not should_hide and obj.xu_hidden:
        obj.xu_hidden = False
        obj.hide_set(False)


def update_scene_visibility(scene: Scene):
    for obj in scene.objects:
        update_object_visibility(scene, obj)


def update_file_visibility():
    for scene in bpy.data.scenes:
        update_scene_visibility(scene)


# Undoes the effect of $update_object_visibility(obj)
def reset_object_visibility(obj: Object):
    if obj.xu_hidden:
        obj.xu_hidden = False
        obj.hide_set(False)


def reset_scene_visibility(scene: Scene):
    for obj in scene.objects:
        reset_object_visibility(obj)


def reset_file_visibility():
    for scene in bpy.data.scenes:
        reset_scene_visibility(scene)


@persistent
def save_pre_handler(scene: Scene, depsgraph: Depsgraph):
    reset_file_visibility()


@persistent
def save_post_handler(scene: Scene, depsgraph: Depsgraph):
    update_file_visibility()


def register_odd_handlers():
    handlers.save_pre.append(save_pre_handler)
    handlers.save_post.append(save_post_handler)
    handlers.load_post.append(save_post_handler)


def unregister_odd_handlers():
    handlers.save_pre.remove(save_pre_handler)
    handlers.save_post.remove(save_post_handler)
    handlers.load_post.remove(save_post_handler)
    reset_file_visibility()


@persistent
def update_handler(scene: Scene, depsgraph: Depsgraph):
    update_scene_visibility(scene)


bootstrap_utils.register_listeners.append(register_properties)
bootstrap_utils.register_listeners.append(register_odd_handlers)
bootstrap_utils.unregister_listeners.append(unregister_odd_handlers)
bootstrap_utils.unregister_listeners.append(unregister_properties)
bootstrap_utils.update_listeners.append(update_handler)
