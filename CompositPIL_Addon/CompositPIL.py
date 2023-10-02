import bpy

from . import UI_SendPIL

# UIカテゴリ名
COMPIL_CATEGORY = "CompositPIL"

# Main UI
# ===========================================================================================
# Compositing Tools Panel
class COMPOSIT_PIL_PT_ui(bpy.types.Panel):
    bl_label = "ConvertCanny"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = COMPIL_CATEGORY
    bl_idname = "COMPOSIT_PIL_PT_UI"
#    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        UI_SendPIL.draw(self, context)
 
def register():
    pass

def unregister():
    pass
