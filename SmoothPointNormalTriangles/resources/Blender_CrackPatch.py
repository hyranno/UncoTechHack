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

def CrackPatch(Ps, Ns0,Ws0, Ns1,Ws1, ts):
    L1 = PNLineVals([Ps[0],Ps[1]], [Ns0[0],Ns0[1]], [Ws0[0],Ws0[1]], ts[0])
    L2 = PNLineVals([Ps[0],Ps[1]], [Ns1[0],Ns1[1]], [Ws1[0],Ws1[1]], ts[0])
    return ts[1]*L1[0] + (1-ts[1])*L2[0]



P1 = np.array([+1,+1,0])
P2 = np.array([+1,-1,0])
P3 = np.array([-1,-1,0])
P4 = np.array([-1,+1,0])

P1u = np.array([+np.sqrt(2),0,1])
P2u = np.array([0,-np.sqrt(2),1])
P3u = np.array([-np.sqrt(2),0,1])
P4u = np.array([0,+np.sqrt(2),1])

N1 = normalize(P1)
N2 = normalize(P2)
N3 = normalize(P3)
N4 = normalize(P4)

N1u = np.array([+1,0,0])
N2u = np.array([0,-1,0])
N3u = np.array([-1,0,0])
N4u = np.array([0,+1,0])
Nd = np.array([0,0,-1])

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

def tesselateCrackPatch(Ps, Ns0,Ws0, Ns1,Ws1):
    numstep = 50
    vertices = []
    faces = []
    for i in range(numstep+1):
        vertices.append( CrackPatch(Ps, Ns0,Ws0, Ns1,Ws1, [i/numstep,0]).tolist() )
        if (1 < i):
            lastv = len(vertices)-1
            faces.append([lastv-2, lastv-1, lastv])
        if (0 < i and i < numstep):
            vertices.append( CrackPatch(Ps, Ns0,Ws0, Ns1,Ws1, [i/numstep,1]).tolist() )
            lastv = len(vertices)-1
            faces.append([lastv, lastv-1, lastv-2])
    return [vertices, faces]

meshes = [
         tesselatePNLITriangle([P1,P1u,P2],[N1,N1u,N2],[1,1,1]),
         tesselatePNLITriangle([P1u,P2,P2u],[N1u,N2,N2u],[1,1,1]),
         tesselatePNLITriangle([P2,P2u,P3],[N2,N2u,N3],[1,1,1]),
         tesselatePNLITriangle([P2u,P3,P3u],[N2u,N3,N3u],[1,1,1]),
         tesselatePNLITriangle([P3,P3u,P4],[N3,N3u,N4],[1,1,1]),
         tesselatePNLITriangle([P3u,P4,P4u],[N3u,N4,N4u],[1,1,1]),
         tesselatePNLITriangle([P4,P4u,P1],[N4,N4u,N1],[1,1,1]),
         tesselatePNLITriangle([P4u,P1,P1u],[N4u,N1,N1u],[1,1,1]),
         tesselatePNLITriangle([P1,P2,P4],[Nd,Nd,Nd],[0,0,0]),
         tesselatePNLITriangle([P3,P4,P2],[Nd,Nd,Nd],[0,0,0]),
         tesselateCrackPatch([P1,P2], [N1,N2],[1,1], [Nd,Nd],[0,0]),
         tesselateCrackPatch([P2,P3], [N2,N3],[1,1], [Nd,Nd],[0,0]),
         tesselateCrackPatch([P3,P4], [N3,N4],[1,1], [Nd,Nd],[0,0]),
         tesselateCrackPatch([P4,P1], [N4,N1],[1,1], [Nd,Nd],[0,0])
    ]


for i in range(14):
    mesh = bpy.data.meshes.new('tri'+str(i))
    mesh.from_pydata(meshes[i][0], [], meshes[i][1])
    obj = bpy.data.objects.new('tri'+str(i), mesh)
    bpy.context.scene.collection.objects.link(obj)
