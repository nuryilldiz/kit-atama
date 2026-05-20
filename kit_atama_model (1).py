# =============================================================================
#  KİT ATAMA OPTİMİZASYON MODELİ - Final Versiyon
#  Terminal: python "kit_atama_model (1).py"
#  UI:       ui.py tarafindan model_calistir() ile cagrilir
# =============================================================================

import argparse
import sys
import io
from pathlib import Path
import openpyxl
import gurobipy as gp
from gurobipy import GRB

class C:
    BOLD   = "\033[1m"; RESET  = "\033[0m"; GREEN  = "\033[92m"
    YELLOW = "\033[93m"; CYAN  = "\033[96m"; RED    = "\033[91m"
    PURPLE = "\033[95m"; GRAY  = "\033[90m"; WHITE  = "\033[97m"

ALAN_RENK = {"A": C.CYAN, "B": C.PURPLE, "C": C.GREEN, "D": C.YELLOW}

B_MAX       = 10
MAX_KORIDOR = 2
D_MAX       = 100.0
ALFA        = 0.3

KARSILIKI_CIFTLER = [
    (1,4),(2,5),(3,6),
    (10,15),(11,16),(12,17),(13,18),(14,19),
    (26,29),(27,30),(28,31),
]
KARSILIKI_DICT = {}
for (bj,bk) in KARSILIKI_CIFTLER:
    KARSILIKI_DICT[bj]=bk; KARSILIKI_DICT[bk]=bj


def excel_oku(dosya) -> dict:
    if isinstance(dosya, bytes):
        wb = openpyxl.load_workbook(io.BytesIO(dosya), data_only=True)
    else:
        wb = openpyxl.load_workbook(str(dosya), data_only=True)

    def sayfa(isim):
        if isim not in wb.sheetnames:
            raise ValueError(f"'{isim}' sayfasi bulunamadi!")
        return wb[isim]

    ws = sayfa("Ck_Blok_Kapasite")
    C_k, tip_k, alan_k, K_new = {}, {}, {}, []
    for r in ws.iter_rows(min_row=3, values_only=True):
        if r[0] is None or not isinstance(r[0],(int,float)): continue
        k=int(r[0]); C_k[k]=float(r[1])
        tip_k[k]=str(r[2]).strip() if r[2] else "Mevcut"
        alan_k[k]=str(r[4]).strip() if len(r)>4 and r[4] else None
        if tip_k[k]=="Aday": K_new.append(k)

    K=sorted(C_k.keys()); K_alan={}
    for k in K: K_alan.setdefault(alan_k[k],[]).append(k)
    alanlar=sorted(K_alan.keys())

    ws=sayfa("Ui_Kapasite"); U_i,kod_i={},{}
    for r in ws.iter_rows(min_row=3,values_only=True):
        if r[0] is None or not isinstance(r[0],(int,float)): continue
        i,kod,ui=int(r[0]),str(r[1]).strip(),float(r[2])
        if i not in U_i: U_i[i],kod_i[i]=ui,[kod]
        else: U_i[i]=max(U_i[i],ui); kod_i[i].append(kod)
    I=sorted(U_i.keys())

    ws=sayfa("F_il_Matrisi")
    header=[c.value for c in list(ws.iter_rows(min_row=2,max_row=2))[0]]
    L=list(range(1,sum(1 for h in header if h and str(h).startswith("l"))+1))
    F_il={}
    for r in ws.iter_rows(min_row=3,values_only=True):
        if r[0] is None or not isinstance(r[0],(int,float)): continue
        i=int(r[0])
        for idx,l in enumerate(L):
            v=r[idx+1] if idx+1<len(r) else 0
            F_il[(i,l)]=float(v) if v else 0.0

    ws=sayfa("d_kl_Matrisi"); d_kl={}
    for r in ws.iter_rows(min_row=3,values_only=True):
        if r[0] is None or not isinstance(r[0],(int,float)): continue
        k=int(r[0])
        for idx,l in enumerate(L):
            v=r[idx+1] if idx+1<len(r) else 0
            d_kl[(k,l)]=float(v) if v else 0.0

    D_ik,F_i={},{}
    for i in I:
        total_f=sum(F_il.get((i,l),0) for l in L)
        F_i[i]=max(F_il.get((i,l),0) for l in L)
        for k in K:
            D_ik[(i,k)]=(sum(F_il.get((i,l),0)*d_kl.get((k,l),0) for l in L)/total_f
                         if total_f>0 else 0.0)

    hat_i={}
    for i in I:
        for l in L:
            if F_il.get((i,l),0)>0: hat_i[i]=l; break

    blok_koridor,koridor_alan={},{}
    if "KORIDORLAR" in wb.sheetnames:
        ws=wb["KORIDORLAR"]
        for r in ws.iter_rows(min_row=2,values_only=True):
            if r[0] is None or not isinstance(r[0],(int,float)): continue
            blok=int(r[0]); alan=str(r[1]).strip() if r[1] else None
            kor_no=int(r[2]) if r[2] is not None else None
            if kor_no is not None:
                blok_koridor[blok]=kor_no; koridor_alan[kor_no]=alan

    koridor_gruplari_dict={}
    for blok,kor_no in blok_koridor.items():
        koridor_gruplari_dict.setdefault(kor_no,set()).add(blok)
    koridor_gruplari=[(kn,frozenset(bl),koridor_alan.get(kn))
                      for kn,bl in sorted(koridor_gruplari_dict.items())]

    kod_adi={}
    if "ALT_GRUPLAR" in wb.sheetnames:
        ws=wb["ALT_GRUPLAR"]
        for r in ws.iter_rows(min_row=3,values_only=True):
            if r[0] is None or not isinstance(r[0],(int,float)): continue
            ad=str(r[1]).strip() if r[1] else ""
            kod=str(r[2]).strip() if r[2] else ""
            if kod: kod_adi[kod]=ad

    return dict(I=I,K=K,L=L,K_new=K_new,K_alan=K_alan,alanlar=alanlar,
                U_i=U_i,C_k=C_k,tip_k=tip_k,alan_k=alan_k,
                F_il=F_il,F_i=F_i,D_ik=D_ik,
                kod_i=kod_i,hat_i=hat_i,kod_adi=kod_adi,
                koridor_gruplari=koridor_gruplari,blok_koridor=blok_koridor)


