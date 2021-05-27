#
# Copyright (C) 2020 by Modicolitor
#
# This file is part of PuzzleUrPrint.
#
# License Text
#
# You should have received a copy of the GNU General Public License along with PuzzleUrPrint. If
# not, see <https://www.gnu.org/licenses/>.
import bpy
from .aom_properties import FloatdataItem
from .aom_properties import AOMPropertyGroup
from .aom_ui import BE_PT_AdvOceanAdd
from .aom_ui import BE_PT_AdvOceanMenu
from .aom_ui import BE_PT_AdvOceanInteract
from .aom_ui import BE_PT_AdvOceanFoam
from .aom_ui import BE_PT_AdvOceanWaves
from .aom_ui import BE_PT_AdvOceanMat
from .aom import BE_OT_FloatSelButt
from .aom import BE_OT_StaticOb
from .aom import BE_OT_GenOceanMat
#from .aom import BE_OT_SetStorm
#from .aom import BE_OT_SetMod
#from .aom import BE_OT_SetLov
from .aom import BE_OT_UpdateOceAniFrame
#from .aom import BE_OT_UpdateWeather
from .aom import BE_OT_GenOceanButton
from .aom import BE_OT_CageVisability
from .aom import BE_OT_RemBtn
#from .aom import BE_OT_GenObjFoam
from .aom import BE_OT_DeleteOcean
from .aom import BE_OT_SetPreset

#from .modalops import PP_OT_PlanarZScaleMenu


#from bpy.types import Scene, Image, Object


#from .utils import addon_auto_imports

bl_info = {  # für export als addon
    "name": "Advanced Ocean Modifier",
    "author": "Modicolitor",
    "version": (3, 00),
    "blender": (3, 00, 0),
    "location": "View3D > Tools",
    "description": "Create an Ocean with all Material properties set and add as many floating Objects as you like.",
    "category": "Object"}

#from .ui import PP_PT_PuzzlePrintActive
#from.gizmos import PUrP_CouplSizeGizmo


'''define the Centerobject and make it globally avaiable'''

# Centerobj Pointer


classes = (BE_PT_AdvOceanAdd,
           BE_PT_AdvOceanMenu,
           BE_PT_AdvOceanInteract,
           BE_PT_AdvOceanFoam,
           BE_PT_AdvOceanWaves,
           BE_PT_AdvOceanMat,
           BE_OT_FloatSelButt,
           BE_OT_StaticOb,
           BE_OT_GenOceanMat,
           # BE_OT_SetStorm,
           # BE_OT_SetMod,
           # BE_OT_SetLov,
           BE_OT_UpdateOceAniFrame,
           # BE_OT_UpdateWeather,
           BE_OT_GenOceanButton,
           BE_OT_CageVisability,
           BE_OT_RemBtn,
           # BE_OT_GenObjFoam,
           BE_OT_DeleteOcean,
           AOMPropertyGroup,
           BE_OT_SetPreset,
           FloatdataItem
           )

register, unregister = bpy.utils.register_classes_factory(classes)
