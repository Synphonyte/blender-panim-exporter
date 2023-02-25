bl_info = {
    "name": "Export custom props anim (.panim)",
    "author": "Marc-Stefan Cassola (maccesch)",
    "version": (0, 2, 0),
    "blender": (3, 4, 0),
    "location": "File > Export > Custom Props Anim (.panim)",
    "description": "Export all animations of custom properties as a binary .panim file",
    "doc_url": "https://github.com/Synphonyte/blender-panim-exporter",
    "category": "Import-Export",
}

import bpy
import re
import struct

def i32(i):
    return struct.pack("<i", i)


def u32(i):
    return struct.pack("<I", i)


def f32(f):
    return struct.pack("<f", f)

def write_anim_data(context, filepath):
    print("Exporting custom props anim data...")
    f = open(filepath, 'wb')

    major, minor, patch = bl_info["version"]
    major = u32(major << 20)
    minor = u32(minor << 10)
    patch = u32(patch)

    file_version = bytes(x | y | z for (x, y), z in zip(zip(major, minor), patch))
    f.write(file_version)

    f.write(f32(bpy.data.scenes["Scene"].render.fps))

    pattern = re.compile(r'\["([^"]+)"\]')

    for obj in bpy.data.objects:
        if obj.animation_data is not None:
            action = obj.animation_data.action

            for fcurve in action.fcurves:
                m = re.match(pattern, fcurve.data_path)
                if m is not None:
                    f.write(obj.name.encode('utf-8'))
                    f.write(b'\0')  # 0-terminated string

                    name = m.group(1)
                    f.write(name.encode('utf-8'))
                    f.write(b'\0')  # 0-terminated string

                    frame_start, frame_end = [int(x) for x in fcurve.range()]

                    f.write(u32(frame_start))
                    f.write(u32(frame_end))

                    typ = b'\0' # TODO : support other types like vector values and so on
                    f.write(typ)

                    reserved_per_prop_data = b'\0' * 32
                    f.write(reserved_per_prop_data)

                    for frame in range(frame_start, frame_end + 1):
                        bpy.context.scene.frame_set(frame)
                        f.write(f32(obj[name]))

    f.close()

    return {'FINISHED'}


from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportCustomPropsAnim(Operator, ExportHelper):
    """Export all animations of all custom properties"""
    bl_idname = "export_custom_props_anim.synphonyte_com"
    bl_label = "Export Custom Props Anim"

    filename_ext = ".panim"

    filter_glob: StringProperty(
        default="*.panim",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        return write_anim_data(context, self.filepath)


def menu_func_export(self, context):
    self.layout.operator(ExportCustomPropsAnim.bl_idname, text="Custom Props Anim (.panim)")


def register():
    bpy.utils.register_class(ExportCustomPropsAnim)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportCustomPropsAnim)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