def feasibility_kontrol(veri):
    I,K,C_k,U_i=veri["I"],veri["K"],veri["C_k"],veri["U_i"]
    K_alan,alanlar,kod_i=veri["K_alan"],veri["alanlar"],veri["kod_i"]
    print(f"\n{C.BOLD}On feasibility kontrolu...{C.RESET}")
    hata=False
    for i in I:
        talep=U_i[i]; kodlar="+".join(kod_i[i])
        if sum(C_k[k] for k in K)<talep:
            print(f"  {C.RED}HATA{C.RESET}: Kategori {i} [{kodlar}] toplam kapasite yetersiz!")
            hata=True; continue
        uygun=[a for a in alanlar if sum(C_k[k] for k in K_alan.get(a,[]))>=talep]
        uygunsuz=[a for a in alanlar if sum(C_k[k] for k in K_alan.get(a,[]))<talep]
        if not uygun:
            print(f"  {C.RED}HATA{C.RESET}: Kategori {i} [{kodlar}] hicbir alanda kapasite yok!")
            hata=True
        elif uygunsuz:
            print(f"  {C.YELLOW}UYARI{C.RESET}: Kategori {i} [{kodlar}] su alanlarda yetersiz: {uygunsuz}")
    if not hata: print(f"  {C.GREEN}Tum kategoriler icin kapasite yeterli.{C.RESET}")
    return not hata


