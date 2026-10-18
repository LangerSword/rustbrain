scripts/verify_readme_numbers.py output, run 2026-10-19.
Every README coverage figure re-derived from data/snapshot.json.

measure                                                  value    rate / note
labels total                                             19       
labels resolving to an ACTIVE team                       14       73.7%
labels resolving to ANY file                             17       89.5%
labels with no file at all                               2        dev-tools, doc
RFCs total                                               761      
RFCs with >=1 active-team label                          357      46.9%
documents present on RFC nodes                           626      
distinct authors                                         242      
authors on an active team                                85       35.1%
orphan-author RFCs (no people file)                      169      22.2%
orphan-author RFCs that carried merge                    41       
RFCs with no current member AND no alumni record         169      22.2%
successor edges                                          4        
teams total / active                                     224 / 172 
roster edges (lead+member)                               1177     
people                                                   675      

README claims, asserted one by one. A mismatch here means the README is wrong.
  labels -> active team is 73.7% (14/19)                   OK
  labels -> any file is 89.5% (17/19)                      OK
  RFCs with an active-team label is 46.9% (357/761)        OK
  RFCs with any-file label is 63.9% (486/761)              OK
  RFCs with no label at all is 34.2% (260/761)             OK
  numbered RFC files joining to a merged RFC is 96.0% (626/652) OK
  authors on an active team over 761 RFCs is 35.1% (85/242) OK
  no membership and no alumni is 22.2% (169/761)           OK

VERDICT: PASS, every README number reproduces
