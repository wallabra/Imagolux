import omg
import glob
import sys
import io
import numpy as np
import os

from struct import pack as spack
from PIL import Image, ImagePalette


ZDOOM = bool(os.environ.get("ZDOOM", "").strip(' ').upper() == "Y")
ANIM = bool(os.environ.get("ANIM", "").strip(' ').upper() == "Y")


def flatten(key):
    return "F" + key[1:]

def make_patch(image):
    res = spack("2H2h", *imr.size, 0, 0)
    cols = []
    
    for x in range(imr.size[0]):
        res += spack("I", 8 + imr.size[0] * 4 + (3 + imr.size[1]) * len(cols))
        col = spack("3B", 0, image.size[1], 0)
        i = image.crop((x, 0, x + 1, imr.size[1]))
        col += i.tobytes()
        cols.append(col)
    
    return res + b''.join(cols)

if __name__ == "__main__":
    texnames = sys.argv[3:]   
    outwad = omg.WAD()
    pal = ImagePalette.ImagePalette("RGB", bytearray(omg.WAD(from_file=sys.argv[1]).data["PLAYPAL"].data[:768]))
    texture1 = []
    pnames = []
    i = 0
    
    print(":: ImagoLux :: Limit-Removing Colored Lighting ::")
    print("(c)2018 Gustavo R. Rehermann. Code: MIT License. Media:")
    print("CC0 if owned by Gustavo, respective owners otherwise.")
    print()
    
    if ZDOOM:
        print("Exporting ZDoom-style textures.")
    
    else:
        print("Exporting limit-removing TEXTUREx/PNAMES.")
    
    for g in texnames:
        for texname in glob.glob(g):
            sys.stdout.write("\rColoring texture '{}'...                 ".format(texname))
        
            im = Image.open(texname)
            im = im.convert("RGB")
            
            if texname.lower().endswith(".png"):
                texname = texname[:-4]
            
            for r_ in range(10):
                r = r_ / 9
                
                for g_ in range(10):
                    g = g_ / 9
                    
                    for b_ in range(10):
                        b = b_ / 9
                        col = (r_, g_, b_)
                        rcol = (r, g, b)
                        icol = tuple(map(int, (r * 255, g * 255, b * 255)))
                        
                        a = np.linalg.norm(np.array(list(map(lambda x: abs(x - 5 / 9) * 2, rcol))))
                        
                        tt = "{}{}{}{}".format(texname[-5:], *col).upper()
                        tp = "P{}{}{}{}".format(texname[-4:], *col).upper()
                        tf = "F{}{}{}{}".format(texname[-4:], *col).upper()
                        
                        im2 = Image.new("RGB", im.size, icol)
                            
                        # print(col, a)
                        imr = Image.blend(im, im2, a)
                        
                        if ZDOOM:
                            with io.BytesIO() as out:
                                imr.convert("P", palette=pal, dither=Image.NONE).save(out, format="PNG")
                                png = out.getvalue()
                                outwad.ztextures[tt] = omg.Lump(png)
                        
                        else:
                            outwad.patches[tp] = omg.Lump(make_patch(imr.convert("P", palette=pal, dither=Image.NONE)))
                            
                        outwad.flats[tf] = omg.Lump(imr.resize((64, 64)).convert("P", palette=pal, dither=Image.NONE).tobytes())
                        
                        if not ZDOOM:
                            pnames.append(spack("{}s{}c".format(len(tp), max(0, 8 - len(tp))), tp[:8].encode('utf-8'), *[0 for _ in range(max(0, 8 - len(tp)))]))
                            texture1.append(spack("=8sH2BhHI6h", tt.encode('utf-8'), 0, 8, 8, *imr.size, 0, 1, 0, 0, i, 0, 0))
                        
                        i += 1
         
    if ANIM:
        if ZDOOM:
            print("\nCreating ANIMDEFS for color/light oscillations...")
            
            animations = {}
            
            for g in texnames:
                for texname in glob.glob(g):
                    if texname.lower().endswith(".png"):
                        texname = texname[:-4]
                        
                    texname = texname.upper()
                        
                    tr = "{}RED".format(texname[-5:])
                    tg = "{}GRN".format(texname[-5:])
                    tb = "{}BLU".format(texname[-5:])
                    tw = "{}WHT".format(texname[-5:])
                    td = "{}WHD".format(texname[-5:])
                    ty = "{}YEL".format(texname[-5:])
                    tp = "{}PRP".format(texname[-5:])
                    to = "{}ORG".format(texname[-5:])
                        
                    for tkey in (tr, tg, tb, tw, td, ty, tp, to):
                        animations[tkey] = []
                        
                        outwad.flats[flatten(tkey)] = omg.Lump(Image.new("L", (64, 64), 40).tobytes())
                        
                        with io.BytesIO() as out:
                            Image.new("L", (2, 2), 80).save(out, format="PNG")
                            png = out.getvalue()
                            outwad.ztextures[tkey] = omg.Lump(png)
                        
                    for r in range(10):
                        animations[tr].append("{}{}55".replace("5", str(int(min(5, r / 2 + 2)))).format(texname[-5:], r))
                        
                    for g in range(10):
                        animations[tg].append("{}5{}5".replace("5", str(int(min(5, g / 2 + 2)))).format(texname[-5:], g))
                        
                    for b in range(10):
                        animations[tb].append("{}55{}".replace("5", str(int(min(5, b / 2 + 2)))).format(texname[-5:], b))
                        
                    for a in range(10):
                        animations[ty].append("{0}{1}{1}5".replace("5", str(int(min(5, a / 2 + 2)))).format(texname[-5:], a))
                        
                    for a in range(10):
                        animations[tp].append("{0}{1}5{1}".replace("5", str(int(min(5, a / 2 + 2)))).format(texname[-5:], a))
                        
                    for a in range(10):
                        animations[to].append("{}{}{}5".replace("5", str(int(min(5, a / 2 + 2)))).format(texname[-5:], a, int(a / 2)))
                        
                    for w in range(3, 10):
                        animations[tw].append("{0}{1}{1}{1}".format(texname[-5:], w))
                        
                    for w in range(6):
                        animations[td].append("{0}{1}{1}{1}".format(texname[-5:], w))
                        
            res = []
            
            for k, v in animations.items():
                res.append("TEXTURE {}".format(k))
                res.append("    ALLOWDECALS")
                
                for frame in v:
                    res.append("    PIC {} tics 4".format(frame))
                   
                res.append("    OSCILLATE")
                res.append("")
                
                res.append("FLAT {}".format(flatten(k)))
                res.append("    ALLOWDECALS")
                
                for frame in v:
                    res.append("    PIC {} tics 4".format(flatten(frame)))
                    
                res.append("    OSCILLATE")
                res.append("")
            
            outwad.data["ANIMDEFS"] = omg.Lump("\n".join(res[:-1]).encode('utf-8'))
            print("Exporting...")
            
        else:
            print()
            print("ANIMDEFS only works within ZDoom-based ! Set the environment")
            print("variable 'ZDOOM' to 'Y'.")
            print()
            print("Windows:")
            print("    SET \"ZDOOM=Y\"")
            print()
            print("Unix:")
            print("    ZDOOM=Y")
            exit(1)
         
    else:
        print("\nExporting...")
                
    if not ZDOOM:
        outwad.data['PNAMES'] = omg.Lump(spack('i', len(pnames)) + b''.join(pnames))
        outwad.data['TEXTURE1'] = omg.Lump(spack('i{}I'.format(len(texture1)), len(texture1), *tuple(range(4 + len(texture1) * 4, 4 + len(texture1) * 4 + 32 * len(texture1), 32))) + b''.join(texture1))
    
    outwad.to_file(sys.argv[2])
    
    print("Done!")