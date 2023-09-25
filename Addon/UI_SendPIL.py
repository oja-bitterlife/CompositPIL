import bpy
import requests

class COMPOSIT_PIL_OT_send(bpy.types.Operator):
    bl_idname = "composit_pil.send"
    bl_label = "Send"

    def execute(self, context):
        response = requests.get("https://www.google.co.jp")
        print(response)
        return{'FINISHED'}

def draw(self, context):
    self.layout.operator("composit_pil.send")

def register():
    pass

def unregister():
    pass

