import bpy
from bpy.props import EnumProperty, FloatProperty, PointerProperty, StringProperty
from bpy.types import Material, Operator, PropertyGroup, Scene, Text
from bpy.utils import register_class, unregister_class
from explainer_utils import bootstrap_utils
import glob
from math import inf
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

# Some LaTeX code licensed under GPLv3
# https://github.com/ghseeli/latex2blender

class LatexSettings(PropertyGroup):
    source_type: EnumProperty(
        items=[(
            "inline", 
            "Inline", 
            "Specify code in a small text box intead of in a separate text editor"
        ), (
            "resource",
            "Resource",
            "Specify code in an embedded text resource instead of in an inline text box"
        )],
        name="Source Type",
        description="Where to source Latex code from",
        default="inline"
    )

    inline_source: StringProperty(
        name="Source",
        description="Enter Latex Code",
        default="",
    )
    
    resource_source: PointerProperty(
        type=Text,
        name="Source",
        description="The file to source Latex code from"
    )

    scale: FloatProperty(
        name="Scale",
        description="Size of the imported object",
        default=1.0,
        min=0.0,
        max=inf
    )
    
    material: PointerProperty(
        type=Material,
        name="Material",
        description="Choose a material"
    )


def get_latex_source(scene):
    t = scene.explainer_latex_settings
    if t.source_type == 'inline':
        return t.inline_source
    elif t.resource_source is None:
        return "No source file selected"
    else:
        return t.resource_source.as_string()

def save_latex_file(temp_dir, latex_code):
    # Create temp latex file with specified preamble.
    temp_file_name = temp_dir.joinpath('explainer_latex_import.tex')
    temp = open(temp_file_name, "w")
    default_preamble = '\\documentclass{amsart}\n\\usepackage{amssymb,amsfonts}\n\\usepackage{tikz}' \
                       '\n\\usepackage{tikz-cd}\n\\pagestyle{empty}\n\\thispagestyle{empty}'
    temp.write(default_preamble)

    # Add latex code to temp.tex and close the file.
    temp.write('\n\\begin{document}\n' + latex_code + '\n\\end{document}')
    temp.close()
    
    return temp_file_name

def create_svg_file(latex_file):
    # Updates 'PATH' to include reference to folder containing latex and dvisvgm executable files.
    # This only matters when running on MacOS. It is unnecessary for Linux and Windows.
    latex_exec_path = '/Library/TeX/texbin'
    local_env = os.environ.copy()
    local_env['PATH'] = (latex_exec_path + os.pathsep + local_env['PATH'])
    
    subprocess.call(["latex", "-output-directory", str(latex_file.parent), "-interaction=batchmode", str(latex_file)], env=local_env)
    subprocess.call(["dvisvgm", "--no-fonts", str(latex_file.with_suffix(".dvi")), "-o", str(latex_file.with_suffix(".svg"))], env=local_env)

def import_svg(latex_file):
    bpy.ops.object.select_all(action='DESELECT')
    fpaths = glob.glob(str(latex_file.with_name("*.svg")))
    if len(fpaths) == 0:
        raise Exception("LaTeX produced no output (possibly due to a syntax error)")
    bpy.ops.import_curve.svg(filepath=str(fpaths[0]))

def prettify_imported_object(context, user_scale):
    collection = bpy.data.collections["explainer_latex_import.svg"]
    first = collection.objects[0]
    for obj in collection.objects:
        obj.select_set(True)
    context.view_layer.objects.active = first
    bpy.ops.object.join()
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    
    settings = context.scene.explainer_latex_settings
    
    user_scale = settings.scale
    scale = 500.0 * user_scale
    first.scale = [scale, scale, scale]
    bpy.ops.object.transform_apply()
    first.name = "LaTeX"
    
    mat = settings.material
    if mat is not None:
        first.material_slots[0].material = mat
    
    bpy.data.collections.remove(collection)
    context.scene.collection.objects.link(first)
    context.view_layer.objects.active = first

class AddLatex(Operator):
    """Adds rendered LaTeX code. If a selected object's name starts with LaTeX, its mesh will be replaced instead of the imported mesh being added as a new object."""
    bl_idname = "mesh.latex_add"
    bl_label = "Add/Replace LaTeX"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        replace_targets = []
        for item in context.selected_objects:
            if item.name[:5] == "LaTeX":
                replace_targets.append(item)
        source = get_latex_source(context.scene)
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_file = save_latex_file(temp_path, source)
            try:
                create_svg_file(source_file)
                import_svg(source_file)
                prettify_imported_object(context, context.scene.explainer_latex_settings.scale)
                final_object = context.selected_objects[0]
                if len(replace_targets) > 0:
                    for target in replace_targets:
                        target.data = final_object.data
                    bpy.ops.object.delete()
                    for target in replace_targets:
                        target.select_set(True)
                else:
                    final_object.location = context.scene.cursor.location
            except Exception as e:
                self.report({"ERROR"}, "Failed to render LaTeX code:\n" + str(e))
        return {"FINISHED"}


def register():
    register_class(LatexSettings)
    register_class(AddLatex)
    Scene.explainer_latex_settings = PointerProperty(type=LatexSettings)

def unregister():
    unregister_class(LatexSettings)
    unregister_class(AddLatex)
    Scene.explainer_latex_settings = None


bootstrap_utils.register_listeners.append(register)
bootstrap_utils.unregister_listeners.append(unregister)
