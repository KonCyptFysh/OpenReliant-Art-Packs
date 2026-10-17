"""Material filtering and packaging safety checks using small diagnostic images."""
import tempfile, unittest, subprocess
from pathlib import Path
import numpy as np
from PIL import Image
import resolution_pack as rp

class Filtering(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
    def resize(self,name,array,limit=1):
        p=self.root/name; q=self.root/('out-'+name)
        Image.fromarray(np.array(array,dtype='uint8')).save(p)
        rp.resize_texture(p,q,limit)
        return np.array(Image.open(q))
    def test_light_average_is_not_gamma_average(self):
        a=[[[255,255,255],[0,0,0]],[[0,0,0],[0,0,0]]]
        for name in ('hull.png','hull_emissive.png'):
            self.assertTrue(np.all(self.resize(name,a)==137))
    def test_transparent_colour_does_not_bleed(self):
        a=[[[255,0,0,255],[0,255,0,0]],[[0,255,0,0],[0,255,0,0]]]
        self.assertEqual(self.resize('hull.png',a).tolist(),[[[255,0,0,64]]])
    def test_orm_channels_remain_linear_and_independent(self):
        a=[[[0,80,255],[0,80,0]],[[0,80,0],[0,80,0]]]
        self.assertEqual(self.resize('hull_orm.png',a).tolist(),[[[0,80,64]]])
    def test_sloped_normals_are_unit_vectors_after_reduction(self):
        a=[[[255,128,128],[128,128,255]],[[255,128,128],[128,128,255]]]
        n=self.resize('hull_normal.png',a)[0,0]/255*2-1
        self.assertAlmostEqual(float(np.linalg.norm(n)),1,delta=.01)
        self.assertAlmostEqual(n[0],n[2],delta=.01)
        self.assertGreater(n[0],.70)
    def test_aspect_ratio_and_small_maps(self):
        self.assertEqual(rp.dimensions((8192,4096),1024),(1024,512))
        self.assertEqual(rp.dimensions((256,1024),1024),(256,1024))
        p=self.root/'small.png';q=self.root/'copy.png'
        Image.new('RGB',(32,16),(21,53,77)).save(p)
        rp.resize_texture(p,q,1024)
        self.assertEqual(p.read_bytes(),q.read_bytes())
    def test_sixteen_bit_precision_is_preserved(self):
        p=self.root/'hull_normal.png';q=self.root/'small_normal.png'
        a=np.tile(np.array([32771,32773,65534],dtype='>u2'),(2,2,1))
        subprocess.run(['magick','-size','2x2','-depth','16','-endian','MSB','RGB:-',
            '-define','png:bit-depth=16',str(p)],input=a.tobytes(),check=True)
        rp.resize_texture(p,q,1)
        self.assertEqual(q.read_bytes()[24],16)
        raw=subprocess.check_output(['magick',str(q),'-depth','16','-endian','MSB','RGB:-'])
        pixel=np.frombuffer(raw,dtype='>u2')
        self.assertLess(abs(int(pixel[0])-32771),2)
        self.assertLess(abs(int(pixel[1])-32773),2)

    def test_dimension_mismatch_is_rejected(self):
        Image.new('RGB',(32,32)).save(self.root/'hull.png')
        Image.new('RGB',(16,16)).save(self.root/'hull_emissive.png')
        with self.assertRaisesRegex(ValueError,'dimensions differ'):rp.audit_maps(self.root,1024)
    def test_orphan_maps_are_rejected(self):
        Image.new('RGB',(16,16)).save(self.root/'hull_normal.png')
        with self.assertRaisesRegex(ValueError,'Orphan'):rp.audit_maps(self.root,1024)

if __name__=='__main__':unittest.main()