def model_calistir(dosya, b_max=10, max_kor=2, t_limit=300, mip_gap=0.01):
    """ui.py tarafindan da cagrilir."""
    import time
    t0=time.time()
    veri=excel_oku(dosya)
    I,K,K_new=veri["I"],veri["K"],veri["K_new"]
    K_alan,alanlar=veri["K_alan"],veri["alanlar"]
    U_i,C_k=veri["U_i"],veri["C_k"]
    F_i,D_ik=veri["F_i"],veri["D_ik"]
    alan_k=veri["alan_k"]; tip_k=veri["tip_k"]
    kod_i=veri["kod_i"]; kod_adi=veri.get("kod_adi",{})
    hat_i=veri["hat_i"]
    koridor_gruplari=veri["koridor_gruplari"]
    blok_koridor=veri["blok_koridor"]

    m=gp.Model("kit_atama")
    m.setParam("TimeLimit",t_limit)
    m.setParam("MIPGap",mip_gap)
    m.setParam("OutputFlag",1)

    x=m.addVars(I,K,vtype=GRB.BINARY,name="x")
    p=m.addVars(I,K,vtype=GRB.BINARY,name="p")
    Y=m.addVars(K_new,vtype=GRB.BINARY,name="Y") if K_new else {}
    u=m.addVars(I,K,lb=0,name="u")
    A=m.addVars(I,alanlar,vtype=GRB.BINARY,name="A")
    kor_numalar=[kn for kn,_,_ in koridor_gruplari]
    G=m.addVars(I,kor_numalar,vtype=GRB.BINARY,name="G") if kor_numalar else {}
    m.update()

    m.addConstrs((gp.quicksum(x[i,k] for k in K)>=1 for i in I),"K1")
    for i in I:
        for j in K_new: m.addConstr(x[i,j]<=Y[j])
    m.addConstrs((gp.quicksum(u[i,k] for k in K)==U_i[i] for i in I),"K3")
    m.addConstrs((gp.quicksum(u[i,k] for i in I)<=C_k[k] for k in K),"K4")
    m.addConstrs((u[i,k]<=C_k[k]*x[i,k] for i in I for k in K),"K5")
    m.addConstrs((u[i,k]>=x[i,k] for i in I for k in K),"K6")
    m.addConstrs((gp.quicksum(x[i,k] for k in K)<=b_max for i in I),"K7")
    m.addConstrs((gp.quicksum(A[i,a] for a in alanlar)==1 for i in I),"K8a")
    m.addConstrs((x[i,k]<=A[i,alan_k[k]] for i in I for k in K),"K8b")
    m.addConstrs((gp.quicksum(p[i,k] for k in K)==1 for i in I),"P1")
    m.addConstrs((p[i,k]<=x[i,k] for i in I for k in K),"P2")
    for i in I:
        for j in K_new: m.addConstr(p[i,j]<=Y[j])
        for k in K: m.addConstr(u[i,k]>=min(U_i[i],C_k[k])*p[i,k])

    if kor_numalar:
        m.addConstrs((gp.quicksum(G[i,kn] for kn in kor_numalar)>=1 for i in I),"KOR1")
        alan_kor={}
        for kn,_,al in koridor_gruplari: alan_kor.setdefault(al,[]).append(kn)
        for i in I:
            for al,kl in alan_kor.items():
                m.addConstr(gp.quicksum(G[i,kn] for kn in kl)<=max_kor)
                ks=sorted(kl)
                for a1,k1 in enumerate(ks):
                    for a2,k2 in enumerate(ks):
                        if abs(a1-a2)>1: m.addConstr(G[i,k1]+G[i,k2]<=1)
        for i in I:
            for k in K:
                kn=blok_koridor.get(k)
                if kn is not None: m.addConstr(x[i,k]<=G[i,kn])

    obj=gp.quicksum(F_i[i]*D_ik[i,k]*x[i,k] for i in I for k in K)
    if K_new: obj+=gp.quicksum(100.0*Y[j] for j in K_new)
    m.setObjective(obj,GRB.MINIMIZE)
    m.optimize()

    sure=time.time()-t0
    if m.Status==GRB.OPTIMAL: durum="OPTIMAL"
    elif m.Status==GRB.TIME_LIMIT and m.SolCount>0: durum="UYGUN"
    else: return {"durum":"COZUM_YOK","sure":sure}

    sonuc_kat={}
    for i in I:
        atanan=[k for k in K if x[i,k].X>0.5]
        birincil=next((k for k in K if p[i,k].X>0.5),None)
        alan_sec=next((a for a in alanlar if A[i,a].X>0.5),"?")
        sonuc_kat[i]={"bloklar":atanan,"birincil":birincil,"alan":alan_sec,
                      "talep":U_i[i],"kodlar":kod_i[i],
                      "adlar":[kod_adi.get(kd,kd) for kd in kod_i[i]],
                      "hat":hat_i.get(i,"?"),
                      "u":{k:round(u[i,k].X,1) for k in atanan}}

    blok_ozet={}
    for k in K:
        kullananlar=[(i,round(u[i,k].X,1)) for i in I if k in sonuc_kat[i]["bloklar"]]
        yuklu=sum(uv for _,uv in kullananlar)
        blok_ozet[k]={"kapasite":C_k[k],"yuklu":yuklu,
                      "doluluk":yuklu/C_k[k]*100 if C_k[k]>0 else 0,
                      "tip":tip_k[k],"alan":alan_k[k],"kullananlar":kullananlar}

    return {"durum":durum,"obj_val":m.ObjVal,"mip_gap":m.MIPGap*100,
            "sure":sure,"sonuc_kat":sonuc_kat,"blok_ozet":blok_ozet,
            "acik_yeni":[j for j in K_new if Y and Y[j].X>0.5],
            "U_i":U_i,"C_k":C_k,"alan_k":alan_k,"kod_i":kod_i,
            "kod_adi":kod_adi,"I":I,"K":K,"K_alan":K_alan,"alanlar":alanlar}


