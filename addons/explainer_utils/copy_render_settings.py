import bpy
from bpy.types import Operator, TOPBAR_MT_render
from bpy.utils import register_class, unregister_class
from explainer_utils import bootstrap_utils


class CopyRenderSettings(Operator):
    bl_idname = "global.copy_render_settings"
    bl_label = "Copy Render Settings To Other Scenes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        proto = context.scene
        for scene in bpy.data.scenes:
            for key in proto.eevee.__dir__():
                if key[0:2] == '__' or key in ['bl_rna', 'rna_type', 'gi_cache_info']:
                    continue
                setattr(scene.eevee, key, getattr(proto.eevee, key))
            for key in proto.cycles.keys():
                setattr(scene.cycles, key, getattr(proto.cycles, key))
            for key in ['use_file_extension', 'use_render_cache', 'use_overwrite', 'use_placeholder']:
                setattr(scene.render, key, getattr(proto.render, key))
            for key in ['file_format', 'color_mode', 'color_depth', 'exr_codec']:
                setattr(scene.render.image_settings, key,
                        getattr(proto.render.image_settings, key))
            scene.render.resolution_percentage = proto.render.resolution_percentage
        return {'FINISHED'}


class CopyRenderSize(Operator):
    bl_idname = "global.copy_render_size"
    bl_label = "Copy Render Size To Other Scenes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        proto = context.scene
        for scene in bpy.data.scenes:
            scene.render.resolution_x = proto.render.resolution_x
            scene.render.resolution_y = proto.render.resolution_y
            scene.render.resolution_percentage = proto.render.resolution_percentage
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(CopyRenderSettings.bl_idname)
    self.layout.operator(CopyRenderSize.bl_idname)


def register():
    register_class(CopyRenderSettings)
    register_class(CopyRenderSize)
    TOPBAR_MT_render.append(menu_func)


def unregister():
    unregister_class(CopyRenderSettings)
    unregister_class(CopyRenderSize)
    TOPBAR_MT_render.remove(menu_func)


bootstrap_utils.register_listeners.append(register)
bootstrap_utils.unregister_listeners.append(unregister)
