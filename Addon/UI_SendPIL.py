import bpy
import requests, json
from urllib.parse import urlencode

# DEFINE
SERVER_PORT = 8080
CANNY_SERVER_URL = "http://localhost:{:d}/canny".format(SERVER_PORT)


# Data Structure
# *****************************************************************************
IMAGE_TYPES = (
    # id, view, desc
    ("BW", "BW", ""),
    ("RGB", "RGB", "AにRGBの結果をまとめてます"),
    ("RGBA", "RGBA", ""),
    ("ALPHA", "ALPHA", "Aがあれば使い無ければGrayScaleを使います"),
    ("DEPTH", "DEPTH", "BWと同じ"),
)

class CANNY_DATA(bpy.types.PropertyGroup):
    image_name: bpy.props.StringProperty(name="image name", default="//")
    image_type: bpy.props.EnumProperty(name = "image type", items=IMAGE_TYPES)
    alpha_threshold: bpy.props.FloatProperty(name = "alpha threshold", default=0.5, min=0, max=1)
    adjacent: bpy.props.IntProperty(name = "minVal", default=80, min=0, max=1000)
    threshold: bpy.props.IntProperty(name = "maxVal", default=255, min=0, max=1000)

    def toJSON(self):
        return json.dumps({
            "image_name": bpy.path.abspath(self.image_name),
            "image_type": self.image_type,
            "alpha_threshold": self.alpha_threshold,
            "adjacent": self.adjacent,
            "threshold": self.threshold,
        })


# Convert Canny
# *****************************************************************************
def run(context, canny_url, no):
    data = {
        "output_path": bpy.path.abspath(context.scene.canny_output_path),
        "canny_data": context.scene.canny_data[no].toJSON()
    }

    # リモート実行
    response = requests.get(canny_url, params=data)
    print(response.text)

    return response

class COMPOSIT_PIL_OT_run_all(bpy.types.Operator):
    bl_idname = "composit_pil.run_all"
    bl_label = "Run All"

    def execute(self, context):

        for i in range(len(context.scene.canny_data)):
            response = run(context, CANNY_SERVER_URL, i)

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
        response = run(context, CANNY_SERVER_URL, self.id)

        # 自動更新
        if context.scene.canny_after_reload:
            for image in bpy.data.images:
                image.reload()

        return{'FINISHED'}

# Add/Remove
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


# draw UI
# *****************************************************************************
def draw(self, context):
    self.layout.prop(context.scene, "canny_output_path", text="Output Path")
    self.layout.prop(context.scene, "canny_after_reload", text="Auto Reload")  # 実行後リロード

    box = self.layout.box()
    box.operator("composit_pil.add")

    # 画像ごとの設定
    for i, canny_data in enumerate(context.scene.canny_data):
        img_box = box.box()

        # 画像タイプ(Canny時の前処理が変わる)
        row = img_box.row().split(align=True, factor=0.9)
        row.prop(canny_data, "image_type", text="Image Type")
        row.operator("composit_pil.remove", icon="PANEL_CLOSE").id = i  # 閉じるボタンをつけておく
        # alpha専用
        if getattr(canny_data, "image_type") in ["ALPHA", "RGBA"]:
            img_box.prop(canny_data, "alpha_threshold", text="Alpha Threshold")

        # 画像名(###が数字に置き換わる)
        img_box.prop(canny_data, "image_name", text="Image Name")

        # cannyのminVal/maxVal設定
        row = img_box.row()
        row.prop(canny_data, "adjacent", text="min")
        row.prop(canny_data, "threshold", text="max")

        # 実行ボタン
        img_box.operator("composit_pil.run").id = i

    # 全部実行ボタン
    self.layout.operator("composit_pil.run_all")


# register/unregister
# *****************************************************************************
def register():
    bpy.types.Scene.canny_output_path = bpy.props.StringProperty(name="output path", default="//canny_edge")
    bpy.types.Scene.canny_data = bpy.props.CollectionProperty(type=CANNY_DATA)
    bpy.types.Scene.canny_after_reload = bpy.props.BoolProperty(name="after reload", default=True)

def unregister():
    pass

