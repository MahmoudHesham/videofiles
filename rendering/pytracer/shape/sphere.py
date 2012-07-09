import math

from .core import PtCommon
from .core import PtShape
from .core import PtGeom
from .core import PtMath
from .core import PtTransform
import core.PtWorld as PtWorld

class sphere(PtShape.PtShape):
    def __init__(self,name=None):
        PtShape.PtShape.__init__(self,name=name)
        # add sphere parameters
        self.addParamFloat("radius",1.)
        self.addParamFloat("phiMax", 360.)
        self.addParamFloat("zmin", -1.)
        self.addParamFloat("zmax",  1.)
        

    def prepareValues(self):
        radius = self.params['radius'].value
        phiMax = self.params['phiMax'].value
        zmin   = self.params['zmin'].value
        zmax   = self.params['zmax'].value
        
        zmin   = PtCommon.clamp(zmin,-radius,radius)
        zmax   = PtCommon.clamp(zmax,-radius,radius)
        invRad = 1. / radius
        
        thetaMin = math.acos(PtCommon.clamp(zmin * invRad,-1., 1.))
        thetaMax = math.acos(PtCommon.clamp(zmax * invRad,-1., 1.))
        
        phiMax = math.radians(PtCommon.clamp(phiMax,0.,360.))
        # Save the values
        self.params["zmin"].setValue(zmin)
        self.params["zmax"].setValue(zmax)
        self.params["phiMax"].setValue(phiMax)
        
        self.prepare()


    def prepare(self):
        if self.prepared == False:
            self.prepared = True


    def bound(self):
        self.prepareValues()
        
        radius = self.params['radius'].value
        phiMax = self.params['phiMax'].value
        zmin   = self.params['zmin'].value
        zmax   = self.params['zmax'].value
         
        bb = PtGeom.PtBBox()
        bb.min.x = -radius
        bb.min.y = -radius
        bb.min.z = -radius
        bb.max.x = radius
        bb.max.y = radius
        bb.max.z = radius


    def intersectP(self,ray):
        radius = self.params['radius'].value
        zmin = self.params['zmin'].value
        zmax = self.params['zmax'].value
        phiMax=self.params['phiMax'].value
        pos = self.params['center'].value
        m = self.params['matrix'].value

        # transform for sphere matrix
        xf = PtTransform.PtTransform(m)
        # transform for sphere center
        xpoint = PtTransform.PiTranslate(pos)
        # multiply transforms
        xf *= xpoint
        # get a local ray
        ray.transform(xf)

        A = ray.d.x*ray.d.x + ray.d.y*ray.d.y + ray.d.z * ray.d.z
        B = 2 * (ray.d.x*ray.o.x + ray.d.y*ray.o.y + ray.d.z*ray.o.z)
        C = ray.o.x*ray.o.x + ray.o.y*ray.o.y + ray.o.z*ray.o.z - radius*radius
        
        hit, t0, t1 = PtMath.quadratic(A,B,C)
        if not hit:
            return False
        #  Compute intersection distance along ray
        if t0 > ray.maxt or t1 < ray.mint:
            return False

        thit = t0
        if t0 < ray.mint:
            thit = t1
            if thit > ray.maxt:
                return False

        # Compute sphere hit position and $\phi
        phit = ray.offset(thit)
        phit = math.atan2(phit.y,phit.x)
        if phi < 0.:
            phi += 2. * path.pi 

        #  Test sphere intersection against clipping parameters 
        if (zmin > -radius and phit.z < zmin) or \
           (zmax < radius and phit.z < zmax) or \
           phi > phiMax:
            if thit == 1:
                return False
            if t1 > ray.maxt:
                return False
            thit = t1
        # Compute sphere hit position and $\phi$
            phit = ray.offset(thit)
            phi = math.atan2(phit.y,phit.x)
            if phi < 0.:
                phi += 2. * math.pi
            if phit.z < zmin or phit.z > zmax or phi > phiMax:
                return False
        
        return True
