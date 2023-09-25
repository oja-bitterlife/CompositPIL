import bpy
import requests

class COMPOSIT_PIL_OT_send(bpy.types.Operator):
    bl_idname = "composit_pil.send"
    bl_label = "Run"

    def execute(self, context):
        canny_url = "http://localhost:8080/canny"
        data = {
            "output_path": bpy.path.abspath(context.scene.output_path),
            "image_name1": bpy.path.abspath(context.scene.image_name1),
            "image_name2": bpy.path.abspath(context.scene.image_name2),
            "image_name3": bpy.path.abspath(context.scene.image_name3),
        }
        response = requests.get(canny_url, params=data)

        # for image in bpy.data.images:
        #     image.reload()
        print(response.json())
        return{'FINISHED'}

def draw(self, context):
    self.layout.prop(context.scene, "output_path", text="OutputPath")
    
    box = self.layout.box()
    box.label(text="Reference Images")
    box.prop(context.scene, "image_name1", text="Image1")
    box.prop(context.scene, "image_name2", text="Image2")
    box.prop(context.scene, "image_name3", text="Image3")

    self.layout.operator("composit_pil.send")

def register():
    bpy.types.Scene.output_path = bpy.props.StringProperty(name="output path", default="//")
    bpy.types.Scene.image_name1 = bpy.props.StringProperty(name="image name", default="//")
    bpy.types.Scene.image_name2 = bpy.props.StringProperty(name="image name", default="//")
    bpy.types.Scene.image_name3 = bpy.props.StringProperty(name="image name", default="//")

def unregister():
    pass

