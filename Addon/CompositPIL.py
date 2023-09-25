import bpy

from . import UI_SendPIL

# Main UI
# ===========================================================================================
# Compositing Tools Panel
class COMPOSIT_PIL_PT_ui(bpy.types.Panel):
    bl_label = "CompositPIL"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "COMPIL"
    bl_idname = "COMPOSIT_PIL_PT_UI"
#    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        UI_SendPIL.draw(self, context)
 
def register():
    pass

def unregister():
    pass
