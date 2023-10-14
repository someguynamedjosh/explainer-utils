import bpy
from bpy.props import IntProperty, StringProperty, PointerProperty
from bpy.types import Menu, Operator, PropertyGroup
from bpy.utils import register_class, unregister_class
from explainer_utils import bootstrap_utils
import math


def get_fcurve(obj, property_path, index):
    if obj.animation_data is None or obj.animation_data.action is None:
        return None
    for fcurve in obj.animation_data.action.fcurves:
        if fcurve.data_path == property_path and (index == -1 or fcurve.array_index == index):
            return fcurve
    return None


def get_animated_value(context, obj, property_path, index):
    fcurve = get_fcurve(obj, property_path, index)
    if fcurve is not None:
        return fcurve.evaluate(context.scene.frame_current)
    return None


def get_anim_progress_property_name(anim_name):
    node_group = bpy.data.node_groups[anim_name]
    for i in node_group.inputs:
        if i.name.startswith('Progress'):
            return i.identifier

def actual_framerate(context):
    return context.scene.render.fps / context.scene.render.fps_base


class TimingSettings(PropertyGroup):
    short_time: IntProperty(name="Short Time", min=0, default=20)
    med_time: IntProperty(name="Medium Time", min=0, default=50)
    long_time: IntProperty(name="Long Time", min=0, default=120)
    jump_time: IntProperty(name="Jump Time", min=0, default=30)


class AddTransitionImpl(Operator):
    bl_idname = "anim.explainer_add_transition_impl"
    bl_label = "Add Transition"
    bl_options = {'REGISTER', 'UNDO'}

    anim_name: StringProperty(name="Anim Name", default="")

    def execute(self, context):
        # Get the property under the mouse cursor
        obj = None
        prop_path = None
        index = -1
        bipolar = False

        if self.anim_name == '':
            if 'property' not in dir(context):
                self.report({'ERROR'}, "No property under the mouse cursor")
                return {'CANCELLED'}
            obj, prop_path, index = context.property
            print(index)
        else:
            bipolar = '(Bipolar)' in self.anim_name
            obj = context.active_object
            modifier_name = None
            input_name = get_anim_progress_property_name(self.anim_name)
            for mod in obj.modifiers:
                if mod.type == 'NODES' and mod.node_group is not None and mod.node_group.name == self.anim_name:
                    modifier_name = mod.name
                    break
            if modifier_name is None:
                mod = obj.modifiers.new(self.anim_name, 'NODES')
                mod.node_group = bpy.data.node_groups[self.anim_name]
                modifier_name = mod.name
            prop_path = f'modifiers["{modifier_name}"]["{input_name}"]'

        transition_from = get_animated_value(context, obj, prop_path, index)
        index_text = f'[{index}]' if index != -1 else ''
        overridden_val = eval(f'obj.{prop_path}{index_text}')
        if transition_from is None:
            transition_from = overridden_val
        transition_to = 0.0
        if abs(overridden_val - transition_from) > 0.001:
            transition_to = overridden_val
        elif abs(transition_from - 1.0) > 0.01:
            transition_to = 1.0
        else:
            transition_to = 2.0 if bipolar else 0.0
        
        duration = 0.333333
        frame_hint_pos = self.anim_name.find(' Seconds)')
        if frame_hint_pos != -1:
            trimmed = self.anim_name[:frame_hint_pos]
            start = trimmed.rfind('(')
            try:
                duration = float(trimmed[start + 1:])
            except:
                self.report({'ERROR'}, f'Malformed duration in animation name "{self.anim_name}"')
                return {'CANCELLED'}
        duration = int(math.ceil(duration * actual_framerate(context)))

        exec(f'obj.{prop_path}{index_text} = {transition_from}')
        obj.keyframe_insert(data_path=prop_path, index=index)
        exec(f'obj.{prop_path}{index_text} = {transition_to}')
        obj.keyframe_insert(data_path=prop_path, index=index,
                            frame=context.scene.frame_current + duration)
        obj.update_tag()
        if 'modifiers' in prop_path:
            obj.modifiers.update()
        context.scene.frame_current += 1
        context.scene.frame_current -= 1
        context.view_layer.update()
        return {'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}


class FrameOffsetJump(Operator):
    """Jump a certain number of frames (depending on the setting in the scene)"""
    bl_idname = "anim.explainer_jump"
    bl_label = "Jump"

    multiplier: IntProperty(name="Multiplier", default=1)

    def execute(self, context):
        context.scene.frame_current += context.scene.explainer_timing_settings.jump_time * self.multiplier
        return {'FINISHED'}


class TransitionMenu(Menu):
    bl_idname = "VIEW3D_MT_explainer_transitions"
    bl_label = "Transitions"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        layout.separator()
        # layout.operator(AddTransitionImpl.bl_idname,
        #                 text="Short").duration = context.scene.explainer_timing_settings.short_time
        for node_group in bpy.data.node_groups:
            name = node_group.name_full
            if 'Anim' in name and get_anim_progress_property_name(name) is not None:
                layout.operator(AddTransitionImpl.bl_idname,
                                text=name).anim_name = name


class AddTransition(Operator):
    bl_idname = "anim.explainer_add_transition"
    bl_label = "Add Transition"

    def execute(self, context):
        if 'property' not in dir(context) or context.property is None:
            bpy.ops.wm.call_menu(name=TransitionMenu.bl_idname)
        else:
            bpy.ops.anim.explainer_add_transition_impl()
        return {'FINISHED'}


def draw_transition_menu(self, context):
    layout = self.layout
    layout.menu(TransitionMenu.bl_idname)
    layout.separator()


keymap = None
keymap2 = None
keymap_item = None
keymap_item2 = None
keymap_item3 = None


def register():
    global keymap, keymap2, keymap_item, keymap_item2, keymap_item3
    register_class(FrameOffsetJump)
    register_class(TimingSettings)
    register_class(AddTransitionImpl)
    register_class(TransitionMenu)
    register_class(AddTransition)

    bpy.types.Scene.explainer_timing_settings = PointerProperty(
        type=TimingSettings)
    bpy.types.VIEW3D_MT_object_animation.prepend(draw_transition_menu)

    keyconfigs = bpy.context.window_manager.keyconfigs
    keymap = keyconfigs.addon.keymaps.new(
        name='Window', space_type='EMPTY')
    keymap_item = keymap.keymap_items.new(
        AddTransition.bl_idname, 'F', 'PRESS')

    keymap2 = keyconfigs.addon.keymaps.new(
        name='Frames', space_type='EMPTY')
    keymap_item2 = keymap2.keymap_items.new(
        FrameOffsetJump.bl_idname, 'UP_ARROW', 'PRESS', shift=True)
    keymap_item2.properties.multiplier = 1
    keymap_item3 = keymap2.keymap_items.new(
        FrameOffsetJump.bl_idname, 'DOWN_ARROW', 'PRESS', shift=True)
    keymap_item3.properties.multiplier = -1


def unregister():
    bpy.types.VIEW3D_MT_object_animation.remove(draw_transition_menu)
    keymap.keymap_items.remove(keymap_item)
    keymap2.keymap_items.remove(keymap_item2)
    keymap2.keymap_items.remove(keymap_item3)

    unregister_class(TransitionMenu)
    unregister_class(AddTransitionImpl)
    unregister_class(TimingSettings)
    unregister_class(FrameOffsetJump)
    unregister_class(AddTransition)


bootstrap_utils.register_listeners.append(register)
bootstrap_utils.unregister_listeners.append(unregister)
