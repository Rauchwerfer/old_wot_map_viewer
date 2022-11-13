''' ShadowHunterRUS 2015-2016 '''



#####################################################################
# Addon - header

bl_info = {
    "name": "My World of Tanks - Maps Viewer",
    "author": "ShadowHunterRUS",
    "version": (0, 0, 4),
    "blender": (2, 78, 0),
    "location": "View3D > Tool Shelf > WoTMapsViewer",
    "description": "My WoT Maps Viewer",
    "warning": "Test version",
    "wiki_url": "http://www.koreanrandom.com/forum/topic/28240-/",
    "category": "3D View",
}



#####################################################################
# Import settings

from .settings import *



#####################################################################
# imports

import os

from . import maps_utils
from . import map_loader

import bpy



#####################################################################
# defaults

user_preferences = bpy.context.user_preferences
wot_parse_status = False
current_map_info = None
current_map_models = {}



#####################################################################
# Delete models

def deleteModels(kill_dict):
    use_global_undo_orig = user_preferences.edit.use_global_undo
    user_preferences.edit.use_global_undo = False

    if kill_dict.get('Objects'):
        for object_name in kill_dict['Objects']:
            if bpy.data.objects.get(object_name):
                object_ = bpy.data.objects[object_name]
                bpy.context.scene.objects.unlink(object_)
                bpy.data.objects.remove(object_)

    if kill_dict.get('Meshes'):
        for mesh_name in kill_dict['Meshes']:
            if bpy.data.meshes.get(mesh_name):
                mesh_ = bpy.data.meshes[mesh_name]
                bpy.data.meshes.remove(mesh_)

    if kill_dict.get('Materials'):
        for material_name in kill_dict['Materials']:
            if bpy.data.materials.get(material_name):
                material_ = bpy.data.materials[material_name]
                bpy.data.materials.remove(material_)

    if kill_dict.get('Textures'):
        for texture_name in kill_dict['Textures']:
            if bpy.data.textures.get(texture_name):
                texture_ = bpy.data.textures[texture_name]
                bpy.data.textures.remove(texture_)

    if kill_dict.get('Images'):
        for image_name in kill_dict['Images']:
            if bpy.data.images.get(image_name):
                image_ = bpy.data.images[image_name]
                bpy.data.images.remove(image_)

    kill_dict.clear()
    kill_dict['Meshes'] = []
    kill_dict['Objects'] = []
    kill_dict['Images'] = []
    kill_dict['Materials'] = []
    kill_dict['Textures'] = []

    user_preferences.edit.use_global_undo = use_global_undo_orig



#####################################################################
# Apply Path Operator

class Apply_Path_Operator(bpy.types.Operator):
    bl_label = 'Operator apply paths'
    bl_idname = 'wotmapsviewer.apply_path_op'

    def execute(self, context):
        global wot_parse_status
        prefs = user_preferences.addons[__package__].preferences
        wot_exe_path = os.path.join(prefs.world_of_tanks_game_path, 'WorldOfTanks.exe')
        if not os.path.exists(wot_exe_path):
            # INFO, WARNING or ERROR
            self.report({'WARNING'}, 'Error in path!')
            return {'FINISHED'}

        # register
        bpy.utils.register_class(UI_WoTMaps_List)
        bpy.utils.register_class(MapsCustomProp)
        bpy.utils.register_class(Show_Map_Info_Operator)
        bpy.types.Scene.wot_maps_list_custom = bpy.props.CollectionProperty(type = MapsCustomProp)
        bpy.types.Scene.wot_maps_list_custom_index = bpy.props.IntProperty()
        bpy.utils.register_class(Panel_WoTMaps_List)

        # unregister
        bpy.utils.unregister_class(Panel_WoTMapsViewer_Start)
        bpy.utils.unregister_class(Apply_Path_Operator)

        maps_utils.init(os.path.join(prefs.world_of_tanks_game_path, 'res'))
        maps_list = maps_utils.load_maps_dictionary()

        scn = context.scene
        scn.wot_maps_list_custom_index = 0
        scn.wot_maps_list_custom.clear()

        for map_tuple in maps_list:
            wot_maps_list_item = scn.wot_maps_list_custom.add()
            wot_maps_list_item.name_l10n = map_tuple[2]
            wot_maps_list_item.map_name = map_tuple[1]
            wot_maps_list_item.map_id = map_tuple[0]

        wot_parse_status = True
        return {'FINISHED'}



