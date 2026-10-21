from pathlib import Path
H=Path(__file__).parent
s=(H/'final_validation.py').read_text(encoding='utf8')
s=s.replace('from estimate import','from estimate_revised import')
s=s.replace('All eight primary','All twelve primary').replace("==8 and V.loc","==12 and V.loc")
s=s.replace('holm_eight_wild_changes','holm_twelve_wild_changes')
s=s.replace("[('mayor',2005,'PXY'),('mayor',2015,'PXY'),('secretary',2010,'PY'),('secretary',2015,'CITY_PXY')]", "[('all',2008,'PXY'),('all',2015,'PXY'),('all',2010,'PY'),('secretary',2015,'CITY_PXY')]")
s=s.replace("d=sample(A[A.role.eq(role)],", "d=sample(A if role=='all' else A[A.role.eq(role)],")
s=s.replace("for col in (['province_code'", "if d.role.nunique()>1:chunks.append(d[['role_secretary']].to_numpy(float))\n for col in (['province_code'")
(H/'validate_revised.py').write_text(s,encoding='utf8')
out=Path(r'C:\Users\siyang zhu\Desktop\hometown\project_organized\result\promotion_connections_revised_2006_2017_2026_10_20')
(out/'code/validate_revised.py').write_text(s,encoding='utf8')
print('Revised independent validations generated')
