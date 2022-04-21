import os
import igl
import math
import numpy as np
import urllib.request

def rotation_matrix(axis, theta):
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

def quaternion_to_matrix(args):
    """
    Quaternion to matrix
    :param args:
    :return:
    """
    tx = args[0] + args[0]
    ty = args[1] + args[1]
    tz = args[2] + args[2]
    twx = tx * args[3]
    twy = ty * args[3]
    twz = tz * args[3]
    txx = tx * args[0]
    txy = ty * args[0]
    txz = tz * args[0]
    tyy = ty * args[1]
    tyz = tz * args[1]
    tzz = tz * args[2]

    result = np.zeros((3, 3))
    result[0, 0] = 1.0 - (tyy + tzz)
    result[0, 1] = txy - twz
    result[0, 2] = txz + twy
    result[1, 0] = txy + twz
    result[1, 1] = 1.0 - (txx + tzz)
    result[1, 2] = tyz - twx
    result[2, 0] = txz - twy
    result[2, 1] = tyz + twx
    result[2, 2] = 1.0 - (txx + tyy)
    return result

def vector_dot_matrix3(v, mat):
    rot_mat = np.mat(mat)
    vec = np.mat(v).T
    result = np.dot(rot_mat, vec)
    return np.array(result.T)[0]

def transform_v(v, instance):
    
    pos = instance.pos
    if hasattr(instance,'rotscale'):
        v = np.dot(v, np.array(instance.rotscale))
    else:
        rot = instance.rot
        scale = instance.scale
        v = v.astype(np.float64) * scale
        rotMatrix = quaternion_to_matrix(rot)
        R = np.array(rotMatrix)
        v = np.transpose(v)
        v = np.matmul(R, v)
        v = np.transpose(v)
    v = v + pos
    return v

def read_mesh_attr(mesh):
    v = mesh.xyz
    faces = mesh.faces
    vt = None
    mat = None
    if mesh.uv is not None:
        vt = mesh.uv
        if mesh.material is not None:
            mat = mesh.material
            if mat.UVTransform is not None:
                vt = mat.UVTransform[:2,:2] @ vt.T
                vt = vt.T
    return v,faces,vt, mat
def quadrilateral2triangle(filepath):

    dir_path = os.path.dirname(filepath)

    objpath = os.path.join(dir_path, 'raw_model.obj')
    tri_obj = os.path.join(dir_path, 'raw_model_tri.obj')

    fid_obj = open(objpath, 'r', encoding='utf-8',errors='ignore')
    fid_tri_obj = open(tri_obj, 'w', encoding='utf-8')
    alllines = fid_obj.readlines()

    for line in alllines:
        if line.startswith('f  '):
            tri = line.split('  ')[1].split(' ')
            tri = [t for t in tri if t != '\n']
        elif line.startswith('f '):
            tri = line.split(' ')[1:]
            tri = [t for t in tri if t != '\n']
        if (line.startswith('f ') or line.startswith('f  ')) and len(tri) >= 4:
            fid_tri_obj.write('f ' + tri[0] + ' ' + tri[1] + ' ' + tri[2] + '\n')
            fid_tri_obj.write('f ' + tri[0] + ' ' + tri[2] + ' ' + tri[3] + '\n')
        else:
            fid_tri_obj.write(line)
    fid_obj.close()
    fid_tri_obj.close()

def save_obj(ori_obj_path, savepath, v, model_id):

    obj_dir_path = os.path.dirname(ori_obj_path)
    save_dir = os.path.dirname(savepath)

    objpath = ori_obj_path
    tri_obj = savepath

    fid_obj = open(objpath, 'r', encoding='utf-8',errors='ignore')
    fid_save_obj = open(tri_obj, 'w', encoding='utf-8')
    alllines = fid_obj.readlines()
    idx = 0
    for line in alllines:
        if line.startswith('mtllib model.mtl'):
            line = 'mtllib ' + model_id + '.mtl\n'
        if (line.startswith('v ') or line.startswith('v  ')):
            fid_save_obj.write('v ' + str(v[idx][0]) + ' ' + str(v[idx][1]) + ' ' + str(v[idx][2]) + '\n')
            idx = idx + 1
        else:
            fid_save_obj.write(line)

    fid_obj.close()
    fid_save_obj.close()


    if os.path.exists(save_dir+'/'+model_id+'.mtl'):
        return


    fid_obj = open(obj_dir_path+'/model.mtl', 'r', encoding='utf-8',errors='ignore')
    fid_save_obj = open(save_dir+'/'+model_id+'.mtl', 'w', encoding='utf-8')
    alllines = fid_obj.readlines()
    idx = 0
    for line in alllines:
        line = line.replace('./texture.png', obj_dir_path.replace('\\','/')+'/texture.png')
        fid_save_obj.write(line)

    fid_obj.close()
    fid_save_obj.close()


def read_obj(filepath):
    if not os.path.exists(filepath):
        quadrilateral2triangle(filepath)
    v, vt, _, faces, ftc, _ = igl.read_obj(filepath)
    return v


def save_mesh(savepath, filename, *args):
    fid = open(savepath+'/'+str(filename)+'.obj', "w")

    mtl_fid = open(savepath+'/'+str(filename)+'.mtl', "w")
    fid.write('mtllib '+str(filename)+'.mtl\n')
    v_id = 1
    vt_id = 1
    for mesh in args:
        mesh_id, v, faces, vt, texture = mesh
        
        for vi in v:
            fid.write('v %f %f %f\n' % (vi[0], vi[1], vi[2]))
        if type(texture) != list:
            for vti in vt:
                fid.write('vt %f %f\n' % (vti[0], vti[1]))
            
        
        mtl_fid.write('newmtl '+str(mesh_id)+'\n')
        if type(texture) == list:
            mtl_fid.write('Kd '+str(texture[0]/255.)+' '+str(texture[1]/255.)+' '+str(texture[2]/255.)+'\n')
        else:
            mtl_fid.write('map_Kd '+texture+'\n')
        fid.write('usemtl '+str(mesh_id)+'\n')
        for f in faces:
            if type(texture) == list:
                fid.write('f %d %d %d\n' % (f[0]+v_id,f[1]+v_id,f[2]+v_id))
            else:
                fid.write('f %d/%d %d/%d %d/%d\n' % (f[0]+v_id,f[0]+vt_id,f[1]+v_id,f[1]+vt_id,f[2]+v_id,f[2]+vt_id))
        if type(texture) != list:
            vt_id = vt_id + vt.shape[0]
        v_id = v_id + v.shape[0]
    fid.close()
    mtl_fid.close()

def read_mesh(mesh, meshes, material, save_path, floor_path, fid_error):
    for constructid, all_mesh in mesh.items():
        output = []
        mesh_type = 'walls'
        for uid in all_mesh:
            v, faces, vt, mat = read_mesh_attr(meshes[uid], material)
            texture = None
            if vt is not None and mat is not None:
                if mat.texture != '':
                    if not os.path.exists(floor_path+'/' + mat.jid):
                        os.mkdir(floor_path+'/' + mat.jid)
                        try:
                            urllib.request.urlretrieve(mat.texture,floor_path+'/' + mat.jid +'/texture.png')
                        except:
                            fid_error.write(meshes[uid].room_id + ': load '+ mat.texture +' texture failed\n')

                    texture = floor_path+'/' + mat.jid + '/texture.png'
            output.append([meshes[uid].instanceid, v,faces,vt,texture])
        
        save_mesh(save_path, mesh_type+'_'+constructid, *output)