#####################################################################
# WoTMapsViewerPreferences

class WoTMapsViewerPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    world_of_tanks_game_path = bpy.props.StringProperty(
        name = 'WoT Path',
        subtype = 'DIR_PATH',
        default = WOT_PATH_DEFAULT
    )

    def draw(self, context):
        layout = self.layout

        layout.prop(self, 'world_of_tanks_game_path')



#####################################################################
# Panel WoTMapsViewer Start

class Panel_WoTMapsViewer_Start(bpy.types.Panel):
    bl_label = 'Start'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'MyWoTMapsViewer'

    def draw(self, context):
        layout = self.layout

        layout.operator('wotmapsviewer.apply_path_op', text = 'Parse WoT')



#####################################################################
# MapsCustomProp

class MapsCustomProp(bpy.types.PropertyGroup):
    name_l10n = bpy.props.StringProperty()
    map_name = bpy.props.StringProperty()
    map_id = bpy.props.IntProperty()



#####################################################################
# UI_Maps_List

class UI_WoTMaps_List(bpy.types.UIList): 
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name_l10n, translate=False)



#####################################################################
# Panel Tank List

class Panel_WoTMaps_List(bpy.types.Panel):
    bl_label = 'WoT Maps List'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'MyWoTMapsViewer'

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        layout.row().template_list('UI_WoTMaps_List', '', scn, 'wot_maps_list_custom', scn, 'wot_maps_list_custom_index')

        layout.separator()
        layout.operator('wotmapsviewer.show_map_info', text='Show Map')

        if current_map_info:
            layout.label(str(current_map_info['geometry']))



#####################################################################
# Show Map Info Operator

class Show_Map_Info_Operator(bpy.types.Operator):
    bl_label = 'Operator show map info paths'
    bl_idname = 'wotmapsviewer.show_map_info'

    def execute(self, context):
        global current_map_info, current_map_models
        scn = context.scene
        map_name = scn.wot_maps_list_custom[scn.wot_maps_list_custom_index].map_name
        current_map_info = maps_utils.load_map_info(map_name)

        deleteModels(current_map_models)

        prefs = user_preferences.addons[__package__].preferences
        res_pkg_path = os.path.join(prefs.world_of_tanks_game_path, 'res', 'packages')
        map_loader.load(current_map_info, res_pkg_path, current_map_models)

        return {'FINISHED'}



#####################################################################
# unregister

def unregister():
    global wot_parse_status, current_map_info
    bpy.utils.unregister_class(WoTMapsViewerPreferences)
    current_map_info = None

    if wot_parse_status:
        wot_parse_status = False
        bpy.utils.unregister_class(UI_WoTMaps_List)
        bpy.utils.unregister_class(MapsCustomProp)
        bpy.utils.unregister_class(Show_Map_Info_Operator)
        bpy.utils.unregister_class(Panel_WoTMaps_List)
        del bpy.types.Scene.wot_maps_list_custom
        del bpy.types.Scene.wot_maps_list_custom_index
        maps_utils.fini()

    else:
        bpy.utils.unregister_class(Panel_WoTMapsViewer_Start)
        bpy.utils.unregister_class(Apply_Path_Operator)



#####################################################################
# register

def register():
    bpy.utils.register_class(WoTMapsViewerPreferences)
    bpy.utils.register_class(Panel_WoTMapsViewer_Start)
    bpy.utils.register_class(Apply_Path_Operator)
