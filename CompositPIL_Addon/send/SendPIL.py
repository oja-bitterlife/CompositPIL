import bpy
import requests, json


# DEFINE
CANNY_SERVER_URL = "http://localhost:{:d}/canny"


# Convert Canny
# *****************************************************************************
def run(context, canny_url, no):
    data = {
        "output_path": bpy.path.abspath(context.scene.canny_output_path),
        "scale_type": context.scene.canny_scale_type,
        "canny_data": context.scene.canny_data[no].toJSON()
    }

    # リモート実行
    try:
        response = requests.get(canny_url, params=data)
        if response.status_code != 200:
            return "サーバでの処理に失敗しました"
    except Exception as e:
        return "サーバとの接続に失敗しました"

    return None

class COMPOSIT_PIL_OT_run_all(bpy.types.Operator):
    bl_idname = "composit_pil.run_all"
    bl_label = "Run All"

    def execute(self, context):

        for i in range(len(context.scene.canny_data)):
            response = run(context, CANNY_SERVER_URL.format(context.scene.canny_server_port), i)

        # 自動更新
        if context.scene.canny_after_reload:
            for image in bpy.data.images:
                image.reload()

        return{'FINISHED'}


# 個別
class COMPOSIT_PIL_OT_run(bpy.types.Operator):
    bl_idname = "composit_pil.run"
    bl_label = "Run"

    id: bpy.props.IntProperty()

    def execute(self, context):
        error_txt = run(context, CANNY_SERVER_URL.format(context.scene.canny_server_port), self.id)
        if error_txt != None:
            self.report({'ERROR'}, error_txt)
            return{'FINISHED'}

        # 自動更新
        if context.scene.canny_after_reload:
            for image in bpy.data.images:
                image.reload()

        return{'FINISHED'}


# Add/Remove/move
# *****************************************************************************
class COMPOSIT_PIL_OT_add(bpy.types.Operator):
    bl_idname = "composit_pil.add"
    bl_label = "Add Reference Image"

    def execute(self, context):
        context.scene.canny_data.add()
        return{'FINISHED'}

class COMPOSIT_PIL_OT_remove(bpy.types.Operator):
    bl_idname = "composit_pil.remove"
    bl_label = ""

    id: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.canny_data.remove(self.id)
        return{'FINISHED'}

class COMPOSIT_PIL_OT_moveup(bpy.types.Operator):
    bl_idname = "composit_pil.moveup"
    bl_label = ""

    id: bpy.props.IntProperty()

    def execute(self, context):
        if self.id > 0:
            context.scene.canny_data.move(self.id-1, self.id)
        return{'FINISHED'}

class COMPOSIT_PIL_OT_movedown(bpy.types.Operator):
    bl_idname = "composit_pil.movedown"
    bl_label = ""

    id: bpy.props.IntProperty()

    def execute(self, context):
        if self.id < len(context.scene.canny_data)-1:
            context.scene.canny_data.move(self.id, self.id+1)
        return{'FINISHED'}


# register/unregister
# *****************************************************************************
classes = [
    COMPOSIT_PIL_OT_run_all,
    COMPOSIT_PIL_OT_run,
    COMPOSIT_PIL_OT_add,
    COMPOSIT_PIL_OT_remove,
    COMPOSIT_PIL_OT_moveup,
    COMPOSIT_PIL_OT_movedown,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
