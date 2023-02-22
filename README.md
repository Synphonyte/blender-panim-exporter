# Blender PANIM Exporter

Export all animations of custom properties in a Blender file as a binary .panim file

## Installation

Download the file [io_export_panim.py](https://raw.githubusercontent.com/Synphonyte/blender-panim-exporter/main/io_export_panim.py) and [install it in Blender as an addon](https://docs.blender.org/manual/en/latest/editors/preferences/addons.html#installing-add-ons).

## File format

The file format is a binary format that is designed to be as compact as possible. The following
shows the format of the file. It's given as `field_name - type`. All data is stored in little endian byte order.
At the moment only f32 frame values are supported.

```
version                 : u32
frames_per_second       : f32

<repeat for all objects and custom properties>

    object_name         : utf8 string, 0-terminated
    property_name       : utf8 string, 0-terminated
    frame_start         : u32
    frame_end           : u32
    value_type          : u8, not used currently. always 0.
    reserved            : 32 bytes of unused per prop data reserved for future use
    
    <repeat for every frame between frame_start until frame_end (including)>
        frame_value     : f32
    </repeat>
    
</repeat>
```