def cikti_yazdir(sonuc):
    if sonuc.get("durum")=="COZUM_YOK":
        print(f"{C.RED}Cozum bulunamadi.{C.RESET}"); return
    sonuc_kat=sonuc["sonuc_kat"]; obj_val=sonuc["obj_val"]
    acik_yeni=sonuc["acik_yeni"]; I=sonuc["I"]; K=sonuc["K"]
    C_k=sonuc["C_k"]; alan_k=sonuc["alan_k"]
    kod_i=sonuc["kod_i"]; kod_adi=sonuc.get("kod_adi",{})
    hat_i={i:sonuc_kat[i]["hat"] for i in I}
    K_alan=sonuc["K_alan"]; alanlar=sonuc["alanlar"]
    tip_k={k:sonuc["blok_ozet"][k]["tip"] for k in K}

    def adi(k): return kod_adi.get(k,k)
    ALAN_ADI={"A":"Alan A (Blok 1-7)","B":"Alan B (Blok 8-9)",
               "C":"Alan C (Blok 10-25)","D":"Alan D (Blok 26-31)"}
    sep="-"*72

    print(f"\n{C.BOLD}{'='*72}{C.RESET}")
    print(f"{C.BOLD}  KIT ATAMA OPTIMIZASYON SONUCLARI{C.RESET}")
    print(f"{C.BOLD}{'='*72}{C.RESET}")
    print(f"  Amac degeri : {C.GREEN}{obj_val:,.1f}{C.RESET}")
    print(f"  Yeni bloklar: {C.YELLOW}{acik_yeni}{C.RESET}\n")

    for a in alanlar:
        renk=ALAN_RENK.get(a,C.WHITE)
        katlar=[i for i in I if sonuc_kat[i]["alan"]==a]
        print(f"\n  {renk}{C.BOLD}{ALAN_ADI.get(a,a)}{C.RESET}")
        print(f"  {sep}")
        if not katlar: print(f"  {C.GRAY}Bu alana kategori atanmadi.{C.RESET}"); continue
        for i in sorted(katlar):
            s=sonuc_kat[i]
            kodlar=" + ".join(kod_i[i])
            adlar=" + ".join(adi(k2) for k2 in kod_i[i])
            print(f"\n  {renk}{C.BOLD}  Kat.{i:2d} [{kodlar}] {adlar} -> Hat l{hat_i[i]}{C.RESET}")
            print(f"  {'-'*68}")
            print(f"  {'Blok':>6}  {'Tip':<8}  {'Kapasite':>10}  {'Yuklenen':>10}  {'Doluluk':>9}  {'Birincil':>10}")
            print(f"  {'-'*68}")
            toplam=0
            for k in sorted(s["bloklar"]):
                yuklu=s["u"][k]; kap=C_k[k]
                dol=yuklu/kap*100 if kap>0 else 0
                dr=C.RED if dol>=90 else (C.YELLOW if dol>=70 else C.GREEN)
                tr=C.YELLOW if tip_k[k]=="Aday" else C.GRAY
                bi="(*)" if k==s["birincil"] else ""
                print(f"  {k:>6}  {tr}{tip_k[k]:<8}{C.RESET}  {kap:>10.0f}  {yuklu:>10.1f}  {dr}{dol:>8.1f}%{C.RESET}  {bi:>10}")
                toplam+=yuklu
            print(f"  {'-'*68}")
            dol_ort=toplam/s["talep"]*100 if s["talep"]>0 else 0
            print(f"  {'TOPLAM':>6}  {'':8}  {'':>10}  {toplam:>10.1f}    Talep:{s['talep']:.0f} ({dol_ort:.1f}%)")
    print(f"\n{C.BOLD}{'='*72}{C.RESET}\n")



