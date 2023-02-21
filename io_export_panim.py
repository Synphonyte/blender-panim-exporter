bl_info = {
    "name": "Export custom props anim (.panim)",
    "author": "Marc-Stefan Cassola (maccesch)",
    "version": (1, 0, 0),
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

    f.write(f32(bpy.data.scenes["Scene"].render.fps))

    pattern = re.compile(r'\["([^"]+)"\]')

    for obj in bpy.data.objects:
        if obj.animation_data is not None and len(obj.animation_data.action.fcurves) == 1:
            action = obj.animation_data.action

            m = re.match(pattern, action.fcurves[0].data_path)
            if m is not None:
                f.write(obj.name.encode('utf-8'))
                f.write(b'\0')  # 0-terminated string

                name = m.group(1)
                f.write(name.encode('utf-8'))
                f.write(b'\0')  # 0-terminated string

                frame_start, frame_end = [int(x) for x in action.frame_range]

                f.write(u32(frame_start))
                f.write(u32(frame_end))

                typ = b'i' if type(obj[name]) is int else b'f'
                f.write(typ)

                for frame in range(frame_start, frame_end + 1):
                    bpy.context.scene.frame_set(frame)

                    if typ == b'i':
                        f.write(i32(obj[name]))
                    else:
                        f.write(f32(obj[name]))

    f.close()

    return {'FINISHED'}


from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportCustomPropsAnim(Operator, ExportHelper):
    """Export all animations of all custom properties"""
    bl_idname = "export_custom_props_anim.synphonyte.com"
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
