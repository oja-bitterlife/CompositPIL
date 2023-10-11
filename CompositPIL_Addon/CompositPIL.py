import bpy

from . import UI_SendPIL, UI_AppendNodes

# UIカテゴリ名
COMPIL_CATEGORY = "CompositPIL"


# Main UI
# ===========================================================================================
# Compositing Tools Panel
class COMPOSIT_PIL_PT_node_ui(bpy.types.Panel):
    bl_label = "ConvertCanny"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = COMPIL_CATEGORY
    bl_idname = "COMPOSIT_PIL_PT_NODE_UI"

    def draw(self, context):
        self.layout.label(text="Append Resources")
        self.layout.operator("composit_pil.append_composit_nodes")


class COMPOSIT_PIL_PT_view_ui(bpy.types.Panel):
    bl_label = "ConvertCanny"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = COMPIL_CATEGORY
    bl_idname = "COMPOSIT_PIL_PT_VIEW_UI"

    def draw(self, context):
        self.layout.label(text="Append Resources")
        self.layout.operator("composit_pil.append_3dview_nodes")


def register():
    pass

def unregister():
    pass
