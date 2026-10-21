import unittest
from bench import decode,voltage
class BenchTest(unittest.TestCase):
    def test_nominal(self): self.assertAlmostEqual(decode(1.6)[0],25,places=8)
    def test_roundtrip(self):
        for t in [16,25,35,44,50,54]: self.assertAlmostEqual(decode(float(voltage(t)))[0],t,places=8)
    def test_faults(self):
        self.assertEqual(decode(0)[1],'LOW_FAULT')
        self.assertEqual(decode(3.1)[1],'HIGH_FAULT')
        self.assertEqual(decode(float('nan'))[1],'INVALID')
    def test_hysteresis(self):
        self.assertEqual(decode(float(voltage(46)))[1],'HOT')
        self.assertEqual(decode(float(voltage(44)),'HOT')[1],'HOT')
        self.assertEqual(decode(float(voltage(44)),'NORMAL')[1],'NORMAL')
        self.assertEqual(decode(float(voltage(42)),'HOT')[1],'NORMAL')
    def test_range(self): self.assertEqual(decode(float(voltage(60)))[1],'OUT_OF_RANGE')
if __name__=='__main__': unittest.main()
