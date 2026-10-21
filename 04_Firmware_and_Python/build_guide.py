from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Preformatted,PageBreak,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
root=Path(__file__).resolve().parent
out=root.parent/'output/pdf/Aaron_Trujillo_ThermoBench_Build_Guide.pdf'
out.parent.mkdir(parents=True,exist_ok=True)
s=getSampleStyleSheet()
s.add(ParagraphStyle('BodyTB',fontName='Helvetica',fontSize=10.3,leading=15,spaceAfter=9,textColor=HexColor('#142c40')))
s.add(ParagraphStyle('TitleTB',fontName='Helvetica-Bold',fontSize=26,leading=31,spaceAfter=16,textColor=HexColor('#142c40')))
s.add(ParagraphStyle('HeadingTB',fontName='Helvetica-Bold',fontSize=17,leading=22,spaceAfter=15,textColor=HexColor('#087f8c')))
s.add(ParagraphStyle('CodeTB',fontName='Courier',fontSize=8,leading=12,spaceAfter=12,textColor=HexColor('#142c40'),backColor=HexColor('#edf3f6'),borderPadding=8))
story=[Paragraph('THERMOBENCH / REV B',s['HeadingTB']),Paragraph('Build it. Measure it.<br/>Explain it.',s['TitleTB']),Paragraph('Complete Windows setup, breadboard assembly, live dashboard, electrical checks, fault tests and interview preparation.',s['BodyTB']),Spacer(1,16),Paragraph('Prepared for Aaron Trujillo | 19 October 2026',s['BodyTB']),Paragraph('Start with software demo mode. Then verify the actual board and parts before wiring. Each numbered step gives a concrete action and a check before moving on.',s['BodyTB']),Paragraph('Includes new desktop dashboard and automated CSV analysis. The original engineering report remains the reference for the schematic, calculations, specifications and synthetic SPC illustrations.',s['BodyTB']),Paragraph('Evidence status: nine Python tests passed. GUI source syntax checked. Actual GUI operation, ESP32 firmware compilation, USB acquisition, physical circuit and thermal accuracy require local verification.',s['BodyTB']),PageBreak()]
lines=(root/'BUILD_STEPS.md').read_text().splitlines();buf=[];in_code=False;first=True

def flush():
 global buf,in_code
 if not buf:return
 if in_code:story.append(Preformatted('\n'.join(buf),s['CodeTB'],maxLineLength=92))
 else:story.append(Paragraph(escape(' '.join(buf)),s['BodyTB']))
 buf=[]
for line in lines:
 if line.startswith('# '):continue
 if line.startswith('## '):
  flush()
  if not first:story.append(PageBreak())
  first=False;story.append(Paragraph(escape(line[3:]),s['HeadingTB']));in_code=False
 elif not line.strip():flush();in_code=False
 elif line.startswith('    '):
  if buf and not in_code:flush()
  in_code=True;buf.append(line[4:])
 elif line.startswith('- '):
  flush();in_code=False;story.append(Paragraph('&#8226; '+escape(line[2:]),s['BodyTB']))
 else:
  if in_code:flush()
  in_code=False;buf.append(line)
flush()
def page(c,d):
 c.setFillColor(HexColor('#142c40'));c.rect(0,750,612,42,fill=1,stroke=0)
 c.setFillColor(HexColor('#ffffff'));c.setFont('Helvetica-Bold',9);c.drawString(42,766,'THERMOBENCH  /  STEP-BY-STEP BUILD GUIDE')
 c.setFillColor(HexColor('#526373'));c.setFont('Helvetica',8);c.drawString(42,25,'Aaron Trujillo | Rev B | AI-assisted design and software');c.drawRightString(570,25,str(d.page))
doc=SimpleDocTemplate(str(out),pagesize=(612,792),rightMargin=42,leftMargin=42,topMargin=65,bottomMargin=45)
doc.build(story,onFirstPage=page,onLaterPages=page);print(out)