def manuel_dogrula(dosya, manuel_atama, b_max=10, max_kor=2, t_limit=120, mip_gap=0.01):
    """
    Kullanıcının manuel atamasını sabit tutarak modeli çalıştırır.
    Kısıt ihlalleri varsa büyük ceza ile amaç fonksiyonuna yansıtılır.
    manuel_atama: {kategori_i: [blok_k, ...], ...}
    """
    import time
    t0 = time.time()
    veri = excel_oku(dosya)
    I, K, K_new    = veri["I"], veri["K"], veri["K_new"]
    K_alan, alanlar = veri["K_alan"], veri["alanlar"]
    U_i, C_k        = veri["U_i"], veri["C_k"]
    F_i, D_ik       = veri["F_i"], veri["D_ik"]
    alan_k, tip_k   = veri["alan_k"], veri["tip_k"]
    kod_i, hat_i    = veri["kod_i"], veri["hat_i"]
    koridor_gruplari = veri["koridor_gruplari"]
    blok_koridor    = veri["blok_koridor"]

    CEZA_BUYUK = 1e7  # kısıt ihlali cezası

    m = gp.Model("manuel_dogrula")
    m.setParam("TimeLimit", t_limit)
    m.setParam("MIPGap", mip_gap)
    m.setParam("OutputFlag", 0)

    # Değişkenler
    x = m.addVars(I, K, vtype=GRB.BINARY, name="x")
    u = m.addVars(I, K, lb=0, name="u")
    p = m.addVars(I, K, vtype=GRB.BINARY, name="p")
    Y = m.addVars(K_new, vtype=GRB.BINARY, name="Y") if K_new else {}
    A = m.addVars(I, alanlar, vtype=GRB.BINARY, name="A")

    # Ceza değişkenleri
    ceza_alan     = m.addVars(I, lb=0, name="ceza_alan")     # alan kısıtı ihlali
    ceza_koridor  = m.addVars(I, lb=0, name="ceza_kor")      # koridor kısıtı ihlali
    ceza_kapasite = m.addVars(K, lb=0, name="ceza_kap")      # kapasite aşımı
    m.update()

    # Manuel atamayı ZORLA sabitle — x[i,k]=1 ise sabit, yoksa 0
    for i in I:
        atanan_bloklar = manuel_atama.get(i, [])
        for k in K:
            if k in atanan_bloklar:
                m.addConstr(x[i, k] == 1, name=f"fix1_{i}_{k}")
            else:
                m.addConstr(x[i, k] == 0, name=f"fix0_{i}_{k}")

    # Temel kısıtlar
    m.addConstrs((gp.quicksum(x[i,k] for k in K) >= 1 for i in I), "K1")
    m.addConstrs((gp.quicksum(u[i,k] for k in K) == U_i[i] for i in I), "K3")

    # Kapasite kısıtı — ihlal varsa ceza_kapasite[k] devreye girer
    for k in K:
        m.addConstr(gp.quicksum(u[i,k] for i in I) <= C_k[k] + ceza_kapasite[k], name=f"K4_{k}")

    m.addConstrs((u[i,k] <= C_k[k] * x[i,k] + ceza_kapasite[k] for i in I for k in K), "K5")
    m.addConstrs((u[i,k] >= x[i,k] for i in I for k in K), "K6")

    # Birincil blok
    m.addConstrs((gp.quicksum(p[i,k] for k in K) == 1 for i in I), "P1")
    m.addConstrs((p[i,k] <= x[i,k] for i in I for k in K), "P2")

    # Alan kısıtı — ihlal varsa ceza_alan[i] devreye girer
    m.addConstrs((gp.quicksum(A[i,a] for a in alanlar) == 1 for i in I), "K8a")
    for i in I:
        for k in K:
            # x[i,k]=1 ama alan(k) != atanan alan → ihlal
            m.addConstr(x[i,k] <= A[i, alan_k[k]] + ceza_alan[i], name=f"K8b_{i}_{k}")

    # Aday blok
    for i in I:
        for j in K_new:
            m.addConstr(x[i,j] <= Y[j])

    # Amaç: F×D mesafe + kısıt ihlali cezaları
    obj = gp.quicksum(F_i[i] * D_ik[i,k] * x[i,k] for i in I for k in K)
    if K_new:
        obj += gp.quicksum(100.0 * Y[j] for j in K_new)
    obj += CEZA_BUYUK * gp.quicksum(ceza_alan[i]    for i in I)
    obj += CEZA_BUYUK * gp.quicksum(ceza_kapasite[k] for k in K)

    m.setObjective(obj, GRB.MINIMIZE)
    m.optimize()

    sure = time.time() - t0
    if m.Status in (GRB.OPTIMAL, GRB.TIME_LIMIT) and m.SolCount > 0:
        durum = "OPTIMAL" if m.Status == GRB.OPTIMAL else "UYGUN"
    else:
        return {"durum": "COZUM_YOK", "sure": sure}

    # İhlalleri tespit et
    ihlaller = []
    for i in I:
        if ceza_alan[i].X > 0.001:
            ihlaller.append(f"Kat.{i} alan kısıtı ihlali ({ceza_alan[i].X:.1f})")
    for k in K:
        if ceza_kapasite[k].X > 0.001:
            ihlaller.append(f"Blok {k} kapasite aşımı ({ceza_kapasite[k].X:.1f} raf)")

    # Saf mesafe değeri (ceza hariç)
    saf_mesafe = sum(F_i[i] * D_ik[i,k] * x[i,k].X for i in I for k in K)
    toplam_ceza = (CEZA_BUYUK * sum(ceza_alan[i].X for i in I) +
                   CEZA_BUYUK * sum(ceza_kapasite[k].X for k in K))

    sonuc_kat = {}
    for i in I:
        atanan = [k for k in K if x[i,k].X > 0.5]
        birincil = next((k for k in K if p[i,k].X > 0.5), None)
        alan_sec = next((a for a in alanlar if A[i,a].X > 0.5), "?")
        sonuc_kat[i] = {
            "bloklar": atanan, "birincil": birincil, "alan": alan_sec,
            "talep": U_i[i], "kodlar": kod_i[i],
            "adlar": [veri.get("kod_adi",{}).get(kd,kd) for kd in kod_i[i]],
            "hat": hat_i.get(i,"?"),
            "u": {k: round(u[i,k].X,1) for k in atanan}
        }

    blok_ozet = {}
    for k in K:
        kullananlar = [(i, round(u[i,k].X,1)) for i in I if k in sonuc_kat[i]["bloklar"]]
        yuklu = sum(uv for _,uv in kullananlar)
        blok_ozet[k] = {
            "kapasite": C_k[k], "yuklu": yuklu,
            "doluluk": yuklu/C_k[k]*100 if C_k[k]>0 else 0,
            "tip": tip_k[k], "alan": alan_k[k], "kullananlar": kullananlar
        }

    return {
        "durum": durum,
        "obj_val": m.ObjVal,
        "saf_mesafe": saf_mesafe,
        "toplam_ceza": toplam_ceza,
        "ihlaller": ihlaller,
        "mip_gap": m.MIPGap * 100,
        "sure": sure,
        "sonuc_kat": sonuc_kat,
        "blok_ozet": blok_ozet,
        "acik_yeni": [j for j in K_new if Y and Y[j].X > 0.5],
        "U_i": U_i, "C_k": C_k, "alan_k": alan_k, "kod_i": kod_i,
        "kod_adi": veri.get("kod_adi",{}), "I": I, "K": K,
        "K_alan": K_alan, "alanlar": alanlar
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--excel",default="Parametreler_31Raf_12Lokasyon.xlsx")
    parser.add_argument("--bmax",type=int,default=B_MAX)
    parser.add_argument("--kor",type=int,default=MAX_KORIDOR)
    parser.add_argument("--sure",type=int,default=300)
    parser.add_argument("--gap",type=float,default=0.01)
    args=parser.parse_args()

    dosya=Path(args.excel)
    if not dosya.exists(): sys.exit(f"HATA: '{dosya}' bulunamadi.")

    print(f"{C.BOLD}Veri okunuyor: {dosya}{C.RESET}")
    veri=excel_oku(str(dosya))
    print(f"  Kategoriler: {len(veri['I'])} | Bloklar: {len(veri['K'])} | Alanlar: {veri['alanlar']}")
    print(f"  Toplam talep: {sum(veri['U_i'].values()):.0f} | Kapasite: {sum(veri['C_k'].values()):.0f}")

    if not feasibility_kontrol(veri): sys.exit(1)

    sonuc=model_calistir(str(dosya),b_max=args.bmax,max_kor=args.kor,
                         t_limit=args.sure,mip_gap=args.gap)
    cikti_yazdir(sonuc)

if __name__=="__main__":
    main()
