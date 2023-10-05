import bpy
import os.path

TARGET_MATERIAL_NODES = ["OjaNPR2023.10", "OjaSpec2023.10"]
TARGET_COMPOSIT_NODES = ["OjaCOMPIL_Normal"]

# Append
# *****************************************************************************
class COMPOSIT_PIL_OT_append_material_nodes(bpy.types.Operator):
    bl_idname = "composit_pil.append_material_nodes"
    bl_label = "Material NodeGroups"

    def execute(self, context):
        # すでに全部読み込んであれば何もしない
        if all([bpy.data.node_groups.get(ng) != None for ng in TARGET_MATERIAL_NODES]):
            return{'FINISHED'}

        # データ転送
        script_file = os.path.realpath(__file__)
        resource_file = os.path.join(os.path.dirname(script_file), "resource", "resource.blend")

        with bpy.data.libraries.load(resource_file, link=False, relative=True) as (data_from, data_to):
            for ng in data_from.node_groups:
                # 追加対象のみ処理
                if ng in TARGET_MATERIAL_NODES:
                    if bpy.data.node_groups.get(ng):  # 存在すればなにもしない
                        continue
                    else:
                        data_to.node_groups.append(ng)
                        print("append:", ng)

        return{'FINISHED'}


class COMPOSIT_PIL_OT_append_composit_nodes(bpy.types.Operator):
    bl_idname = "composit_pil.append_composit_nodes"
    bl_label = "Compositing NodeGroups"

    def execute(self, context):
        # すでに全部読み込んであれば何もしない
        if all([bpy.data.node_groups.get(ng) != None for ng in TARGET_COMPOSIT_NODES]):
            return{'FINISHED'}

        # データ転送
        script_file = os.path.realpath(__file__)
        resource_file = os.path.join(os.path.dirname(script_file), "resource", "resource.blend")

        with bpy.data.libraries.load(resource_file, link=False, relative=True) as (data_from, data_to):
            for ng in data_from.node_groups:
                # 追加対象のみ処理
                if ng in TARGET_COMPOSIT_NODES:
                    if bpy.data.node_groups.get(ng):  # 存在すればなにもしない
                        continue
                    else:
                        data_to.node_groups.append(ng)
                        print("append:", ng)

        return{'FINISHED'}


# draw UI
# *****************************************************************************
def draw(self, context):
    # Loadボタン
    self.layout.label(text="Append Resources")
    self.layout.operator("composit_pil.append_material_nodes")
    self.layout.operator("composit_pil.append_composit_nodes")


# register/unregister
# *****************************************************************************
def register():
    pass

def unregister():
    pass
