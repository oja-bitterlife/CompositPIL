import bpy
import json
from .send import SendPIL

# UIカテゴリ名
COMPIL_CATEGORY = "CompositPIL"

# Data Structure
# *****************************************************************************
IMAGE_TYPES = (
    # id, view, desc
    ("BW", "BW", "GlayScale"),
    ("RGB", "RGB", "RGB各チャンネルで実行。AはRGBの合成結果"),
    ("ALPHA", "ALPHA", "Aがあれば使い無ければGrayScaleを使います"),
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
    output_prefix: bpy.props.StringProperty(name="output prefix")

    def toJSON(self):
        return json.dumps({
            "image_name": bpy.path.abspath(self.image_name),
            "image_type": self.image_type,
            "alpha_threshold": self.alpha_threshold,
            "adjacent": self.adjacent,
            "threshold": self.threshold,
            "output_prefix": self.output_prefix,
        })


# Main UI
# ===========================================================================================
class COMPOSIT_PIL_PT_compositing_ui(bpy.types.Panel):
    bl_idname = "COMPOSIT_PIL_PT_COMP_UI"
    bl_label = "ConvertCanny"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = COMPIL_CATEGORY

    def draw(self, context):
        # compositingの時だけ表示するように
        if context.space_data.tree_type != 'CompositorNodeTree':
            self.layout.label(text="compositing only")
            return

        self.layout.prop(context.scene, "canny_output_path", text="Output Path")  # 出力パス

        self.layout.prop(context.scene, "canny_scale_type", text="Scale Type")  # 事前拡大モード
        self.layout.prop(context.scene, "canny_after_reload", text="Auto Reload")  # 実行後リロード

        box = self.layout.box()
        box.operator("composit_pil.add")

        # 画像ごとの設定
        for i, canny_data in enumerate(context.scene.canny_data):
            img_box = box.box()

            # 画像タイプ(Canny時の前処理が変わる)
            row = img_box.row().split(align=True, factor=0.75)
            row.prop(canny_data, "image_type", text="Image Type")

            # 上下閉じるボタン
            row.operator("composit_pil.moveup", icon="TRIA_UP").id = i
            row.operator("composit_pil.movedown", icon="TRIA_DOWN").id = i
            row.operator("composit_pil.remove", icon="PANEL_CLOSE").id = i

            # alpha専用
            if getattr(canny_data, "image_type") in ["ALPHA", "RGBA"]:
                img_box.prop(canny_data, "alpha_threshold", text="Alpha Threshold")

            # 画像名(###が数字に置き換わる)
            img_box.prop(canny_data, "image_name", text="Image Name")

            # cannyのminVal/maxVal設定
            row = img_box.row()
            row.prop(canny_data, "adjacent", text="min")
            row.prop(canny_data, "threshold", text="max")

            # 生成ファイルのprefix設定
            img_box.prop(canny_data, "output_prefix", text="Output Prefix")

            # 実行ボタン
            img_box.operator("composit_pil.run").id = i

        # サーバポート指定
        row = self.layout.box().row().split(align=True, factor=0.1)
        if context.scene.canny_server_port_lock:
            row.prop(context.scene, "canny_server_port_lock", icon="LOCKED", text="")
        else:
            row.prop(context.scene, "canny_server_port_lock", icon="UNLOCKED", text="")
        row_child = row.row()
        if context.scene.canny_server_port_lock:
            row_child.enabled = False
        row_child.prop(context.scene, "canny_server_port", text="Server Port")

        # 全部実行ボタン
        self.layout.operator("composit_pil.run_all")


# register/unregister
# *****************************************************************************
modules = [
    SendPIL,
]

def register():
    bpy.types.Scene.canny_output_path = bpy.props.StringProperty(name="output path", default="//canny_edge")
    bpy.types.Scene.canny_data = bpy.props.CollectionProperty(type=CANNY_DATA)
    bpy.types.Scene.canny_after_reload = bpy.props.BoolProperty(name="after reload", default=True)
    bpy.types.Scene.canny_scale_type = bpy.props.EnumProperty(name = "image type", items=SCALE_TYPES, default="x2c-down")

    bpy.types.Scene.canny_server_port_lock = bpy.props.BoolProperty(name="server port lock", default=True)
    bpy.types.Scene.canny_server_port = bpy.props.IntProperty(name="server port", default=8080, min=0, max=65535)

    for module in modules:
        if hasattr(module, "register"):
            module.register()

def unregister():
    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()
