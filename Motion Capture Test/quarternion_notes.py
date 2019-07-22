#quarternion will be a tuple/array in the order of x,y,z,w

"""
example data:
0.05794358253479004 -0.25065937638282776 -0.083066910502948 -0.9627629518508911

Euler (in XYZ order for matrix):
angle:
x: -10.0146766, y: 28.230812, z: 12.3869013
radians:
x: -0.1747891, y: 0.4927206, z: 0.2161922

Axis angle:
x: 0.2143301, y: -0.9271752, z: -0.3072599, angle: 328.6301278 radians: 5.7356778

Matrix
0.8605396, -0.1889957,  0.4730246
0.1308993,  0.9794849,  0.1532148
-0.4922774, -0.0699289,  0.8676249

While Axis angle could work for a 2D example, it is only transforming the rotation from world to
local which is not useful in 3D space. Instead, rotation around the local y-axis would be better
to maintain consistent angels in 3D space

"""

import math

#returns axis followed by angle (angel in radians)
def quaternion_to_axis_angle(q):
    mul=1.0/math.sqrt(1-q[3]*q[3])
    return [q[0]*mul, q[1]*mul, q[2]*mul, math.acos(q[3])*2.0]

#matrix order YZX
def quaternion_to_eulerYZX(q):
    test = q[0]*q[1] + q[2]*q[3]
    #singularity at north pole
    if(test>0.499):
        return [2.0*math.atan2(q[0], q[3]), math.pi/2.0,0.0]
    if(test<-0.499):
        return [-2.0*math.atan2(q[0], q[3]), -math.pi/2.0,0.0]

    return [math.atan2(2*q[1]*q[3] - 2*q[0]*q[2], 1 - 2*q[1]*q[1] - 2*q[2]*q[2]),
            math.asin(2*q[0]*q[1] + 2*q[2]*q[3]),
            math.atan2(2*q[0]*q[3] - 2*q[1]*q[2], 1 - 2*q[0]*q[0] - 2*q[2]*q[2])]

def axis_angle_to_matrix(aa):
    c = math.cos(aa[3])
    s = math.sin(aa[3])
    t = 1 - c
    return [[t*aa[0]*aa[0] + c, t*aa[0]*aa[1] - aa[2]*s, t*aa[0]*aa[2] + aa[1]*s],
            [t*aa[0]*aa[1] + aa[2]*s, t*aa[1]*aa[1] + c, t*aa[1]*aa[2] - aa[0]*s],
            [t*aa[0]*aa[2] - aa[1]*s, t*aa[1]*aa[2] + aa[0]*s, t*aa[2]*aa[2] + c]]

def quarternion_to_matrix(q):
    return axis_angle_to_matrix(quaternion_to_axis_angle(q))

def mag(v):
    return math.sqrt(dot(v,v))

def dot(v1,v2):
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def cross(v1,v2):
    return [v1]

# assume that y is approximately in the vertical direction (0,1,0)
def lazy_angle(q):
    mat=quarternion_to_matrix(q)
    x_vec = (mat[0][0],mat[1][0],mat[2][0])
    return math.atan2(x_vec[2], x_vec[0])

q=[0.05794358253479004, -0.25065937638282776, -0.083066910502948, -0.9627629518508911]
print(q)
print(quaternion_to_axis_angle(q))
print(quaternion_to_eulerYZX(q))
print(quarternion_to_matrix(q))
print(lazy_angle(q))




















# Ignore: Old Quaternion Functions
def convert_quat_to_euler(self, q):
    # X
    sinr_cosp = +2.0 * (q[3] * q[0] + q[1] * q[2])
    cosr_cosp = +1.0 - 2.0 * (q[0] * q[0] + q[1] * q[1])
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # Y
    sinp = +2.0 * (q[3] * q[1] - q[2] * q[0])
    if (abs(sinp) >= 1):
        pitch = math.copysign(math.pi / 2, sinp)
    else:
        pitch = math.asin(sinp)

    # Z
    siny_cosp = +2.0 * (q[3] * q[2] + q[0] * q[1])
    cosy_cosp = +1.0 - 2.0 * (q[1] * q[1] + q[2] * q[2])
    yaw = math.atan2(siny_cosp, cosy_cosp)

    # return (roll*180/math.pi, pitch*180/math.pi, yaw*180/math.pi)
    return (roll, pitch, yaw)


def convert_quat_to_angle(self, q):
    mul = 1.0 / math.sqrt(1 - q[3] * q[3])
    return (2 * math.acos(q[3]) * 180 / math.pi, q[0] * mul, q[1] * mul, q[2] * mul)


def convert_euler_to_rotational(self, r):
    heading, attitude, bank = (r[0], r[1], r[2])
    ch = math.cos(heading);
    sh = math.sin(heading);
    ca = math.cos(attitude);
    sa = math.sin(attitude);
    cb = math.cos(bank);
    sb = math.sin(bank);

    m00 = ch * ca;
    m01 = sh * sb - ch * sa * cb;
    m02 = ch * sa * sb + sh * cb;
    m10 = sa;
    m11 = ca * cb;
    m12 = -ca * sb;
    m20 = -sh * ca;
    m21 = sh * sa * cb + ch * sb;
    m22 = -sh * sa * sb + ch * cb;

    return (m10, m11, m12)


def quaternion_to_euler(self, x, y, z, w):
    import math
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    X = math.degrees(math.atan2(t0, t1))

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    Y = math.degrees(math.asin(t2))

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    Z = math.degrees(math.atan2(t3, t4))

    return X, Y, Z