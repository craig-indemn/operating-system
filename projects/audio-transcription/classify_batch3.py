#!/usr/bin/env python3
"""
Classify 309 calls from batch 3 into engagement types.
Uses rule-based keyword/pattern matching on caller_intent and summary fields.
"""

import json
import re
from collections import defaultdict

INPUT_FILE = '/Users/home/Repositories/operating-system/projects/audio-transcription/classify_batch_3.jsonl'
OUTPUT_FILE = '/Users/home/Repositories/operating-system/projects/audio-transcription/classify_result_3.json'

# Load all calls
calls = []
with open(INPUT_FILE, 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            calls.append(json.loads(line))

print(f"Loaded {len(calls)} calls")


def classify_call(call):
    """Classify a single call. Returns (engagement_type, confidence)."""
    intent = (call.get('caller_intent') or '').lower()
    summary = (call.get('summary') or '').lower()
    text = intent + ' ' + summary
    resolution = ' '.join(call.get('resolution_steps', [])).lower()
    knowledge = ' '.join(call.get('knowledge_required', [])).lower()
    systems = ' '.join(call.get('systems_referenced', [])).lower()
    all_text = text + ' ' + resolution + ' ' + knowledge + ' ' + systems

    # Score each type
    scores = {}

    # === MAKE-PAYMENT ===
    s = 0
    if re.search(r'\b(make|process|submit|take)\b.{0,30}\bpayment\b', text): s += 10
    if re.search(r'\bpay\b.{0,20}\b(bill|premium|balance|amount|policy)\b', text): s += 8
    if re.search(r'\b(auto.?pay|autopay|eft|bank draft|automatic payment|recurring payment)\b', text): s += 8
    if re.search(r'\bset up.{0,20}(payment|auto.?pay|draft|eft)\b', text): s += 9
    if re.search(r'\bdown payment\b', text): s += 9
    if re.search(r'\bpayment\b.*\b(credit card|debit card|bank account|routing|account number)\b', text): s += 7
    if re.search(r'\bwants to pay\b', text): s += 9
    if re.search(r'\bmake a payment\b', text): s += 10
    if re.search(r'\bpayment processing\b', all_text): s += 3
    if re.search(r'\bcatch up\b.*\b(payment|balance)\b', text): s += 7
    # Negative: if it's about questioning a charge, that's billing
    if re.search(r'\b(confus|unexpected|discrepanc|disput|question|why|clarif|overcharg)\b', text): s -= 5
    scores['make-payment'] = s

    # === BILLING-QUESTION ===
    s = 0
    if re.search(r'\b(unexpected|confus|discrepanc|disput|question|clarif)\b.{0,40}\b(charge|bill|amount|premium|payment|rate|price)\b', text): s += 9
    if re.search(r'\b(charge|bill|amount|premium)\b.{0,40}\b(unexpected|confus|discrepanc|disput|question|clarif|why|incorrect|wrong)\b', text): s += 9
    if re.search(r'\bwhy.{0,30}(charge|bill|premium|amount|increas|rate|higher)\b', text): s += 8
    if re.search(r'\brefund\b', text): s += 6
    if re.search(r'\b(overcharg|double.?charg|duplicate.?charg)\b', text): s += 9
    if re.search(r'\b(billing|bill)\b.{0,20}\b(inquiry|question|concern|issue|confusion)\b', text): s += 8
    if re.search(r'\bexplanation\b.{0,20}\b(charge|bill|premium)\b', text): s += 7
    if re.search(r'\bpayment status\b', text): s += 4
    if re.search(r'\bunexpected.{0,20}(increase|amount|charge|bill)\b', text): s += 8
    if re.search(r'\bpremium\b.{0,20}\b(discrepanc|incorrect|wrong|confus)\b', text): s += 8
    # Escrow/mortgage billing goes to mortgage-lender
    if re.search(r'\bescrow\b', text): s -= 5
    scores['billing-question'] = s

    # === NEW-QUOTE ===
    s = 0
    if re.search(r'\b(new|get|obtain|request|need|seeking|shop)\b.{0,30}\b(quote|insurance|coverage|policy)\b', text) and re.search(r'\bquote\b', text): s += 9
    if re.search(r'\bquote\b', text) and not re.search(r'\bfollow.?up\b', text): s += 5
    if re.search(r'\bshopping\b', text): s += 7
    if re.search(r'\bnew.{0,10}(insurance|policy|coverage)\b', text) and not re.search(r'\b(add|vehicle|driver|car)\b', text): s += 6
    if re.search(r'\b(home|auto|renters?|commercial|life|liability|moped|motorcycle|boat|flood)\b.{0,20}\b(quote|insurance)\b', text) and re.search(r'\bquote\b', text): s += 7
    if re.search(r'\bprice comparison\b', text): s += 6
    if re.search(r'\bbetter rate\b', text) and not re.search(r'\bcancel\b', text): s += 4
    if re.search(r'\bnew (construction |cleaning |landscaping )?(company|business|llc)\b', text): s += 5
    if re.search(r'\bquote follow.?up\b', text): s += 6
    if re.search(r'\binsurance for\b.{0,40}\b(new|start)\b', text): s += 5
    # General quote requests
    if re.search(r'\bseeking.{0,30}(insurance|quote|coverage)\b', text) and not re.search(r'\b(cancel|change|modif|add|remove)\b', text): s += 5
    scores['new-quote'] = s

    # === VEHICLE-CHANGE ===
    s = 0
    if re.search(r'\b(add|adding)\b.{0,30}\b(vehicle|car|truck|van|suv|auto)\b', text): s += 9
    if re.search(r'\b(remove|removing)\b.{0,30}\b(vehicle|car|truck|van|suv|auto)\b', text): s += 9
    if re.search(r'\b(swap|replace|switch|trade)\b.{0,30}\b(vehicle|car|truck|van|auto)\b', text): s += 9
    if re.search(r'\b(new|newly|just|recently)\b.{0,20}\b(purchased|bought|acquired)\b.{0,30}\b(vehicle|car|truck|van|suv)\b', text): s += 8
    if re.search(r'\b(sold|totaled|wrecked|traded)\b.{0,30}\b(vehicle|car|truck|van|suv)\b', text): s += 7
    if re.search(r'\badd a car\b', text): s += 10
    if re.search(r'\bremove.{0,10}(a |the )?(vehicle|car|truck)\b', text): s += 9
    if re.search(r'\b(vehicle|car)\b.{0,20}\b(to|from|on)\b.{0,20}\b(policy|insurance)\b', text): s += 5
    if re.search(r'\b20\d{2}\b.{0,30}\b(toyota|honda|ford|chevy|chevrolet|nissan|hyundai|kia|ram|dodge|jeep|bmw|mercedes|subaru|mazda|lexus|audi|volkswagen|vw|gmc|buick|cadillac|lincoln|chrysler|acura|infiniti|volvo|tesla|mitsubishi|fiat|mini|porsche|rav4|camry|civic|altima|corolla|accord|f-150|silverado|tahoe|explorer|escape|wrangler|mustang|charger|challenger|durango|frontier|rogue|pathfinder|sentra|elantra|sonata|tucson|santa fe|forte|optima|soul|sorento|sportage|outback|forester|impreza|crosstrek|cx-5|cx-9|mazda3|mazda6|rx|nx|is|es|a4|a6|q5|q7|jetta|passat|tiguan|atlas|terrain|acadia|encore|enclave|xt4|xt5|mkc|mkz|navigator|300|pacifica|rdx|tlx|mdx|qx50|qx60|xc40|xc60|xc90|model 3|model y|outlander|eclipse|cooper|cayenne|macan)\b', text): s += 4
    # Adding a newly purchased vehicle
    if re.search(r'\bnewly purchased\b', text): s += 7
    scores['vehicle-change'] = s

    # === DRIVER-CHANGE ===
    s = 0
    if re.search(r'\b(add|adding)\b.{0,30}\b(driver|person)\b', text): s += 9
    if re.search(r'\b(remove|removing)\b.{0,30}\b(driver|person)\b', text): s += 9
    if re.search(r'\b(add|remove)\b.{0,30}\b(daughter|son|spouse|wife|husband|teen|child|kid)\b.{0,30}\b(policy|insurance|driver)\b', text): s += 8
    if re.search(r'\b(daughter|son|teen|child)\b.{0,30}\b(license|permit|driving|driver)\b', text): s += 7
    if re.search(r'\blearner.?s? permit\b', text): s += 8
    if re.search(r'\b(add|remove).{0,10}(to|from).{0,10}(policy|insurance)\b.*\b(daughter|son|spouse|driver)\b', text): s += 7
    if re.search(r'\bdriver\b.{0,20}\b(to|from|on)\b.{0,20}\bpolicy\b', text): s += 6
    if re.search(r'\bexclude\b.{0,20}\bdriver\b', text): s += 7
    scores['driver-change'] = s

    # === COVERAGE-MODIFICATION ===
    s = 0
    if re.search(r'\b(change|modify|adjust|increase|decrease|raise|lower|update)\b.{0,30}\b(deductible|coverage|limit|liability)\b', text): s += 9
    if re.search(r'\b(add|remove|drop)\b.{0,30}\b(coverage|collision|comprehensive|comp|towing|roadside|umbrella|uninsured|underinsured|rental|gap|pip|med.?pay)\b', text): s += 9
    if re.search(r'\bdeductible\b', text) and re.search(r'\b(change|modify|adjust|increase|decrease|raise|lower)\b', text): s += 8
    if re.search(r'\bumbrella\b.{0,30}\b(increase|add|raise|from|to)\b', text): s += 7
    if re.search(r'\b(full|comprehensive|collision)\b.{0,10}\bcoverage\b', text) and re.search(r'\b(add|remove|drop|change)\b', text): s += 7
    if re.search(r'\bcoverage modification\b', text): s += 10
    if re.search(r'\b(increase|decrease)\b.{0,20}\b(limits?|coverage|liability)\b', text): s += 7
    if re.search(r'\bremove.{0,20}(towing|roadside|rental|comp|comprehensive|collision)\b', text): s += 8
    if re.search(r'\bdowngrade\b', text): s += 6
    if re.search(r'\bliability only\b', text): s += 5
    scores['coverage-modification'] = s

    # === CANCELLATION ===
    s = 0
    if re.search(r'\bcancel\b.{0,30}\b(policy|insurance|coverage|account)\b', text): s += 10
    if re.search(r'\bcancellation\b', text) and not re.search(r'\breinstat\b', text): s += 7
    if re.search(r'\bcancel\b', text) and re.search(r'\b(policy|insurance)\b', text): s += 8
    if re.search(r'\bwants to cancel\b', text): s += 10
    if re.search(r'\b(selling|sold|closing|moving|relocat|switch|found better|better rate|leaving)\b', text) and re.search(r'\bcancel\b', text): s += 5
    if re.search(r'\b(cancel|terminat|end|stop)\b.{0,20}\b(policy|insurance|coverage)\b', text): s += 8
    # If it's about cancellation due to non-payment and wanting reinstatement, that's reinstatement
    if re.search(r'\breinstat\b', text): s -= 10
    if re.search(r'\bcanceled\b.*\breinstat\b', text): s -= 10
    scores['cancellation'] = s

    # === REINSTATEMENT ===
    s = 0
    if re.search(r'\breinstat\b', text): s += 10
    if re.search(r'\b(cancel|lapse)\b.{0,40}\b(reinstat|reactivat|restore)\b', text): s += 9
    if re.search(r'\b(reinstat|reactivat|restore)\b.{0,40}\b(policy|insurance|coverage)\b', text): s += 9
    if re.search(r'\bnon.?payment\b', text) and re.search(r'\b(reinstat|reactivat)\b', text): s += 8
    if re.search(r'\bcanceled\b.{0,40}\b(non.?payment|lapse)\b', text) and not re.search(r'\bwants to cancel\b', text): s += 5
    if re.search(r'\breinstatement\b', text): s += 10
    scores['reinstatement'] = s

    # === CLAIMS ===
    s = 0
    if re.search(r'\b(file|report|open|submit|make)\b.{0,20}\b(claim|accident|incident)\b', text): s += 9
    if re.search(r'\bclaim\b', text) and re.search(r'\b(file|report|damage|accident|stolen|theft|hit|wreck|crash|collision|flood|fire|hail|storm|vandal|break.?in|burglary)\b', text): s += 8
    if re.search(r'\baccident\b', text) and re.search(r'\b(report|file|claim|insurance)\b', text): s += 7
    if re.search(r'\b(stolen|theft)\b', text) and re.search(r'\b(report|claim|file)\b', text): s += 8
    if re.search(r'\b(adjuster|settlement|claim status|claim number|claim follow)\b', text): s += 7
    if re.search(r'\bdamage\b.{0,30}\b(claim|report|file)\b', text): s += 7
    if re.search(r'\bhit.{0,10}(a |the |my )?(car|vehicle|truck|deer|pole|tree|mailbox|fence|garage)\b', text): s += 6
    if re.search(r'\b(water|wind|hail|storm|flood|fire|lightning|tornado|hurricane)\b.{0,30}\b(damage|claim)\b', text): s += 7
    if re.search(r'\bclaim assistance\b', text): s += 8
    if re.search(r'\bclaim\b', text): s += 3
    scores['claims'] = s

    # === RENEWAL-REVIEW ===
    s = 0
    if re.search(r'\brenewal\b', text): s += 6
    if re.search(r'\b(renewal|renew)\b.{0,30}\b(review|premium|rate|increase|policy)\b', text): s += 8
    if re.search(r'\b(rate|premium)\b.{0,30}\b(increase|went up|higher|change|review|compare|shop)\b', text) and not re.search(r'\bquote\b', text): s += 7
    if re.search(r'\brate.?review\b', text): s += 9
    if re.search(r'\b(best option|better rate|competitive|shop around|compare)\b', text) and re.search(r'\b(renewal|existing|current|policy)\b', text): s += 6
    if re.search(r'\b(rate|premium).{0,20}(went up|increased|jumped|doubled|higher)\b', text): s += 7
    if re.search(r'\bbundle\b', text) and re.search(r'\b(discount|save|savings)\b', text): s += 5
    if re.search(r'\bwhy.{0,20}(rate|premium|price|cost).{0,20}(went up|increased|higher|more)\b', text): s += 7
    scores['renewal-review'] = s

    # === COI-REQUEST ===
    s = 0
    if re.search(r'\bcertificate of insurance\b', text): s += 10
    if re.search(r'\bcoi\b', text): s += 8
    if re.search(r'\bcertificate\b.{0,30}\b(insurance|liability|coverage)\b', text): s += 9
    if re.search(r'\b(additional insured|add.{0,10}insured)\b', text): s += 7
    if re.search(r'\bcertificate\b', text) and re.search(r'\b(send|email|fax|provide|generate|issue|need|request|update)\b', text): s += 6
    if re.search(r'\bcert\b.{0,10}\b(insurance|liability)\b', text): s += 7
    scores['coi-request'] = s

    # === DOCUMENT-REQUEST ===
    s = 0
    if re.search(r'\b(copy|copies)\b.{0,30}\b(policy|declaration|dec page|id card|proof|document)\b', text): s += 9
    if re.search(r'\b(declaration|dec) page\b', text): s += 8
    if re.search(r'\bproof of (insurance|coverage)\b', text): s += 8
    if re.search(r'\bid card\b', text) and re.search(r'\b(insurance|policy)\b', text): s += 8
    if re.search(r'\bloss run\b', text): s += 9
    if re.search(r'\b(send|email|fax|provide|need)\b.{0,30}\b(copy|document|proof|declaration|id card|loss run|bond)\b', text): s += 6
    if re.search(r'\bbinder\b', text) and re.search(r'\b(send|email|need|provide|request)\b', text): s += 6
    if re.search(r'\binsurance card\b', text): s += 7
    if re.search(r'\bdocument\b.{0,20}\b(request|need|send|email)\b', text): s += 5
    # Negative: COI requests are different
    if re.search(r'\bcertificate of insurance\b', text): s -= 5
    if re.search(r'\bcoi\b', text): s -= 5
    scores['document-request'] = s

    # === DMV-COMPLIANCE ===
    s = 0
    if re.search(r'\bdmv\b', text): s += 8
    if re.search(r'\bfs.?1\b', text): s += 10
    if re.search(r'\bplate revocation\b', text): s += 9
    if re.search(r'\bdot number\b', text): s += 8
    if re.search(r'\b(registration|tag|plate)\b.{0,30}\b(revok|suspend|cancel|lapse)\b', text): s += 8
    if re.search(r'\bcompliance\b.{0,20}\b(dmv|dot|state|registration)\b', text): s += 7
    if re.search(r'\bfr.?44\b', text): s += 9
    if re.search(r'\bsr.?22\b', text): s += 9
    scores['dmv-compliance'] = s

    # === MORTGAGE-LENDER ===
    s = 0
    if re.search(r'\b(mortgage|mortgagee|lender|lienholder|lien holder|escrow)\b', text): s += 7
    if re.search(r'\bescrow\b.{0,30}\b(payment|increase|amount|issue)\b', text): s += 9
    if re.search(r'\bmortgage company\b', text): s += 8
    if re.search(r'\b(lienholder|lien holder)\b', text): s += 8
    if re.search(r'\b(add|update|change|remove)\b.{0,30}\b(mortgage|lienholder|lien holder|mortgagee)\b', text): s += 8
    if re.search(r'\b(lender|mortgage)\b.{0,30}\b(proof|need|require|request)\b', text): s += 7
    if re.search(r'\bhomeowner.{0,10}insurance\b.*\b(mortgage|lender|escrow|closing)\b', text): s += 6
    if re.search(r'\bclosing\b', text) and re.search(r'\b(mortgage|lender|loan|house|home)\b', text): s += 5
    scores['mortgage-lender'] = s

    # === WORKERS-COMP ===
    s = 0
    if re.search(r'\bworkers?.{0,3}comp\b', text): s += 10
    if re.search(r'\bwork comp\b', text): s += 9
    if re.search(r'\b(audit|class code|payroll)\b', text) and re.search(r'\bworkers?.{0,3}comp\b', all_text): s += 7
    if re.search(r'\bghost policy\b', text): s += 8
    if re.search(r'\baudit\b', text) and re.search(r'\b(workers|comp|payroll|class code)\b', text): s += 7
    if re.search(r'\bclass code\b', text): s += 5
    if re.search(r'\bpayroll report\b', text): s += 5
    scores['workers-comp'] = s

    # === INFO-UPDATE ===
    s = 0
    if re.search(r'\b(update|change|correct|modify)\b.{0,30}\b(address|phone|email|name|contact|mailing)\b', text): s += 9
    if re.search(r'\b(address|phone|email|name)\b.{0,30}\b(update|change|correct|modify|new)\b', text): s += 7
    if re.search(r'\b(moved|new address|address change)\b', text): s += 7
    if re.search(r'\b(divorce|marriage|married|maiden)\b', text) and re.search(r'\b(name|last name)\b', text): s += 8
    if re.search(r'\b(dba|doing business as)\b', text) and re.search(r'\b(update|change|add)\b', text): s += 7
    if re.search(r'\bupdate\b.{0,20}\b(policy|account|information|info)\b', text) and not re.search(r'\b(coverage|deductible|limit|vehicle|driver|cancel)\b', text): s += 4
    if re.search(r'\bpayment method\b', text) and re.search(r'\b(update|change)\b', text): s += 6
    if re.search(r'\bemail address\b', text) and re.search(r'\b(update|change)\b', text): s += 8
    if re.search(r'\bchange.{0,10}(last |sur)?name\b', text): s += 8
    scores['info-update'] = s

    # === COVERAGE-QUESTION ===
    s = 0
    if re.search(r'\b(am i|are (we|they)|is (it|this|that|my))\b.{0,20}\bcovered\b', text): s += 9
    if re.search(r'\b(does|do|will|would)\b.{0,20}\b(policy|insurance|coverage)\b.{0,20}\bcover\b', text): s += 8
    if re.search(r'\bcoverage\b.{0,20}\b(question|clarif|inquiry|concern)\b', text): s += 8
    if re.search(r'\bwhat.{0,10}(does|is).{0,20}(covered|cover|include)\b', text): s += 7
    if re.search(r'\bcovered for\b', text): s += 7
    if re.search(r'\bcoverage.{0,10}(include|exclude)\b', text): s += 7
    if re.search(r'\binquir\b.{0,30}\b(coverage|covered)\b', text): s += 7
    if re.search(r'\bcover\b.{0,20}\b(lawsuit|damage|flood|theft|rental|towing)\b', text) and not re.search(r'\b(add|change|modify|remove)\b', text): s += 5
    scores['coverage-question'] = s

    # === COMMERCIAL-SPECIALTY ===
    s = 0
    if re.search(r"\bbuilder.?s?.{0,3}risk\b", text): s += 9
    if re.search(r'\b(vacant|unoccupied)\b.{0,20}\b(property|building|house)\b', text): s += 8
    if re.search(r'\b(surety )?bond\b', text) and re.search(r'\b(need|request|quote|insurance)\b', text): s += 6
    if re.search(r'\b(hoa|homeowners? association|church|preschool|daycare|school)\b', text) and re.search(r'\b(insurance|policy|coverage|program)\b', text): s += 7
    if re.search(r'\b(dealer|dealership)\b.{0,20}\b(lot|insurance|bond)\b', text): s += 8
    if re.search(r'\b(special event|liquor liability|farm|ranch|crop)\b', text): s += 7
    if re.search(r'\b(commercial|business)\b.{0,20}\b(insurance|policy|coverage|specialty|question|inquiry)\b', text) and not re.search(r'\b(cancel|payment|renew|billing|claim)\b', text): s += 4
    if re.search(r'\b(umbrella|excess|e&o|errors and omissions|professional liability|cyber|inland marine|garage keeper|bailees)\b', text) and re.search(r'\bcommercial\b', text): s += 5
    if re.search(r'\b(nonprofit|non.?profit|ministry|church)\b', text): s += 5
    if re.search(r'\b(notary|mobile.?notary|notary.?bond)\b', text): s += 6
    scores['commercial-specialty'] = s

    # === FOLLOW-UP ===
    s = 0
    if re.search(r'\bfollow.?up\b', text): s += 7
    if re.search(r'\b(check|checking)\b.{0,20}\b(status|progress|update)\b', text): s += 6
    if re.search(r'\bstatus\b.{0,20}\b(quote|policy|request|change|claim|document|application)\b', text): s += 6
    if re.search(r'\b(pending|waiting|submitted)\b.{0,20}\b(quote|policy|request|change|document|application)\b', text): s += 6
    if re.search(r'\bfollow.?up\b.{0,30}\b(quote|policy|request|payment|document|change)\b', text): s += 8
    if re.search(r'\bprevious (call|conversation|request|email)\b', text): s += 5
    if re.search(r'\bcall(ing|ed)? back\b', text) and re.search(r'\b(about|regarding|for|on)\b', text): s += 4
    if re.search(r'\breturn(ing)? (a |the |my )?(call|voicemail|message)\b', text): s += 3
    # Downweight if there's a clear primary intent
    if re.search(r'\b(cancel|payment|add|remove|file|claim|quote|renew)\b', text) and not re.search(r'\bfollow.?up\b', text): s -= 3
    scores['follow-up'] = s

    # === ROUTING-TRIAGE ===
    s = 0
    if re.search(r'\b(speak|talk|reach|connect|transfer)\b.{0,20}\b(with|to)\b.{0,30}\b(agent|representative|person|someone|holly|jamie|sunny|staff|department)\b', text): s += 7
    if re.search(r'\breturn(ing)?\b.{0,10}\b(voicemail|call|message)\b', text): s += 6
    if re.search(r'\bspanish\b', text) and re.search(r'\b(assist|help|language|speak)\b', text): s += 8
    if re.search(r'\b(wrong number|non.?insurance|personal|it support|solicitation|vendor|sales pitch)\b', text): s += 8
    if re.search(r'\bcourtesy call\b', text): s += 7
    if re.search(r'\btransfer\b.{0,20}\b(to|call)\b', text) and not re.search(r'\b(claim|quote|cancel|payment)\b', text): s += 5
    if re.search(r'\b(unavailable|not available|out of office|on vacation|voicemail)\b', text) and re.search(r'\b(agent|representative|staff|person)\b', text): s += 5
    if re.search(r'\blanguage\b.{0,20}\b(barrier|assist|spanish|interpret)\b', text): s += 7
    if re.search(r'\bwrong (number|department|office|company)\b', text): s += 8
    if re.search(r'\bspam\b', text): s += 8
    if re.search(r'\bnon.?insurance\b', text): s += 7
    if re.search(r'\brobot|automated|scam\b', text): s += 6
    # Very short/empty calls
    if re.search(r'\b(no (one|answer)|hang up|hung up|disconnect|dropped|silence|dead air)\b', text): s += 4
    if re.search(r'\bincomplete\b', text) and len(intent) < 100: s += 3
    scores['routing-triage'] = s

    # Find the best match
    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    # If best score is 0, default based on keywords
    if best_score <= 0:
        # Fallback: try to find any signal
        if re.search(r'\bpayment\b', text):
            best_type = 'make-payment'
            best_score = 2
        elif re.search(r'\bquote\b', text):
            best_type = 'new-quote'
            best_score = 2
        elif re.search(r'\bclaim\b', text):
            best_type = 'claims'
            best_score = 2
        elif re.search(r'\bcancel\b', text):
            best_type = 'cancellation'
            best_score = 2
        elif re.search(r'\bcoverage\b', text):
            best_type = 'coverage-question'
            best_score = 2
        elif re.search(r'\bpolicy\b', text):
            best_type = 'follow-up'
            best_score = 1
        else:
            best_type = 'routing-triage'
            best_score = 1

    # Determine confidence
    sorted_scores = sorted(scores.values(), reverse=True)
    second_best = sorted_scores[1] if len(sorted_scores) > 1 else 0
    gap = best_score - second_best

    if best_score >= 8 and gap >= 4:
        confidence = 'high'
    elif best_score >= 5 and gap >= 2:
        confidence = 'medium'
    else:
        confidence = 'low'

    return best_type, confidence


# Classify all calls
classifications = []
for call in calls:
    etype, confidence = classify_call(call)
    classifications.append({
        'file': call['file'],
        'engagement_type': etype,
        'confidence': confidence
    })

# Print distribution
from collections import Counter
dist = Counter(c['engagement_type'] for c in classifications)
print("\nDistribution:")
for k, v in sorted(dist.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

conf_dist = Counter(c['confidence'] for c in classifications)
print(f"\nConfidence: {dict(conf_dist)}")

# Save intermediate for review
with open('/tmp/classify_batch3_intermediate.json', 'w') as f:
    json.dump(classifications, f, indent=2)
print(f"\nClassified {len(classifications)} calls")
