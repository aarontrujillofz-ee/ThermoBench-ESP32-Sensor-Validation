import csv,tempfile,unittest
from pathlib import Path
from station import parse_line,load_csv,analyze
class StationTest(unittest.TestCase):
    def test_fault_blank_and_inconsistent_rejected(self):
        self.assertIsNone(parse_line('0,0,,LOW_FAULT')['temp_c'])
        for line in ['0,1600,,NORMAL','0,nan,25,NORMAL','0,1600,25,LOW_FAULT','0,0,25,NORMAL','0,1600,inf,NORMAL']:
            with self.assertRaises(ValueError):parse_line(line)
    def test_mixed_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'mixed.csv';p.write_text('source,ms,mv,temp_c,status\nHARDWARE,0,1600,25,NORMAL\nSYNTHETIC,200,1600,25,NORMAL\n')
            with self.assertRaises(ValueError):load_csv(p)
    def test_valid_run_then_wrong_reference(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.csv'
            with p.open('w',newline='') as f:
                w=csv.writer(f);w.writerow(['source','ms','mv','temp_c','status'])
                for i in range(301):w.writerow(['SYNTHETIC',i*200,1600,25,'NORMAL'])
            a=analyze(p,Path(d)/'a',1600,30)
            self.assertEqual(a['source'],'SYNTHETIC')
            self.assertTrue(all(x=='PASS' for x in a['checks'].values()))
            b=analyze(p,Path(d)/'b',1700,30)
            self.assertEqual(b['checks']['voltage_mean_vs_dmm'],'FAIL')
    def test_reset_not_pass(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'reset.csv';p.write_text('source,ms,mv,temp_c,status\nSYNTHETIC,200,1600,25,NORMAL\nSYNTHETIC,0,1600,25,NORMAL\n')
            a=analyze(p,Path(d)/'a')
            self.assertEqual(a['checks']['timestamps_increasing'],'FAIL')
            self.assertEqual(a['checks']['steady_repeatability_sd_le_0p15_c'],'NOT_EVALUATED')
if __name__=='__main__':unittest.main()
