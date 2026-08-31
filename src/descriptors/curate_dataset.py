"""
curate_dataset.py
Curates a comprehensive library of 42 organic small-molecule drugs relevant for 
Triple-Negative Breast Cancer (TNBC) including PARP inhibitors, anthracyclines, 
taxanes, targeted kinase inhibitors, PI3K/mTOR/AXL pathway modulators, and ADC payloads.
"""

import os
import json
import pandas as pd

TNBC_DRUG_LIBRARY = [
    # 1. PARP Inhibitors (Standard of Care for BRCA-mutated TNBC)
    {"name": "Olaparib", "class": "PARP Inhibitor", "smiles": "O=C(c1cc(Cc2n[nH]c(=O)c3ccccc23)ccc1F)N1CCN(C(=O)C2CC2)CC1", "drugbank_id": "DB00140"},
    {"name": "Talazoparib", "class": "PARP Inhibitor", "smiles": "FC(F)(c1ccc(cc1)[C@H]1c2cc(F)ccc2N[C@@H]2C(=O)NN=C12)F", "drugbank_id": "DB11760"},
    {"name": "Rucaparib", "class": "PARP Inhibitor", "smiles": "CNCc1ccc(-c2cc3[nH]c2CCNC(=O)c2cccc(F)c2-3)cc1", "drugbank_id": "DB12331"},
    {"name": "Niraparib", "class": "PARP Inhibitor", "smiles": "NC(=O)c1cccc(c1)[C@@H]1CCCN(Cc2ccc3ncccc3c2)C1", "drugbank_id": "DB12340"},
    {"name": "Veliparib", "class": "PARP Inhibitor", "smiles": "CC1(NC(=O)c2cccc3[nH]c(C)nc23)CCCN1", "drugbank_id": "DB11692"},
    {"name": "Pamiparib", "class": "PARP Inhibitor", "smiles": "C[C@]12CCCN1CC3=NNC(=O)C4=C5C3=C2NC5=CC(=C4)F", "drugbank_id": "DB15002"},

    # 2. Targeted Kinase & Pathway Modulators in TNBC Clinical Trials
    {"name": "Everolimus", "class": "mTOR Inhibitor", "smiles": "CO[C@@H]1C[C@H](C)CC[C@@H](C)[C@@H](O)[C@@H](OC)C(=O)[C@H](C)C[C@H](C)\C=C\C=C\C=C\[C@H](C)[C@H](O)C(=O)C(C)(C)[C@@H](O)C(=O)N2CCCC[C@H]2C(=O)O1", "drugbank_id": "DB00444"},
    {"name": "Buparlisib", "class": "PI3K Inhibitor", "smiles": "Cc1nc(nc(n1)N1CCOCC1)-c1ccc(F)c(N2CCOCC2)c1", "drugbank_id": "DB12128"},
    {"name": "Cediranib", "class": "VEGFR/c-Kit Inhibitor", "smiles": "COc1cc2ncnc(Nc3ccc4[nH]c(C)nc4c3F)c2cc1OCC1CCN(C)CC1", "drugbank_id": "DB06436"},
    {"name": "Paxalisib", "class": "PI3K/mTOR Inhibitor", "smiles": "CC(C)(C)c1nc(nc(n1)N1CCOCC1)-c1cnc(N2CCOCC2)nc1N", "drugbank_id": "DB15438"},

    # 3. Anthracyclines & Topoisomerase Inhibitors
    {"name": "Doxorubicin", "class": "Anthracycline", "smiles": "COc1cccc2C(=O)c3c(O)c4C[C@](O)(C(=O)CO)C[C@@H](O[C@H]5C[C@H](N)[C@H](O)[C@H](C)O5)c4c(O)c3C(=O)c12", "drugbank_id": "DB00997"},
    {"name": "Epirubicin", "class": "Anthracycline", "smiles": "COc1cccc2C(=O)c3c(O)c4C[C@](O)(C(=O)CO)C[C@@H](O[C@H]5C[C@H](N)[C@@H](O)[C@H](C)O5)c4c(O)c3C(=O)c12", "drugbank_id": "DB00445"},
    {"name": "Idarubicin", "class": "Anthracycline", "smiles": "CC(=O)[C@@]1(O)Cc2c(O)c3C(=O)c4ccccc4C(=O)c3c(O)c2C[C@@H]1O[C@H]1C[C@H](N)[C@H](O)[C@H](C)O1", "drugbank_id": "DB00642"},
    {"name": "Topotecan", "class": "Topoisomerase I Inhibitor", "smiles": "CCC1(O)C(=O)OCc2c1cc1-c3nc4cc(O)c(CN(C)C)cc4cc3Cn1c2=O", "drugbank_id": "DB01030"},
    {"name": "Irinotecan", "class": "Topoisomerase I Inhibitor", "smiles": "CCC1(O)C(=O)OCc2c1cc1-c3nc4ccc(OC(=O)N5CCC(CC5)N5CCCCC5)cc4cc3Cn1c2=O", "drugbank_id": "DB00762"},
    {"name": "SN-38", "class": "Topoisomerase I Inhibitor / ADC Payload", "smiles": "CCC1(O)C(=O)OCc2c1cc1-c3nc4ccc(O)cc4cc3Cn1c2=O", "drugbank_id": "DB05482"},
    {"name": "Etoposide", "class": "Topoisomerase II Inhibitor", "smiles": "COc1cc([C@@H]2c3cc4OCOc4cc3[C@@H](O[C@@H]3O[C@@H]4CO[C@@H](C)O[C@@H]4[C@H](O)[C@H]3O)[C@H]3COC(=O)[C@H]23)cc(OC)c1O", "drugbank_id": "DB00773"},

    # 4. Antimetabolites
    {"name": "Gemcitabine", "class": "Antimetabolite", "smiles": "Nc1ccn([C@@H]2O[C@H](CO)[C@@H](O)C2(F)F)c(=O)n1", "drugbank_id": "DB00441"},
    {"name": "Capecitabine", "class": "Antimetabolite", "smiles": "CCCCCOC(=O)Nc1nc(=O)n([C@@H]2O[C@H](C)[C@@H](O)[C@H]2O)cc1F", "drugbank_id": "DB01101"},
    {"name": "Fluorouracil", "class": "Antimetabolite", "smiles": "O=c1[nH]cc(F)c(=O)[nH]1", "drugbank_id": "DB00544"},
    {"name": "Methotrexate", "class": "Antifolate", "smiles": "CN(Cc1cnc2nc(N)nc(N)c2n1)c1ccc(C(=O)N[C@@H](CCC(=O)O)C(=O)O)cc1", "drugbank_id": "DB00563"},
    {"name": "Pemetrexed", "class": "Antifolate", "smiles": "Nc1nc2[nH]c(CCc3ccc(cc3)C(=O)N[C@@H](CCC(=O)O)C(=O)O)cc2c(=O)[nH]1", "drugbank_id": "DB00643"},
    {"name": "Cytarabine", "class": "Antimetabolite", "smiles": "Nc1ccn([C@@H]2O[C@H](CO)[C@@H](O)[C@@H]2O)c(=O)n1", "drugbank_id": "DB00503"},

    # 5. Microtubule Disruptors & Taxanes
    {"name": "Paclitaxel", "class": "Taxane", "smiles": "CC(=O)O[C@H]1C(=O)[C@]2(C)[C@@H](O)C[C@H]3OCC3(OC(C)=O)[C@H]2[C@H](OC(=O)c2ccccc2)[C@]2(O)C[C@H](OC(=O)[C@H](O)[C@@H](NC(=O)c3ccccc3)c3ccccc3)C(C)=C1C2(C)C", "drugbank_id": "DB01204"},
    {"name": "Docetaxel", "class": "Taxane", "smiles": "CC(C)(C)OC(=O)N[C@@H](c1ccccc1)[C@@H](O)C(=O)O[C@H]1C[C@@]2(O)[C@H](OC(=O)c3ccccc3)[C@H]3[C@]4(OC(C)=O)CO[C@@]4(C[C@@H](O)[C@]3(C)C(=O)[C@H](O)C(=C1C)C2(C)C)OC(=O)C", "drugbank_id": "DB01248"},
    {"name": "Cabazitaxel", "class": "Taxane", "smiles": "CC(C)(C)OC(=O)N[C@@H](c1ccccc1)[C@@H](O)C(=O)O[C@H]1C[C@@]2(O)[C@H](OC(=O)c3ccccc3)[C@H]3[C@]4(OC(C)=O)CO[C@@]4(C[C@@H](OC)[C@]3(C)C(=O)[C@H](OC)C(=C1C)C2(C)C)OC(=O)C", "drugbank_id": "DB08868"},
    {"name": "Vinorelbine", "class": "Vinca Alkaloid", "smiles": "CCC1=C[C@@H]2C[C@@](C1)(c1c([nH]c3ccccc13)[C@@]1(CO2)C[C@H]2N(C)c3ccccc3[C@@]23C=CCN4CC[C@]13[C@H]4CC)C(=O)OC", "drugbank_id": "DB00361"},
    {"name": "Vinblastine", "class": "Vinca Alkaloid", "smiles": "CCC1(O)C[C@@H]2C[C@@](C1)(c1c([nH]c3ccccc13)[C@]3(O)C[C@H]2N(C)c1ccccc1[C@]34C=CCN1CC[C@@]41CC)C(=O)OC", "drugbank_id": "DB00570"},
    {"name": "Ixabepilone", "class": "Epothilone", "smiles": "CC1CCCC(C)(C)[C@@H](O)CC(=O)N[C@H](C)[C@@H](O)[C@@H](C)/C(=C/c2nc(C)cs2)C1(C)C", "drugbank_id": "DB04845"},
    {"name": "Eribulin", "class": "Halichondrin B Analog", "smiles": "C=C1[C@H]2C[C@H]3O[C@]4(O[C@H]5C[C@@H]6O[C@]7(C[C@H]8O[C@@H]9[C@H](C)C(=C)C[C@@]9(O[C@@H]8C[C@H]7C5)C6)[C@H]4CC[C@@H]3O2)C[C@@H]1O", "drugbank_id": "DB08871"},

    # 6. Targeted Receptor Tyrosine Kinase & CDK4/6 Inhibitors
    {"name": "Lapatinib", "class": "EGFR/HER2 Inhibitor", "smiles": "CS(=O)(=O)CCNCc1ccc(-c2ccc3ncnc(Nc4ccc(OCc5cccc(F)c5)c(Cl)c4)c3c2)o1", "drugbank_id": "DB01259"},
    {"name": "Gefitinib", "class": "EGFR Inhibitor", "smiles": "COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1OCCCN1CCOCC1", "drugbank_id": "DB00317"},
    {"name": "Erlotinib", "class": "EGFR Inhibitor", "smiles": "COCCOc1cc2ncnc(Nc3cccc(C#C)c3)c2cc1OCCOC", "drugbank_id": "DB00530"},
    {"name": "Afatinib", "class": "EGFR Inhibitor", "smiles": "CN(C)C/C=C/C(=O)Nc1cc2c(Nc3ccc(F)c(Cl)c3)ncnc2cc1O[C@H]1CCOC1", "drugbank_id": "DB08907"},
    {"name": "Bemcentinib", "class": "AXL Kinase Inhibitor", "smiles": "Cc1ccc(cc1)N1CCN(CC1)c1nc2ccccc2c(Nc2ccc(cc2)c2ccccc2)n1", "drugbank_id": "DB12411"},
    {"name": "Capivasertib", "class": "AKT Inhibitor", "smiles": "CN1CCN(c2nc(C3CC3)c3c(N)ncnc3n2)CC1.Clc1ccc(C2CCNCC2)cc1", "drugbank_id": "DB15259"},
    {"name": "Alpelisib", "class": "PI3Kalpha Inhibitor", "smiles": "CC(C)(C(=O)N)c1nc(nc(c1)-c1nc(NC(=O)N[C@@H](C)c2ccccc2)cs1)N1CCCC1", "drugbank_id": "DB12001"},
    {"name": "Palbociclib", "class": "CDK4/6 Inhibitor", "smiles": "CC(=O)c1c(C)c2cnc(Nc3ccc(N4CCNCC4)cn3)nc2n(C2CCCC2)c1=O", "drugbank_id": "DB09073"},
    {"name": "Ribociclib", "class": "CDK4/6 Inhibitor", "smiles": "CN(C)C(=O)c1cnc(Nc2ccc(N3CCN(C)CC3)cn2)nc1N1CCCC1", "drugbank_id": "DB09075"},
    {"name": "Abemaciclib", "class": "CDK4/6 Inhibitor", "smiles": "CCN1CCN(Cc2ccc(Nc3ncc(F)c(Nc4ccc5c(c4)n(C(C)C)c(=O)n5C)n3)cn2)CC1", "drugbank_id": "DB12001"},

    # 7. Additional Targeted & ADC Payloads
    {"name": "Exatecan", "class": "Topoisomerase I Inhibitor / DXd precursor", "smiles": "CCC1(O)C(=O)OCc2c1cc1-c3nc4c(F)c(C)c(N)c(F)c4cc3Cn1c2=O", "drugbank_id": "DB04982"},
    {"name": "Monomethyl auristatin E", "class": "Tubulin Inhibitor / ADC Payload (MMAE)", "smiles": "CCC(C)[C@H](NC(=O)[C@H](C)NC(=O)[C@H](CC(C)C)NC(=O)[C@H](C)NC)C(=O)N[C@@H]([C@@H](C)CC)C(=O)N1CCC[C@H]1[C@@H](OC)[C@@H](C)C(=O)N[C@H](CO)c1ccccc1", "drugbank_id": "DB06161"}
]

def export_library():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out_dir = os.path.join(base_dir, "data", "raw")
    os.makedirs(out_dir, exist_ok=True)
    
    df = pd.DataFrame(TNBC_DRUG_LIBRARY)
    csv_path = os.path.join(out_dir, "tnbc_drug_library.csv")
    json_path = os.path.join(out_dir, "tnbc_drug_library.json")
    
    df.to_csv(csv_path, index=False)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(TNBC_DRUG_LIBRARY, f, indent=2)
        
    print(f"Successfully curated {len(TNBC_DRUG_LIBRARY)} TNBC drugs.")
    return df

if __name__ == "__main__":
    export_library()
