import pysal.core.FileIO as FileIO
import re


#####################################################################
## ToDo: Add Well-Known-Binary support...
##       * WKB spec:
##  http://webhelp.esri.com/arcgisserver/9.3/dotNet/index.htm#geodatabases/the_ogc_103951442.htm 
##
##
#####################################################################



class WKTReader(FileIO.FileIO):
    MODES = ['r']
    FORMATS = ['wkt']
    def __init__(self,*args,**kwargs):
        pysal.core.FileIO.__init__(self,*args,**kwargs)
        self.__idx = {}
        self.__pos = 0
        self.__open()
    def open(self):
        self.__open()
    def __open(self):
        self.dataObj = open(self.dataPath,self.mode)
        self.wkt = WKTParser()
    def _read(self):
        pysal.core.FileIO._complain_ifclosed(self.closed)
        if self.__pos not in self.__idx:
            self.__idx[self.__pos] = self.dataObj.tell()
        line = self.dataObj.readline()
        if line:
            shape = self.wkt.fromWKT(line)
            shape.id = self.pos
            self.__pos += 1
            self.pos += 1
            return shape
        else:
            self.seek(0)
            return None
    def seek(self,n):
        pysal.core.FileIO.seek(self,n)
        pos = self.pos
        if pos in self.__idx:
            self.dataObj.seek(self.__idx[pos])
            self.__pos = pos
        else:
            while pos not in self.__idx:
                s = self._read()
                if not s:
                    raise IndexError, "%d not in range(0,%d)"%(pos,max(self.__idx.keys()))
            self.pos = pos
            self.__pos = pos
            self.dataObj.seek(self.__idx[pos])
    def close(self):
        self.dataObj.close()
        pysal.core.FileIO.close(self)
        

class WKTParser:
    """ Class to represent OGC WKT, supports reading and writing
        Modified from...
        # URL: http://dev.openlayers.org/releases/OpenLayers-2.7/lib/OpenLayers/Format/WKT.js
        #Reg Ex Strings copied from OpenLayers.Format.WKT
    """
    regExes = { 'typeStr': re.compile('^\s*(\w+)\s*\(\s*(.*)\s*\)\s*$'),
        'spaces': re.compile('\s+'),
        'parenComma': re.compile('\)\s*,\s*\('),
        'doubleParenComma': re.compile('\)\s*\)\s*,\s*\(\s*\('),  # can't use {2} here
        'trimParens': re.compile('^\s*\(?(.*?)\)?\s*$') }
    def __init__(self):
        self.parsers = p = {}
        p['point'] = self.Point
        p['linestring'] = self.LineString
        p['polygon'] = self.Polygon
    def Point(self,geoStr):
        coords = self.regExes['spaces'].split(geoStr.strip())
        return pysal.Point(coords[0],coords[1])
    def LineString(self,geoStr):
        points = geoStr.strip().split(',')
        points = map(self.Point,points)
        return pysal.LineString(points)
    def Polygon(self,geoStr):
        rings = self.regExes['parenComma'].split(geoStr.strip())
        for i,ring in enumerate(rings):
            ring = self.regExes['trimParens'].match(ring).groups()[0]
            ring = self.LineString(ring)
            rings[i] = ring
        return pysal.Polygon(rings)
    def fromWKT(self,wkt):
        matches = self.regExes['typeStr'].match(wkt)
        if matches:
            geoType,geoStr = matches.groups()
            geoType = geoType.lower()
            try:
                return self.parsers[geoType](geoStr)
            except KeyError:
                raise NotImplementedError, "Unsupported WKT Type: %s"%geoType
        else:
            return None
    __call__ = fromWKT
if __name__=='__main__':
    p = 'POLYGON((1 1,5 1,5 5,1 5,1 1),(2 2, 3 2, 3 3, 2 3,2 2))'
    pt = 'POINT(6 10)'
    l = 'LINESTRING(3 4,10 50,20 25)'
    wktExamples = ['POINT(6 10)',
            'LINESTRING(3 4,10 50,20 25)',
            'POLYGON((1 1,5 1,5 5,1 5,1 1),(2 2, 3 2, 3 3, 2 3,2 2))',
            'MULTIPOINT(3.5 5.6,4.8 10.5)',
            'MULTILINESTRING((3 4,10 50,20 25),(-5 -8,-10 -8,-15 -4))',
            'MULTIPOLYGON(((1 1,5 1,5 5,1 5,1 1),(2 2, 3 2, 3 3, 2 3,2 2)),((3 3,6 2,6 4,3 3)))',
            'GEOMETRYCOLLECTION(POINT(4 6),LINESTRING(4 6,7 10))',
            'POINT ZM (1 1 5 60)',
            'POINT M (1 1 80)',
            'POINT EMPTY',
            'MULTIPOLYGON EMPTY']
    wkt = WKTParser()
    

