# This script is able to convert models into a spiral by using raycasting to project points onto the surface of objects. This also means that it handles concave surfaces in the Z direction very poorly. I might fix this in the future and or include being able to use bezier curves to direct the spiral.

import bpy
import math
import mathutils

# https://blender.stackexchange.com/questions/6173/where-does-console-output-go
def print(data):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'CONSOLE':
                override = {'window': window, 'screen': screen, 'area': area}
                bpy.ops.console.scrollback_append(override, text=str(data), type="OUTPUT")       
# https://blender.stackexchange.com/questions/269821/detect-if-a-mesh-surface-is-hit-by-a-light-or-not
def ray_cast(fr,to):
    is_hit, pos, _, face_index, obj, _ = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, fr, to-fr)
    if is_hit:
        return pos
    else:
        return -1
    
selected = bpy.context.selected_objects[0]

heightPerTurn = 0.25
pointsPerTurn = 256
turns = 128
radius = 15
offset = 0
heightThick = 0.18
widthThick = 0.4

includeTopLayer = False

points = []
edges = []

vertices = []

anglePerTurn = 2*math.pi / pointsPerTurn;

heightPerPoint = heightPerTurn / pointsPerTurn;

highestPoint = 0

for j in range(pointsPerTurn):
    points.append((radius * math.cos(anglePerTurn * j), radius * math.sin(anglePerTurn * j),0))


for i in range(turns):
    for j in range(pointsPerTurn):
        points.append((radius * math.cos(anglePerTurn * j), radius * math.sin(anglePerTurn * j),heightPerTurn * i + heightPerPoint * j))

for point in points:
    res = ray_cast(mathutils.Vector(point),mathutils.Vector((selected.location[0],selected.location[1],point[2])))
    
    if res != -1:
        vertices.append(res)
        highestPoint = point[2]
        
topPoints = []        

for i in range(turns):
    for j in range(pointsPerTurn):
        topPoints.append((radius * math.cos(anglePerTurn * j), radius * math.sin(anglePerTurn * j),highestPoint))

if includeTopLayer:
    for point in topPoints:
        res = ray_cast(mathutils.Vector(point),mathutils.Vector((selected.location[0],selected.location[1],point[2])))
        if res != -1:
            vertices.append(res)
        
for i in range(len(vertices)-1):
    edges.append((i,i+1))

me = bpy.data.meshes.new("Mesh")

me.from_pydata(vertices, edges, [])

ob = bpy.data.objects.new("Spiral", me)

bpy.context.collection.objects.link(ob)

ob.location = ob.location + mathutils.Vector((radius,0,0))

selected.select_set(False)
ob.select_set(True)

bpy.context.view_layer.objects.active = ob

screw = ob.modifiers.new(name="Screw",type='SCREW')
solid = ob.modifiers.new(name="Solidify",type='SOLIDIFY')

screw.angle = 0.01*math.pi/180
screw.screw_offset = heightThick
solid.thickness = widthThick

