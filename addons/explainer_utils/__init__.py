from . import bootstrap_utils
from bpy.app import handlers

bl_info = {
    "name": "Explainer Utils",
    "category": "All",
    "location": "View3D > Object > Explainer Utils; Properties > Object > Explainer Utils; Topbar > Render",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
}


def module_and_children(module_name, child_names):
    return [
        module_name,
        *[module_name + "." + child_name for child_name in child_names]
    ]


# A list of all modules excluding the root module and bootstrap_utils.
modules = module_and_children(__name__, [
    "add_transition",
    "copy_render_settings",
    "driver_namespace",
    "exclude_from_render",
    "latex",
    "lazy_parent",
    *module_and_children("storage", [
        "instantiate",
        "properties"
    ]),
    *module_and_children("ui", [
        "main_pie",
        "object_properties_panel",
        "viewport_menu",
        "viewport_side_panels"
    ]),
])[1:]


def register():
    bootstrap_utils.clear_all_registries()
    for module in modules:
        bootstrap_utils.import_or_reload(module)
    for listener in bootstrap_utils.register_listeners:
        listener()


def unregister():
    for listener in bootstrap_utils.unregister_listeners:
        listener()
