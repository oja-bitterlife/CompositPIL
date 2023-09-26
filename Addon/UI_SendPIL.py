import bpy
import requests


IMAGE_TYPES = (
    # id, view, desc
    ("BW", "BW", ""),
    ("RGB", "RGB", ""),
    ("ALPHA", "ALPHA", ""),
    ("DEPTH", "DEPTH", ""),
)

class CANNY_DATA(bpy.types.PropertyGroup):
    image_name: bpy.props.StringProperty(name="image name", default="//")
    image_type: bpy.props.EnumProperty(name = "image type", items=IMAGE_TYPES)
    alpha_threshold: bpy.props.FloatProperty(name = "alpha threshold", default=0.5, min=0, max=1)
#adjacent/threshold


# Convert Canny
class COMPOSIT_PIL_OT_send(bpy.types.Operator):
    bl_idname = "composit_pil.send"
    bl_label = "Run"

    def execute(self, context):
        # canny_url = "http://localhost:8080/canny"
        # data = {
        #     "output_path": bpy.path.abspath(context.scene.output_path),
        #     "image_name_1": bpy.path.abspath(context.scene.canny[0].image_name),
        #     "image_name_2": bpy.path.abspath(context.scene.canny[1].image_name),
        #     "image_name_3": bpy.path.abspath(context.scene.canny[2].image_name),
        # }
        # response = requests.get(canny_url, params=data)

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
        print(self.id)
        context.scene.canny_data.remove(self.id)
        return{'FINISHED'}


# draw UI
# *****************************************************************************
def draw(self, context):
    self.layout.prop(context.scene, "output_path", text="OutputPath")
    
    box = self.layout.box()
    box.label(text="Reference Images")
    box.operator("composit_pil.add")

    # 画像ごとの設定
    for i, canny_data in enumerate(context.scene.canny_data):
        img_box = box.box()
        row = img_box.row().split(align=True, factor=0.9)
        row.prop(canny_data, "image_type", text="ImageType")
        row.operator("composit_pil.remove", icon="PANEL_CLOSE").id = i
        img_box.prop(canny_data, "image_name", text="ImageName")
        if getattr(canny_data, "image_type") == "ALPHA":
            img_box.prop(canny_data, "alpha_threshold", text="AlphaThreshold")


    # 実行ボタン
    self.layout.prop(context.scene, "canny_after_reload", text="Auto Reload")
    self.layout.operator("composit_pil.send")


# register/unregister
# *****************************************************************************
def register():
    bpy.types.Scene.canny_output_path = bpy.props.StringProperty(name="output path", default="//")
    bpy.types.Scene.canny_data = bpy.props.CollectionProperty(type=CANNY_DATA)
    bpy.types.Scene.canny_after_reload = bpy.props.BoolProperty(name="after reload", default=True)

def unregister():
    pass

