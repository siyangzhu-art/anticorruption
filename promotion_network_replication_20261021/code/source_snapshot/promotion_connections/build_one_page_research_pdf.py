"""One-page Chinese research note; uses verified existing estimates only."""
from pathlib import Path
import sys, json, hashlib
sys.path.append(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\code\vendor\dml_python')
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image as PILImage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether
from pypdf import PdfReader
import pypdfium2 as pdfium

B=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
O=B/'one_page_research_design_2026_10_21';O.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('YaHei',r'C:\Windows\Fonts\msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('YaHeiBold',r'C:\Windows\Fonts\msyhbd.ttc',subfontIndex=0))
pdfmetrics.registerFontFamily('YaHei',normal='YaHei',bold='YaHeiBold',italic='YaHei',boldItalic='YaHeiBold')
W,H=A4;M=42;CW=W-2*M
body=ParagraphStyle('body',fontName='YaHei',fontSize=10.5,leading=16.1,spaceAfter=5.5,wordWrap='CJK',textColor=colors.HexColor('#202020'))
head=ParagraphStyle('head',fontName='YaHeiBold',fontSize=11.7,leading=17,spaceBefore=7.2,spaceAfter=3.4,wordWrap='CJK')
small=ParagraphStyle('small',parent=body,fontSize=8.5,leading=12,spaceAfter=2,textColor=colors.HexColor('#555555'))
title=ParagraphStyle('title',fontName='YaHeiBold',fontSize=18,leading=24,alignment=TA_CENTER,spaceAfter=4)
subtitle=ParagraphStyle('subtitle',parent=body,fontSize=9,leading=13,alignment=TA_CENTER,spaceAfter=10,textColor=colors.HexColor('#555555'))

def equation(tex,name,maxwidth=CW-16):
 fig=plt.figure(figsize=(8,.6));fig.text(0,.5,tex,fontsize=16,va='center',ha='left');p=O/(name+'.png')
 fig.savefig(p,dpi=360,bbox_inches='tight',pad_inches=.035,transparent=True);plt.close(fig)
 with PILImage.open(p) as im: iw,ih=im.size
 width=min(maxwidth,iw/360*72);img=Image(str(p),width=width,height=width*ih/iw);img.hAlign='CENTER';return img

prepath=B/'preinspection_fixed_C0_levels_2026_10_21/adjusted_preinspection_results.csv'
eventpath=B/'control_FE_sensitivity_post4/all_level_results.csv'
pre=pd.read_csv(prepath);event=pd.read_csv(eventpath)
a=pre[pre.model_id.eq(3)].iloc[0]
e=event[event.estimator.eq('TWFE_fixed')&event.control_id.eq('C08')&event.term.eq('post_average')].set_index('fe')
assert abs(a.b-7.980637)<1e-5

story=[];record=[]
def p(text,style=body):story.append(Paragraph(text,style));record.append(text)
def h(text):p(text,head)
p('地方政治关系与官员晋升',title)
p('首次中央巡视的事前证据与动态检验　｜　一页研究说明　｜　2026年10月21日',subtitle)
p('<b>研究问题：</b>中央巡视进驻后，市级主官与省级领导的既有关系，其晋升回报是否下降？晋升分析作为整篇论文的机制证据，用于考察中央监督如何改变地方网络的职业回报；政策是否更服从中央，仍需直接的政策行为证据。')

h('样本与变量')
p('CPED履历重建2006—2017年市长及市委书记的年度晋升。晋升包括行政级别上升、市长升市委书记，以及首次转任副省长（允许原已为副部级）。固定关系 C<sub>0</sub> 为与基期省委书记或省长任一人的事前至少六个月共事关系，形成于2012年前、早于双方当前共同任职。G 为首次中央巡视年份，k＝t−G；2013、2014巡视省的关系快照分别为2011、2012年底。')

h('事前描述性证据')
story.append(equation(r'$100\,Promotion_{it}=\delta C_i^0+\lambda_{pt}+X_{it}^{\prime}\gamma+\varepsilon_{it},\quad k\in\{-4,-3,-2,-1\}.$','equation_pre'))
story.append(Spacer(1,4))
p('使用主事件研究固定组的事前观测：1,562个官员年、542人（62名有关系者）、26省。加入省份×年份FE及个人、城市经济控制，不加城市或个人FE；固定关系水平会被个人FE吸收。原始晋升率为17.06%与14.44%。完整控制的差异为<b>＋7.98个百分点</b>，95% CI [0.89，15.07]，p＝0.029；仅省年FE时为＋1.22，p＝0.614。城市FE敏感性结果不支持稳健的正向水平差异，需在附录保留。')

h('巡视事件研究')
story.append(equation(r'$100\,Promotion_{it}=\alpha_i+\eta_{c(i,t)}+\lambda_{pt}+\sum_{k\neq-1}\beta_k C_i^0\mathbf{1}\{t-G_p=k\}+X_{it}^{\prime}\gamma+\varepsilon_{it}.$','equation_event'))
story.append(Spacer(1,4))
p('α 为个人FE，η 为加法城市FE，λ 为省份×实际年份FE；并列报告省去η的版本。β 衡量两组晋升差距相对巡视前一年（k＝−1）的变化，不能解释为巡视对全部官员的平均效应。主年度共同样本为2,807个官员年、547人、26省；事后＋1至＋4期的TWFE平均变化如下。')
rows=[['固定效应组合','平均变化 百分点','95% CI','p值']]
for key,label in [('I_PXY','个人＋省份×年份'),('I_CITY_PXY','个人＋城市＋省份×年份')]:
 r=e.loc[key];rows.append([label,f'{r.b:.2f}',f'[{r.lo:.2f}, {r.hi:.2f}]',f'{r.p:.3f}'])
table=Table(rows,colWidths=[215,103,128,CW-446],hAlign='LEFT')
table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'YaHeiBold'),('FONTNAME',(0,1),(-1,-1),'YaHei'),('FONTSIZE',(0,0),(-1,-1),9),('LEADING',(0,0),(-1,-1),13),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf0f2')),('GRID',(0,0),(-1,-1),.45,colors.HexColor('#d9d9d9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(1,0),(-1,-1),'CENTER'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
story.append(table);story.append(Spacer(1,5))

h('推断与解释')
p('个人控制包括年龄特征、任期及平方、职级和现职身份；经济控制为跟随官员任职城市的上年GDP增长、对数人均GDP及人口。标准误按省聚类，报告95%逐点CI；个人＋时间FE吸收线性年龄。关系组与非关系组均受到巡视，因果解释要求没有巡视时两组差距按相应条件趋势演变。')
p('<b>可支持的表述：</b>事前存在正向条件关联；巡视后差距变化为负，但估计对FE和样本支持敏感，现阶段不能确认关系优势已消失。事前水平δ与事件系数β不能直接相加。固定名单回看早期履历有选择问题，关系可能尚未形成；＋4期仅4名关系官员。排除腐败更替省份的检查不能消除全部选择或混杂，后验规格探索也需披露。')
p('文献定位：Li与Manion（2023，BJPS）已研究反腐强度与旧部晋升，并有巡视扩展。本设计的潜在增量在于固定事前关系、围绕首次巡视检验动态变化，并与政策执行证据衔接。',small)

out=O/'地方政治关系与晋升_一页完整研究说明.pdf'
def footer(canvas,doc):
 canvas.setFont('YaHei',8);canvas.setFillColor(colors.HexColor('#666666'))
 canvas.drawString(M,23,'研究设计与已有结果汇总　未新增回归')
 canvas.drawRightString(W-M,23,str(doc.page))
doc=SimpleDocTemplate(str(out),pagesize=A4,leftMargin=M,rightMargin=M,topMargin=32,bottomMargin=36,title='地方政治关系与官员晋升 首次中央巡视研究说明',author='研究项目说明')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
reader=PdfReader(str(out));assert len(reader.pages)==1, f'Expected one page, got {len(reader.pages)}'
txt=reader.pages[0].extract_text();assert '地方政治关系' in txt and '7.98' in txt and '-11.18' in txt
pdf=pdfium.PdfDocument(str(out));page=pdf[0];page.render(scale=1.8).to_pil().save(O/'page_preview.png')
(O/'content_source.txt').write_text('\n\n'.join(record)+'\n\n'+str(rows),encoding='utf8')
(O/'verification.json').write_text(json.dumps(dict(pages=1,bytes=out.stat().st_size,source_files=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [prepath,eventpath]],text_characters=len(txt)),ensure_ascii=False,indent=2),encoding='utf8')
print(str(out));print('Verified one page; text extraction and data checks passed.')
