import bpy
from bpy.app import handlers
from bpy.app.handlers import persistent
from bpy.props import BoolProperty, IntProperty
from bpy.types import Depsgraph, Object, Scene
from collections.abc import Callable
from explainer_utils import bootstrap_utils
from explainer_utils.alpha.composite import compute_composite_alpha_on_frame


saving_right_now = False
rendering_right_now = False


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
        default=120,
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
    Object.xu_hidden_render = BoolProperty(
        name="Hidden In Render Due To Transparency",
        description="Internal property used by explainer utils",
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'}
    )


def unregister_properties():
    Scene.hide_transparent = None
    Scene.visibility_range = None
    Object.xu_hidden = None


def max_alpha_in_time_window(obj: Object, window_start: int, window_end: int) -> float:
    ma = 0.0
    for frame in range(window_start, window_end):
        ma = max(ma, compute_composite_alpha_on_frame(obj, frame))
    return ma


# Hide an object based on its transparency.
def update_object_visibility(scene: Scene, obj: Object):
    global saving_right_now, now_rendering
    if not scene.hide_transparent or saving_right_now or obj.select_get():
        reset_object_visibility(obj)
        return

    window_start = scene.frame_current - scene.visibility_range
    window_middle = scene.frame_current
    window_end = scene.frame_current + scene.visibility_range
    # A much cheaper (but technically inaccurate) alternative to checking the
    # alpha at all frames in the range.
    ma = max(
        compute_composite_alpha_on_frame(obj, window_start),
        compute_composite_alpha_on_frame(obj, window_middle),
        compute_composite_alpha_on_frame(obj, window_end),
    )
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

    try:
        if should_hide and not obj.hide_get():
            obj.xu_hidden = True
            obj.hide_set(True)
        elif not should_hide and obj.xu_hidden:
            obj.xu_hidden = False
            obj.hide_set(False)
    except:
        pass


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
        reset_object_visibility_in_render(obj)


def reset_file_visibility():
    for scene in bpy.data.scenes:
        reset_scene_visibility(scene)


def update_object_visibility_in_render(scene: Scene, obj: Object):
    alpha = compute_composite_alpha_on_frame(obj, scene.frame_current)
    should_hide = alpha < 1e-5
    if obj.is_occluder:
        if len(obj.children) == 0:
            should_hide = False
        elif obj.composite_alpha > 1 - 1e-5:
            should_hide = True
    if should_hide and not obj.hide_render:
        obj.xu_hidden_render = True
        obj.hide_render = True
    elif not should_hide and obj.xu_hidden_render:
        obj.xu_hidden_render = False
        obj.hide_render = False


def reset_object_visibility_in_render(obj: Object):
    if obj.xu_hidden_render:
        obj.xu_hidden_render = False
        obj.hide_render = False


now_rendering = False


@persistent
def render_pre_handler(scene: Scene, depsgraph: Depsgraph):
    global now_rendering
    now_rendering = True
    for obj in scene.objects:
        update_object_visibility_in_render(scene, obj)


@persistent
def render_post_handler(scene: Scene, depsgraph: Depsgraph):
    global now_rendering
    now_rendering = False
    for obj in scene.objects:
        reset_object_visibility_in_render(obj)


@persistent
def save_pre_handler(scene: Scene, depsgraph: Depsgraph):
    global saving_right_now
    saving_right_now = True
    reset_file_visibility()


@persistent
def save_post_handler(scene: Scene, depsgraph: Depsgraph):
    global saving_right_now
    saving_right_now = False
    update_file_visibility()


def register_odd_handlers():
    handlers.save_pre.append(save_pre_handler)
    handlers.save_post.append(save_post_handler)
    handlers.load_post.append(save_post_handler)
    handlers.render_pre.append(render_pre_handler)
    handlers.render_post.append(render_post_handler)


def unregister_odd_handlers():
    handlers.save_pre.remove(save_pre_handler)
    handlers.save_post.remove(save_post_handler)
    handlers.load_post.remove(save_post_handler)
    handlers.render_pre.remove(render_pre_handler)
    handlers.render_post.remove(render_post_handler)
    reset_file_visibility()


@persistent
def update_handler(scene: Scene, depsgraph: Depsgraph):
    update_scene_visibility(scene)


bootstrap_utils.register_listeners.append(register_properties)
bootstrap_utils.register_listeners.append(register_odd_handlers)
bootstrap_utils.unregister_listeners.append(unregister_odd_handlers)
bootstrap_utils.unregister_listeners.append(unregister_properties)
bootstrap_utils.update_listeners.append(update_handler)
