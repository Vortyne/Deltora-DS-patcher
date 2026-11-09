"""SCR0 script parser/disassembler."""
import struct, sys, glob, collections
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def recs(b):
    """header: +8 nfunc, +a nimport, +c funcs tbl, +10 imports tbl"""
    nf,ni=u16(b,8),u16(b,10)
    ft,it=u32(b,0x0c),u32(b,0x10)
    F=[u32(b,ft+4*i) for i in range(nf)]
    I=[u32(b,it+4*i) for i in range(ni)]
    return F,I
def rec(b,o):
    name=b[o+0x20:b.index(b'\0',o+0x20)].decode('latin1')
    ty=[];p=o+u32(b,o+8)
    while u16(b,p)!=0xffff: ty.append(u16(b,p));p+=2
    return dict(off=o,name=name,types=ty,code=o+u32(b,o+12),n=u32(b,o+16))
def walk(b,r):
    p=r['code'];e=p+r['n']*2
    while p<e:
        w=u16(b,p);a=p
        hi=w&0xf000
        if hi==0x4000:
            t=w&7
            sz={0:1,1:1,2:2,3:4,4:2,5:None}[t]
            if t==0: v=struct.unpack_from('<b',b,p+2)[0]
            elif t==1: v=struct.unpack_from('<h',b,p+2)[0]
            elif t==2: v=struct.unpack_from('<i',b,p+2)[0]
            elif t==3: v=struct.unpack_from('<q',b,p+2)[0]
            elif t==4: v=struct.unpack_from('<f',b,p+2)[0]
            else:
                n=u16(b,p+2); raw=b[p+4:p+4+n]; v=raw; sz=1+(n+1)//2
            yield a,('push',w,v);p+=2+sz*2
        elif hi==0x6000:
            n=2 if (w&0x18)!=0x10 else 4
            yield a,('var',w,b[p+2:p+n*2].hex());p+=n*2
        elif hi==0x2000:
            yield a,('call',w,u16(b,p+2));p+=4
        else:
            yield a,('op',w,None);p+=2
    yield p,('end',0,e-p)
