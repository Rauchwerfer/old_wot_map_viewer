''' ShadowHunterRUS 2015-2016 '''



#####################################################################
# imports

from .XmlUnpacker import XmlUnpacker
from .string_utils import *

import os
import gettext



#####################################################################
# WoT res path

wot_res_path = ''



#####################################################################
# arenas.mo file

arenas_mo_gettext = None



#####################################################################
# L10n - function

def _a(str_):
    try:
        return arenas_mo_gettext.gettext('%s/name' % str_)
    except:
        return str_



def init(wot_res_path_):
    global arenas_mo_gettext, wot_res_path

    wot_res_path = wot_res_path_

    arenas_mo_path = os.path.join(wot_res_path, 'text', 'lc_messages', 'arenas.mo')
    if not os.path.exists(arenas_mo_path):
        raise Exception('`%s` not exists' % arenas_mo_path)

    arenas_mo_gettext = gettext.GNUTranslations(open(arenas_mo_path, 'rb'))



def fini():
    global arenas_mo_gettext, wot_res_path

    wot_res_path = ''
    arenas_mo_gettext = None



#####################################################################
# Maps List loader

def load_maps_dictionary():
    list_file_path = os.path.join(wot_res_path, 'scripts', 'arena_defs', '_list_.xml')
    if not os.path.exists(list_file_path):
        raise Exception('`%s` not exists' % list_file_path)

    with open(list_file_path, 'rb') as f:
        xmlr = XmlUnpacker()
        listNodes = xmlr.read(f)

    maps_list = []
    for node in listNodes.findall('map'):
        if node.find('id') is None or node.find('name') is None:
            return

        map_id = AsInt(node.find('id').text)
        map_name = node.find('name').text.strip()
        map_l10n_name = _a(map_name)
        maps_list.append((map_id, map_name, map_l10n_name))

    return maps_list



#####################################################################
# Map Info loader

def load_map_info(map_name):
    map_info_file_path = os.path.join(wot_res_path, 'scripts', 'arena_defs', '%s.xml' % map_name)
    map_info = {}

    if not os.path.exists(map_info_file_path):
        raise Exception('`%s` not exists' % map_info_file_path)

    with open(map_info_file_path, 'rb') as f:
        xmlr = XmlUnpacker()
        nodes = xmlr.read(f)

    map_info['geometry'] = nodes.find('geometry').text.strip()

    map_info['boundingBox'] = {
        'bottomLeft': AsVector(nodes.find('boundingBox/bottomLeft').text),
        'upperRight': AsVector(nodes.find('boundingBox/upperRight').text)
    }

    return map_info
