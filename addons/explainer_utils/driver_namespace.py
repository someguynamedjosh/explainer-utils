import bpy
from explainer_utils import bootstrap_utils


def register():
    def lerp(a, b, factor):
        return a * (1.0 - factor) + b * factor

    def lerp3(a, b, c, factor):
        if factor < 1.0:
            return lerp(a, b, factor)
        else:
            return lerp(b, c, factor - 1.0)

    bpy.app.driver_namespace['lerp'] = lerp
    bpy.app.driver_namespace['lerp3'] = lerp3


def unregister():
    bpy.app.driver_namespace['lerp'] = None
    bpy.app.driver_namespace['lerp3'] = None


bootstrap_utils.register_listeners.append(register)
bootstrap_utils.unregister_listeners.append(unregister)
