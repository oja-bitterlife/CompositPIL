import bpy
import requests, json
from urllib.parse import urlencode

# DEFINE
SERVER_PORT = 8080
CANNY_SERVER_URL = "http://localhost:{:d}/canny"


# Data Structure
# *****************************************************************************
IMAGE_TYPES = (
    # id, view, desc
    ("BW", "BW", "GlayScale"),
    ("RGB", "RGB", "RGB各チャンネルで実行。AはRGBの合成結果"),
    ("RGBA", "RGBA", "RGBモードとALPHAモードを実行"),
    ("ALPHA", "ALPHA", "Aがあれば使い無ければGrayScaleを使います"),
    ("DEPTH", "DEPTH", "BWと同じ"),
)

SCALE_TYPES = (
    # id, view, desc
    ("None", "None", "そのままのサイズで変換"),
    ("x2c-up", "x2(Bicubic)", "拡大した画像で変換し出力"),
    ("x2c-down", "x2(Bicubic) -> x0.5(Bicubic)", "拡大して変換後元のサイズで出力"),
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
        "scale_type": context.scene.canny_scale_type,
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
        response = run(context, CANNY_SERVER_URL.format(context.scene.canny_server_port), self.id)

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
    self.layout.prop(context.scene, "canny_scale_type", text="Scale Type")
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

    # サーバポート指定
    row = self.layout.box().row().split(align=True, factor=0.2)
    row.prop(context.scene, "canny_server_port_lock", text="Lock")  # 実行後リロード
    row_child = row.row()
    if context.scene.canny_server_port_lock:
        row_child.enabled = False
    row_child.prop(context.scene, "canny_server_port", text="Server Port")

    # 全部実行ボタン
    self.layout.operator("composit_pil.run_all")


# register/unregister
# *****************************************************************************
def register():
    bpy.types.Scene.canny_output_path = bpy.props.StringProperty(name="output path", default="//canny_edge")
    bpy.types.Scene.canny_data = bpy.props.CollectionProperty(type=CANNY_DATA)
    bpy.types.Scene.canny_after_reload = bpy.props.BoolProperty(name="after reload", default=True)
    bpy.types.Scene.canny_scale_type = bpy.props.EnumProperty(name = "image type", items=SCALE_TYPES, default="x2c-down")

    bpy.types.Scene.canny_server_port_lock = bpy.props.BoolProperty(name="server port lock", default=True)
    bpy.types.Scene.canny_server_port = bpy.props.IntProperty(name="server port", default=8080, min=0, max=65535)

def unregister():
    pass
