import bpy
import os.path

TARGET_NODE_GROUPS = [
    # Material
    "OjaNPR2023.10",
    "OjaSpec2023.10",
    # GeometryNodes
    "OjaGN_Billboard_ZRot",
    "OjaGN_AutoSmooth",
    # Compositing
    "OjaCOMPIL_Normal",
]

APPEND_BUTTON_LABEL = "Append NodeGroups"


# Append
# *****************************************************************************
def AppendNodes():
    # すでに全部読み込んであれば何もしない
    if all([bpy.data.node_groups.get(ng) != None for ng in TARGET_NODE_GROUPS]):
        return{'FINISHED'}

    # データ転送
    script_file = os.path.realpath(__file__)
    resource_file = os.path.join(os.path.dirname(script_file), "resource", "resource.blend")

    with bpy.data.libraries.load(resource_file, link=False, relative=True) as (data_from, data_to):
        for ng in data_from.node_groups:
            # 追加対象のみ処理
            if ng in TARGET_NODE_GROUPS:
                if bpy.data.node_groups.get(ng):  # 存在すればなにもしない
                    continue
                else:
                    data_to.node_groups.append(ng)
                    print("append:", ng)


class COMPOSIT_PIL_OT_append_3dview_nodes(bpy.types.Operator):
    bl_idname = "composit_pil.append_3dview_nodes"
    bl_label = APPEND_BUTTON_LABEL

    def execute(self, context):
        AppendNodes()
        return{'FINISHED'}


class COMPOSIT_PIL_OT_append_composit_nodes(bpy.types.Operator):
    bl_idname = "composit_pil.append_composit_nodes"
    bl_label = APPEND_BUTTON_LABEL

    def execute(self, context):
        AppendNodes()
        return{'FINISHED'}


# register/unregister
# *****************************************************************************
def register():
    pass

def unregister():
    pass
