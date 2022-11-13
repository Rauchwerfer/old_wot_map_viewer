''' ShadowHunterRUS 2015-2016 '''

import os
import shutil

import bpy

from mathutils import Vector
from bpy_extras.image_utils import load_image

from zipfile import ZipFile
from bpy.app import tempdir
from glob import glob
from ctypes import c_short, c_byte
from struct import unpack

def load(map_info, res_pkg_path, kill_dict):
    center = map_info['boundingBox']['upperRight'] + map_info['boundingBox']['bottomLeft']
    geometry = map_info['geometry']
    # pkg = '%s.pkg' % geometry.split('/')[1]
    # pkg_abs_path = os.path.join(res_pkg_path, pkg)

    for item in glob('E:\\Users\\Cherk\\Downloads\\World_of_Tanks_0.06.02.08.00_EU_0000_SD\\res\\' + geometry +  '\\*.cdata*'):
        bname = os.path.basename(item)

        hexX, hexY = int(bname[:4], 16), int(bname[4:8], 16)
        hexX = c_short(hexX).value
        hexY = c_short(hexY).value

        with ZipFile(item, 'r') as zfile:
            zfile.extractall(tempdir + '\\wot2\\' + bname[:8], ['terrain2/lodTexture.dds', 'terrain2/heights1'])
        with open(tempdir + '\\wot2\\' + bname[:8] + '\\terrain2\\heights1.png', 'wb') as fw:
            with open(tempdir + '\\wot2\\' + bname[:8] + '\\terrain2\\heights1', 'rb') as fr:
                magic = fr.read(4)
                png_width, png_height = unpack('<2I', fr.read(8))
                fr.seek(36)
                fw.write(fr.read())
        raw = load_image(tempdir + '\\wot2\\' + bname[:8] + '\\terrain2\\heights1.png')
        rp = list(raw.pixels)
        img = bpy.data.images.remove(raw)
        assert(png_width*png_height == len(rp)//4)
        pos = [0, png_height-1]
        verts = []

        for i in range(0, len(rp), 4):
            tb = c_byte(int(rp[i+2] * 255)).value
            rp[i+2] = tb / 255.0
            scaleFactor = 1000.0 / 256.0
            h = (rp[i] + rp[i+1] * 256 + rp[i+2] * 65536) / scaleFactor

            x = pos[0] * 100.0 / (png_width-1)
            y = pos[1] * 100.0 / (png_height-1)
            z = h

            verts.append(Vector((x, y, z)))

            if pos[0] == png_width-1:
                pos[1] -= 1
                pos[0] = 0
            else:
                pos[0] += 1

        faces = []
        for i in range(0, len(verts)-png_width-1):
            if (i+1) % png_width == 0:
                continue
            faces.append((i+1, i, i+png_width, i+png_width+1))

        bmesh = bpy.data.meshes.new('Mesh_' + bname[:8])
        bmesh.from_pydata(verts, [], faces)
        bmesh.validate()
        bmesh.update()

        material = bpy.data.materials.new('Material_' + bname[:8])
        material.specular_intensity = 0.0
        texture = bpy.data.textures.new(name='Texture_' + bname[:8], type='IMAGE')
        img = load_image(tempdir + '\\wot2\\' + bname[:8] + '\\terrain2\\lodTexture.dds')
        img.use_alpha = False
        img.name = bname[:8] + '_lodTexture.dds'
        img.pack()
        texture.image = img
        mtex = material.texture_slots.add()
        mtex.texture = texture
        mtex.texture_coords = 'ORCO'

        bmesh.materials.append(material)

        ob = bpy.data.objects.new(bname[:8], bmesh)
        ob.location.x = hexX * 100.0 + center.x
        ob.location.y = hexY * 100.0 + center.y

        bpy.context.scene.objects.link(ob)

        kill_dict['Meshes'].append(bmesh.name)
        kill_dict['Objects'].append(ob.name)
        kill_dict['Materials'].append(material.name)
        kill_dict['Textures'].append(texture.name)
        kill_dict['Images'].append(img.name)

    # shutil.rmtree(tempdir + '\\wot')
    shutil.rmtree(tempdir + '\\wot2')


""" def load(map_info, res_pkg_path, kill_dict):
    center = map_info['boundingBox']['upperRight'] + map_info['boundingBox']['bottomLeft']
    geometry = map_info['geometry']
    pkg = '%s.pkg' % geometry.split('/')[1]
    pkg_abs_path = os.path.join(res_pkg_path, pkg)
    with ZipFile(pkg_abs_path, 'r') as zfile:
        zfile.extractall(tempdir + '\\wot')
    for item in glob(tempdir + '\\wot\\' + geometry + '\\*.cdata*'):
        bname = os.path.basename(item)

        hexX, hexY = int(bname[:4], 16), int(bname[4:8], 16)
        hexX = c_short(hexX).value
        hexY = c_short(hexY).value

        with ZipFile(item, 'r') as zfile:
            zfile.extractall(tempdir + '\\wot2\\' + bname[:8], ['terrain2/lodTexture.dds', 'terrain2/heights'])
        with open(tempdir + '\\wot2\\' + bname[:8] + '\\terrain2\\heights.png', 'wb') as fw:
            with open(tempdir + '\\wot2\\' + bname[:8] + '\\terrain2\\heights', 'rb') as fr:
                magic = fr.read(4)
                png_width, png_height = unpack('<2I', fr.read(8))
                fr.seek(36)
                fw.write(fr.read())
        raw = load_image(tempdir + '\\wot2\\' + bname[:8] + '\\terrain2\\heights.png')
        rp = list(raw.pixels)
        img = bpy.data.images.remove(raw)
        assert(png_width*png_height == len(rp)//4)
        pos = [0, png_height-1]
        verts = []

        for i in range(0, len(rp), 4):
            tb = c_byte(int(rp[i+2] * 255)).value
            rp[i+2] = tb / 255.0
            scaleFactor = 1000.0 / 256.0
            h = (rp[i] + rp[i+1] * 256 + rp[i+2] * 65536) / scaleFactor

            x = pos[0] * 100.0 / (png_width-1)
            y = pos[1] * 100.0 / (png_height-1)
            z = h

            verts.append(Vector((x, y, z)))

            if pos[0] == png_width-1:
                pos[1] -= 1
                pos[0] = 0
            else:
                pos[0] += 1

        faces = []
        for i in range(0, len(verts)-png_width-1):
            if (i+1) % png_width == 0:
                continue
            faces.append((i+1, i, i+png_width, i+png_width+1))

        bmesh = bpy.data.meshes.new('Mesh_' + bname[:8])
        bmesh.from_pydata(verts, [], faces)
        bmesh.validate()
        bmesh.update()

        material = bpy.data.materials.new('Material_' + bname[:8])
        material.specular_intensity = 0.0
        texture = bpy.data.textures.new(name='Texture_' + bname[:8], type='IMAGE')
        img = load_image(tempdir + '\\wot2\\' + bname[:8] + '\\terrain2\\lodTexture.dds')
        img.use_alpha = False
        img.name = bname[:8] + '_lodTexture.dds'
        img.pack()
        texture.image = img
        mtex = material.texture_slots.add()
        mtex.texture = texture
        mtex.texture_coords = 'ORCO'

        bmesh.materials.append(material)

        ob = bpy.data.objects.new(bname[:8], bmesh)
        ob.location.x = hexX * 100.0 + center.x
        ob.location.y = hexY * 100.0 + center.y

        bpy.context.scene.objects.link(ob)

        kill_dict['Meshes'].append(bmesh.name)
        kill_dict['Objects'].append(ob.name)
        kill_dict['Materials'].append(material.name)
        kill_dict['Textures'].append(texture.name)
        kill_dict['Images'].append(img.name)

    shutil.rmtree(tempdir + '\\wot')
    shutil.rmtree(tempdir + '\\wot2')
 """