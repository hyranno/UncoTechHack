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

def B3P(Ps,Ns,ts, at):
    return Bezier3Corner(Ps,Ns, at) * ts[at]**3
def B3E(Ps,Ns,ts, near,far):
    return Bezier3Edge(Ps,Ns, near, far) * ts[near]**2 * ts[far]

def PNLine(Ps,Ns, t):
    ts = [t, 1-t]
    return (
            +B3P(Ps,Ns,ts, 0) +B3P(Ps,Ns,ts, 1)
            +3*(
                +B3E(Ps,Ns,ts, 0,1) +B3E(Ps,Ns,ts, 1,0)
            )
        )

def dPNLine_dt(Ps,Ns,t):
    return (
            +Bezier3Corner(Ps,Ns, 0) *3 *t**2
            +Bezier3Corner(Ps,Ns, 1) *3 *(1-t)**2 *(-1)
            +3*Bezier3Edge(Ps,Ns, 0, 1) *( 2*t*(1-t) + t**2*(-1) )
            +3*Bezier3Edge(Ps,Ns, 1, 0) *( (1-t)**2 + t*2*(1-t)*(-1) )
        )

def PNLineNt(Ps,Ns, t):
    ts = [t, 1-t]
    Pt = PNLine(Ps,Ns, t)
    Pnt = PNLine([Ps[0]+Ns[0], Ps[1]+Ns[1]],Ns, t)
    dPt_dt = dPNLine_dt(Ps,Ns, t)
    u_dPt_dt = normalize(dPt_dt)
    Vn = Pnt - Pt
    SNt = Vn - u_dPt_dt * np.dot(Vn, u_dPt_dt)
    return normalize(SNt)

def PNLineInterpTriangle(Ps,Ns,ts):
    Pl1 = PNLine([Ps[0],Ps[1]], [Ns[0],Ns[1]], ts[0])
    Nl1 = PNLineNt([Ps[0],Ps[1]], [Ns[0],Ns[1]], ts[0])
    Pl2 = PNLine([Ps[0],Ps[2]], [Ns[0],Ns[2]], ts[0])
    Nl2 = PNLineNt([Ps[0],Ps[2]], [Ns[0],Ns[2]], ts[0])
    return PNLine([Pl1,Pl2], [Nl1,Nl2], ts[1])



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


def tesselatePNLITriangle(Ps,Ns):
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
            if (0 < l) :
                ts = [i/numstep, j/l]
            else :
                ts = [i/numstep, j]
            vertices.append( PNLineInterpTriangle(Ps,Ns,ts).tolist() )
            if (0 < j):
                faces.append([vertUpperRight-1, vertId-1, vertId])  # left
            if (0 < j and j < l):
                faces.append([vertUpperRight-1, vertId, vertUpperRight])  # up
    return [vertices, faces]


B3PNTriangles = [
         tesselatePNLITriangle([P0,P1,P2],[N0,N1,N2]),
         tesselatePNLITriangle([P0,P2,P3],[N0,N2,N3]),
         tesselatePNLITriangle([P0,P3,P4],[N0,N3,N4]),
         tesselatePNLITriangle([P0,P4,P1],[N0,N4,N1])
    ]


for i in range(4):
    mesh = bpy.data.meshes.new('tri'+str(i))
    mesh.from_pydata(B3PNTriangles[i][0], [], B3PNTriangles[i][1])
    obj = bpy.data.objects.new('tri'+str(i), mesh)
    bpy.context.scene.collection.objects.link(obj)
