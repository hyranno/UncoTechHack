import bpy
import numpy as np

for item in bpy.data.meshes:
    bpy.data.meshes.remove(item)
for item in bpy.data.materials:
    bpy.data.materials.remove(item)


def normalize(v):
    return v / np.sqrt(np.sum(v**2)) # np.linalg.norm()


def Bezier3Corner(Ps,Ns, at):
    return Ps[at]
def Bezier3Edge(Ps,Ns, near,far):
    return 1/3 * ( 2*Ps[near] + Ps[far] -Ns[near] * np.dot(Ps[far]-Ps[near], Ns[near]) )
def Bezier3Center(Ps,Ns):
    E = 1/6 * (
            +Bezier3Edge(Ps,Ns, 0,1) +Bezier3Edge(Ps,Ns, 0,2)
            +Bezier3Edge(Ps,Ns, 1,0) +Bezier3Edge(Ps,Ns, 1,2)
            +Bezier3Edge(Ps,Ns, 2,0) +Bezier3Edge(Ps,Ns, 2,1)
        )
    V = 1/3 * (
          +Bezier3Corner(Ps,Ns, 0)
          +Bezier3Corner(Ps,Ns, 1)
          +Bezier3Corner(Ps,Ns, 2)
        )
    return E + 1/2 * (E-V)

def B3P(Ps,Ns,ts, at):
    return Bezier3Corner(Ps,Ns, at) * ts[at]**3
def B3E(Ps,Ns,ts, near,far):
    return Bezier3Edge(Ps,Ns, near, far) * ts[near]**2 * ts[far]
def B3C(Ps,Ns,ts):
    return Bezier3Center(Ps,Ns) *ts[0]*ts[1]*ts[2]

def Bezier3PNTriangle(Ps,Ns,ts):
    return (
            +(B3P(Ps,Ns,ts,0) +B3P(Ps,Ns,ts,1) +B3P(Ps,Ns,ts,2))
            +3 * (
                +B3E(Ps,Ns,ts, 0,1) +B3E(Ps,Ns,ts, 0,2)
                +B3E(Ps,Ns,ts, 1,0) +B3E(Ps,Ns,ts, 1,2)
                +B3E(Ps,Ns,ts, 2,0) +B3E(Ps,Ns,ts, 2,1)
            )
            +6 * B3C(Ps,Ns,ts)
        )

P0 = np.array([0, 0, np.sqrt(2)])
P1 = np.array([+1,+1,0])
P2 = np.array([+1,-1,0])
P3 = np.array([-1,-1,0])
P4 = np.array([-1,+1,0])

N0 = normalize(P0)
N1 = normalize(P1)
N2 = normalize(P2)
N3 = normalize(P3)
N4 = normalize(P4)


def tesselateB3PNTriangle(Ps,Ns):
    numstep = 50
    vertices = []
    faces = []
    for i in reversed(range(numstep+1)):
        for j in range(numstep+1-i):
            l = numstep-i
            prevLineLen = l
            vertLine = int(l*(l+1)/2)
            vertId = vertLine +j
            vertUpperRight = vertId - prevLineLen
            ts = [i/numstep, j/numstep, 1 -i/numstep -j/numstep]
            vertices.append( Bezier3PNTriangle(Ps,Ns,ts).tolist() )
            if (0 < j):
                faces.append([vertUpperRight-1, vertId-1, vertId])  # left
            if (0 < j and j < l):
                faces.append([vertUpperRight-1, vertId, vertUpperRight])  # up
    return [vertices, faces]


B3PNTriangles = [
         tesselateB3PNTriangle([P0,P1,P2],[N0,N1,N2]),
         tesselateB3PNTriangle([P0,P2,P3],[N0,N2,N3]),
         tesselateB3PNTriangle([P0,P3,P4],[N0,N3,N4]),
         tesselateB3PNTriangle([P0,P4,P1],[N0,N4,N1])
    ]


for i in range(4):
    mesh = bpy.data.meshes.new('tri'+str(i))
    mesh.from_pydata(B3PNTriangles[i][0], [], B3PNTriangles[i][1])
    obj = bpy.data.objects.new('tri'+str(i), mesh)
    bpy.context.scene.collection.objects.link(obj)
