import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty
from bpy.types import FCurve, Object, Operator, Scene
from explainer_utils import bootstrap_utils


def has_any_selected_parent(obj: Object) -> bool:
    if obj.parent is None:
        return False
    elif obj.parent.select_get():
        return True
    else:
        return has_any_selected_parent(obj.parent)


def find_nearest_keyframes(scene: Scene, fcurve: FCurve):
    kp = fcurve.keyframe_points
    nearest_before = None
    nearest_after = None
    now = scene.frame_current
    for kpi in range(len(kp)):
        if kp[kpi].co.x <= now:
            nearest_before = kpi
        else:
            nearest_after = kpi
            break
    return (nearest_before, nearest_after)


def find_keyframes_to_adjust(scene: Scene, mode: str, start: float, end: float, fcurve: FCurve):
    (nearest_before, nearest_after) = find_nearest_keyframes(scene, fcurve)
    both_are_some = nearest_before is not None and nearest_after is not None
    kp = fcurve.keyframe_points
    # If the two keyframes on opposite sides of the current frame have the fade we want...
    if both_are_some and kp[nearest_before].co.y == start and kp[nearest_after].co.y == end:
        return (nearest_before, nearest_after)
    # If the keyframe to the left has the end of the fade we want...
    elif nearest_before is not None and kp[nearest_before].co.y == end:
        # ...and the keyframe before that has the start of the fade we want...
        if nearest_before > 0 and kp[nearest_before - 1].co.y == start:
            return (nearest_before - 1, nearest_before)
    # If the keyframe to the right has the start of the fade we want...
    elif nearest_after is not None and kp[nearest_after].co.y == start:
        # ...and the keyframe after that has the end of the fade we want...
        if nearest_after < len(kp) - 1 and kp[nearest_after + 1].co.y == end:
            return (nearest_after, nearest_after + 1)
    return None


def adjust_keyframe_timing(fcurve: FCurve, new_duration: int, move_end: bool, start_index: int, end_index: int):
    kp = fcurve.keyframe_points
    if move_end:
        kp[end_index].co.x = kp[start_index].co.x + new_duration
    else:
        kp[start_index].co.x = kp[end_index].co.x - new_duration


def try_updating_existing_keyframes(obj: Object, scene: Scene, mode: str, start: float, end: float, duration: int):
    fcurve = None
    if obj.animation_data is not None and obj.animation_data.action is not None:
        fcurve = obj.animation_data.action.fcurves.find('alpha')
    if fcurve is not None and len(fcurve.keyframe_points) >= 2:
        kta = find_keyframes_to_adjust(scene, mode, start, end, fcurve)
        if kta is not None:
            (a, b) = kta
            adjust_keyframe_timing(fcurve, duration, start > end, a, b)
            return True
    return False


def insert_new_alpha_keyframes(obj: Object, scene: Scene, start: float, end: float, duration: int):
    obj.alpha = end
    obj.keyframe_insert(data_path='alpha')
    obj.alpha = start
    obj.keyframe_insert(
        data_path='alpha',
        frame=scene.frame_current - duration
    )


def make_alpha_keyframes_linear(obj: Object):
    fcurve = obj.animation_data.action.fcurves.find('alpha')
    for k in fcurve.keyframe_points:
        k.interpolation = 'LINEAR'
    fcurve.update()


class FadeOperator(Operator):
    """Fades an object in or out by animating its alpha"""
    bl_idname = "object.explainer_fade"
    bl_label = "Fade Objects"
    bl_options = {'REGISTER', 'UNDO'}

    duration: IntProperty(name="Duration", min=0, default=30)
    mode: EnumProperty(
        items=[
            ("fade_in", "Fade In", "", "TRACKING_FORWARDS", 0),
            ("fade_out", "Fade Out", "", "TRACKING_CLEAR_BACKWARDS", 1),
        ],
        name="Mode"
    )
    black_point: FloatProperty(
        name="Black Point", min=0.0, max=1.0, default=0.0)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        start, end = self.black_point, 1.0
        if self.mode == 'fade_out':
            start, end = 1.0, self.black_point
        for obj in context.selected_objects:
            if has_any_selected_parent(obj):
                continue
            if not try_updating_existing_keyframes(obj, context.scene, self.mode, start, end, self.duration):
                insert_new_alpha_keyframes(
                    obj, context.scene, start, end, self.duration)
                make_alpha_keyframes_linear(obj)
            obj.update_tag()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(FadeOperator)


def unregister():
    bpy.utils.unregister_class(FadeOperator)


bootstrap_utils.register_listeners.append(register)
bootstrap_utils.unregister_listeners.append(unregister)
