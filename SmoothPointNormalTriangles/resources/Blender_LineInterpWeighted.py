import bpy
import numpy as np

for item in bpy.data.meshes:
    bpy.data.meshes.remove(item)
for item in bpy.data.materials:
    bpy.data.materials.remove(item)


def normalize(v):
    return v / np.sqrt(np.sum(v**2)) # np.linalg.norm()


def Bezier3Corner(Ps, at):
    return Ps[at]
def Bezier3Edge(Ps,Ns,Ws, near,far):
    return Ps[near] + 1/2 * Ws[near] * (Ps[far]-Ps[near] -Ns[near]*np.dot(Ps[far]-Ps[near], Ns[near]))

def B3P(Ps,ts, at):
    return Bezier3Corner(Ps, at) * ts[at]**3
def B3E(Ps,Ns,Ws,ts, near,far):
    return Bezier3Edge(Ps,Ns,Ws, near,far) * ts[near]**2 * ts[far]

def PNLine(Ps,Ns,Ws, t):
    ts = [t, 1-t]
    return (
            +B3P(Ps,ts, 0) +B3P(Ps,ts, 1)
            +3*(
                +B3E(Ps,Ns,Ws,ts, 0,1) +B3E(Ps,Ns,Ws,ts, 1,0)
            )
        )

def dPNLine_dt(Ps,Ns,Ws,t):
    return (
            +Bezier3Corner(Ps, 0) *3 *t**2
            +Bezier3Corner(Ps, 1) *3 *(1-t)**2 *(-1)
            +3*Bezier3Edge(Ps,Ns,Ws, 0, 1) *( 2*t*(1-t) + t**2*(-1) )
            +3*Bezier3Edge(Ps,Ns,Ws, 1, 0) *( (1-t)**2 + t*2*(1-t)*(-1) )
        )

def PNLineNt(Ps,Ns,Ws, t):
    ts = [t, 1-t]
    Pt = PNLine(Ps,Ns,Ws, t)
    Pnt = PNLine([Ps[0]+Ns[0], Ps[1]+Ns[1]],Ns,Ws, t)
    dPt_dt = dPNLine_dt(Ps,Ns,Ws, t)
    u_dPt_dt = normalize(dPt_dt)
    Vn = Pnt - Pt
    SNt = Vn - u_dPt_dt * np.dot(Vn, u_dPt_dt)
    return normalize(SNt)

def PNLineWt(Ps,Ns,Ws, t):
    ts = [t, 1-t]
    return Ws[0]*ts[0] + Ws[1]*ts[1]

def PNLineVals(Ps,Ns,Ws, t):
    return [PNLine(Ps,Ns,Ws,t), PNLineNt(Ps,Ns,Ws,t), PNLineWt(Ps,Ns,Ws,t)]


def PNLineInterpTriangle(Ps,Ns,Ws, ts):
    L1 = PNLineVals([Ps[0],Ps[1]], [Ns[0],Ns[1]], [Ws[0],Ws[1]], ts[0])
    L2 = PNLineVals([Ps[0],Ps[2]], [Ns[0],Ns[2]], [Ws[0],Ws[2]], ts[0])
    return PNLine([L1[0],L2[0]], [L1[1],L2[1]], [L1[2],L2[2]], ts[1])



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

W0 = 1
W1 = 0.5
W2 = 0.01
W3 = 1
W4 = 2/3


def tesselatePNLITriangle(Ps,Ns,Ws):
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
            vertices.append( PNLineInterpTriangle(Ps,Ns,Ws,ts).tolist() )
            if (0 < j):
                faces.append([vertUpperRight-1, vertId-1, vertId])  # left
            if (0 < j and j < l):
                faces.append([vertUpperRight-1, vertId, vertUpperRight])  # up
    return [vertices, faces]


B3PNTriangles = [
         tesselatePNLITriangle([P0,P1,P2],[N0,N1,N2],[W0,W1,W2]),
         tesselatePNLITriangle([P0,P2,P3],[N0,N2,N3],[W0,W2,W3]),
         tesselatePNLITriangle([P0,P3,P4],[N0,N3,N4],[W0,W3,W4]),
         tesselatePNLITriangle([P0,P4,P1],[N0,N4,N1],[W0,W4,W1])
    ]


for i in range(4):
    mesh = bpy.data.meshes.new('tri'+str(i))
    mesh.from_pydata(B3PNTriangles[i][0], [], B3PNTriangles[i][1])
    obj = bpy.data.objects.new('tri'+str(i), mesh)
    bpy.context.scene.collection.objects.link(obj)
