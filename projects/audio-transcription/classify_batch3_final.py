#!/usr/bin/env python3
"""
Classify 309 calls from batch 3 into engagement types.
Uses rule-based keyword/pattern matching with manual overrides for reviewed edge cases.
"""

import json
import re
from collections import defaultdict, Counter

INPUT_FILE = '/Users/home/Repositories/operating-system/projects/audio-transcription/classify_batch_3.jsonl'
TYPES_FILE = '/Users/home/Repositories/operating-system/projects/audio-transcription/engagement_types.json'
OUTPUT_FILE = '/Users/home/Repositories/operating-system/projects/audio-transcription/classify_result_3.json'

# Load engagement types
with open(TYPES_FILE, 'r') as f:
    engagement_types = json.load(f)
type_ids = {t['id'] for t in engagement_types}

# Load all calls
calls = []
with open(INPUT_FILE, 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            calls.append(json.loads(line))

print(f"Loaded {len(calls)} calls")

# ===== MANUAL OVERRIDES =====
# After reviewing all 309 calls, these need correction from the rule-based approach.
# Key: file name -> (engagement_type, confidence)
OVERRIDES = {
    # IDX=5: seeking liability insurance for business = new-quote
    "in-+13363779003-+13364035628-20250821-141321-1755800001.6452": ("new-quote", "medium"),
    # IDX=6: confused caller trying to reach agent Matt
    "in-+13363779003-+13364036893-20250903-145652-1756925812.9050": ("routing-triage", "high"),
    # IDX=10: urgent policy coverage alerts, seeking clarification
    "in-+13363779003-+13364069829-20260119-122214-1768843334.2294": ("billing-question", "medium"),
    # IDX=14: following up on Medicare plan with agent Morgan
    "in-+13363779003-+13364082499-20251119-111406-1763568846.3024": ("routing-triage", "high"),
    # IDX=16: seeking to review Medicare advantage plans with Steve
    "in-+13363779003-+13364091732-20251112-162125-1762982485.8309": ("routing-triage", "medium"),
    # IDX=22: payment discrepancy/confusion about reversed payment = billing-question
    "in-+13363779003-+13364228402-20250807-103820-1754577500.2466": ("billing-question", "high"),
    # IDX=33: disputed $3,700 charge = billing-question
    "in-+13363779003-+13364678729-20251023-102406-1761229446.1539": ("billing-question", "high"),
    # IDX=44: confirming renter's insurance bill = billing-question
    "in-+13363779003-+13365292003-20251120-114056-1763656856.1577": ("billing-question", "medium"),
    # IDX=48: adding a new car to business policy = vehicle-change
    "in-+13363779003-+13365824500-20251023-154545-1761248745.5674": ("vehicle-change", "high"),
    # IDX=51: caller confused about Alliance vs other company = routing-triage
    "in-+13363779003-+13366027274-20260114-112301-1768407781.1787": ("routing-triage", "high"),
    # IDX=67: reinstate full coverage on Tundra = coverage-modification
    "in-+13363779003-+13366897782-20251204-091212-1764857532.91": ("coverage-modification", "high"),
    # IDX=81: verify account status, address update, spam messages = info-update
    "in-+13363779003-+13367490677-20260119-140654-1768849614.4538": ("info-update", "medium"),
    # IDX=97: confirming policy reinstated after cutoff = reinstatement
    "in-+13363779003-+13368170139-20251124-092905-1763994545.517": ("reinstatement", "high"),
    # IDX=99: caller looking for Monica Southern who doesn't work there = routing-triage
    "in-+13363779003-+13368378131-20251104-102120-1762269680.2069": ("routing-triage", "high"),
    # IDX=101: seeking refund for claim reimbursement = claims
    "in-+13363779003-+13368656233-20251013-153442-1760384082.11475": ("claims", "high"),
    # IDX=109: refund for canceled policy = billing-question
    "in-+13363779003-+13369182152-20250826-121943-1756225183.3987": ("billing-question", "high"),
    # IDX=112: adding vehicle + quote follow-up = vehicle-change (primary)
    "in-+13363779003-+13369186212-20250905-162915-1757104155.6363": ("vehicle-change", "medium"),
    # IDX=126: sending pictures to agent = routing-triage
    "in-+13363779003-+13369729049-20250728-105024-1753714224.3112": ("routing-triage", "high"),
    # IDX=128: updating draft account + separating coverage after divorce = info-update
    "in-+13363779003-+13369790068-20250912-111139-1757689899.1967": ("info-update", "medium"),
    # IDX=133: dog-related Travelers policy issue = coverage-question
    "in-+13363779003-+13369970295-20251209-153234-1765312354.7095": ("coverage-question", "low"),
    # IDX=139: updating credit card info = info-update
    "in-+13363779003-+13369976166-20250811-094349-1754919829.1926": ("info-update", "high"),
    # IDX=142: missing email for insurance license cancellation = follow-up
    "in-+13363779003-+13464349994-20251010-125035-1760115035.6583": ("follow-up", "medium"),
    # IDX=148: Progressive rep trying to reach Alliance agent = routing-triage
    "in-+13363779003-+14409106130-20250818-090526-1755522326.283": ("routing-triage", "high"),
    # IDX=155: terminating current policies because moving = cancellation
    "in-+13363779003-+16073330743-20251003-103930-1759502370.5674": ("cancellation", "high"),
    # IDX=156: parent wanting auto insurance for daughter = new-quote
    "in-+13363779003-+16083323148-20251009-131953-1760030393.3885": ("new-quote", "high"),
    # IDX=160: following up on missing ID document = document-request
    "in-+13363779003-+16622795651-20260114-104043-1768405243.1173": ("document-request", "high"),
    # IDX=161: asking about cancellation reason = billing-question
    "in-+13363779003-+16788134751-20251118-135107-1763491867.3891": ("billing-question", "medium"),
    # IDX=170: seeking homeowner's insurance = new-quote
    "in-+13363779003-+17046157794-20250724-110050-1753369250.1340": ("new-quote", "high"),
    # IDX=172: requesting insurance cards for loaner vehicle = document-request
    "in-+13363779003-+17046508546-20250915-132744-1757957264.9790": ("document-request", "high"),
    # IDX=182: wants to make changes to policy (unspecified) = follow-up
    "in-+13363779003-+17432175374-20251215-161932-1765833572.5672": ("follow-up", "low"),
    # IDX=184: home warranty coverage question = coverage-question
    "in-+13363779003-+17434447366-20250728-115616-1753718176.4716": ("coverage-question", "high"),
    # IDX=187: following up on commercial inquiry = follow-up
    "in-+13363779003-+17863673494-20250730-153512-1753904112.10461": ("follow-up", "high"),
    # IDX=188: seeking commercial insurance, Spanish speaker = new-quote
    "in-+13363779003-+17867952468-20250725-130951-1753463391.8090": ("new-quote", "high"),
    # IDX=190: follow-up + Spanish-speaking agent request = follow-up
    "in-+13363779003-+18033714126-20251210-132423-1765391063.2702": ("follow-up", "high"),
    # IDX=192: property insurance quote for renewal = new-quote
    "in-+13363779003-+18053901792-20250821-140430-1755799470.6284": ("new-quote", "medium"),
    # IDX=196: following up to get form signed by Gary = follow-up
    "in-+13363779003-+18438745111-20251013-140618-1760378778.10622": ("follow-up", "high"),
    # IDX=202: mortgage company seeking home insurance info = mortgage-lender
    "in-+13363779003-+18882609876-20250822-105405-1755874445.5331": ("mortgage-lender", "high"),
    # IDX=203: Mister Cooper requesting renewal info = mortgage-lender
    "in-+13363779003-+18882609876-20250908-151158-1757358718.9046": ("mortgage-lender", "high"),
    # IDX=213: requesting homeowners insurance quote = new-quote
    "in-+13363779003-+19542605510-20251222-155312-1766436792.4710": ("new-quote", "high"),
    # IDX=214: confirming renewal date and rate changes = renewal-review
    "in-+13363779003-+19545945588-20250915-125830-1757955510.8014": ("renewal-review", "high"),
    # IDX=215: international caller struggling to pay = routing-triage
    "in-+13363779003-+19733626934-20251222-113454-1766421294.2330": ("routing-triage", "medium"),
    # IDX=227: reporting car accident = claims
    "in-+13365913091-+13365773297-20250801-131851-1754068731.4731": ("claims", "high"),
    # IDX=228: why is Geo Tracker premium higher than truck = billing-question
    "in-+13365913091-+13365958735-20250805-145816-1754420296.6734": ("billing-question", "high"),
    # IDX=229: confused about letter requiring additional insurance = coverage-question
    "in-+13365913091-+13368163540-20260115-092323-1768487003.505": ("coverage-question", "medium"),
    # IDX=240: changing policy due to pregnancy, adding dependent = coverage-modification
    "in-+13367861133-+13364034763-20251201-125923-1764611963.8840": ("coverage-modification", "medium"),
    # IDX=242: insurance estimates for jet skis = new-quote
    "in-+13367861133-+13364102581-20250722-104622-1753195582.5296": ("new-quote", "high"),
    # IDX=249: letter saying car insurance unpaid = billing-question
    "in-+13367861133-+13366487739-20251126-100227-1764169347.1188": ("billing-question", "high"),
    # IDX=252: trying to reach Heather Jones = routing-triage
    "in-+13367861133-+13366690888-20260112-100832-1768230512.625": ("routing-triage", "high"),
    # IDX=253: changing commercial truck to regular = coverage-modification
    "in-+13367861133-+13367100758-20251209-110054-1765296054.1678": ("coverage-modification", "medium"),
    # IDX=256: Dana from PF Plumbing requesting payment for backflow test = routing-triage (non-insurance)
    "in-+13367861133-+13367782008-20251120-114508-1763657108.1612": ("routing-triage", "high"),
    # IDX=265: bond modification for stormwater project = commercial-specialty
    "internal-105-409-20250806-152617-1754508377.9255": ("commercial-specialty", "high"),
    # IDX=267: internal call about policy status and collectible property = commercial-specialty
    "internal-301-702-20250806-161112-1754511072.11732": ("commercial-specialty", "medium"),
    # IDX=268: internal discussion about challenging cancellation = cancellation
    "internal-401-501-20251208-124915-1765216155.8749": ("cancellation", "medium"),
    # IDX=270: autopay setup issues = make-payment
    "internal-409-100-20251110-105258-1762789978.1320": ("make-payment", "medium"),
    # IDX=271: rate increase adjustment / policy change = renewal-review
    "internal-409-504-20251110-111953-1762791593.2227": ("renewal-review", "medium"),
    # IDX=274: finalizing JUA insurance policy = new-quote
    "internal-510-202-20251222-100349-1766415829.1305": ("new-quote", "medium"),
    # IDX=276: verifying properties on policy + professional liability = coverage-question
    "internal-510-702-20260107-094426-1767797066.446": ("coverage-question", "medium"),
    # IDX=277: confirming extension + document needing signature = routing-triage
    "internal-702-201-20251105-144531-1762371931.5697": ("routing-triage", "medium"),
    # IDX=281: resolving billing discrepancy = billing-question
    "out-+17863714662-101-20250910-114654-1757519214.2016": ("billing-question", "high"),
    # IDX=282: overdue audit payment = workers-comp (audit-related)
    "out-12142440302-302-20251006-113531-1759764931.3569": ("workers-comp", "medium"),
    # IDX=284: failed payment draft from SafeCo = billing-question
    "out-12525615271-509-20251215-120640-1765818400.2553": ("billing-question", "medium"),
    # IDX=288: life insurance policy discussion = commercial-specialty
    "out-13362090172-705-20250826-143637-1756233397.7594": ("commercial-specialty", "high"),
    # IDX=289: medical records for life insurance = follow-up
    "out-13362579534-701-20251229-115629-1767027389.7057": ("follow-up", "high"),
    # IDX=294: confirming vehicle added + payment timing = vehicle-change
    "out-13363402207-114-20250827-164819-1756327698.7705": ("vehicle-change", "high"),
    # IDX=298: golf course inquiry = routing-triage
    "out-13363682828-705-20250811-133927-1754933967.10829": ("routing-triage", "high"),
    # IDX=299: confirming car insurance payment to avoid cancellation = make-payment
    "out-13363740199-702-20251212-134816-1765565296.3615": ("make-payment", "medium"),
    # IDX=300: ordering hibachi chicken = routing-triage
    "out-13363770147-100-20250811-133820-1754933900.10826": ("routing-triage", "high"),
    # IDX=301: Progressive canceled wrong policy = claims (resolving coverage error)
    "out-13363910990-114-20250916-141236-1758046356.8803": ("reinstatement", "medium"),
    # IDX=308: follow up on auto claim + homeowners premium increase = renewal-review
    "out-13364085560-113-20260116-142050-1768591250.4629": ("renewal-review", "medium"),
    # IDX=7: Medicare Advantage plans inquiry
    "in-+13363779003-+13364039762-20251114-134610-1763145970.6406": ("commercial-specialty", "medium"),
    # IDX=34: outstanding balance on policy = make-payment
    "in-+13363779003-+13364692541-20250908-162523-1757363123.10195": ("make-payment", "high"),
    # IDX=41: comparing commercial insurance statements = billing-question
    "in-+13363779003-+13364924092-20250825-141057-1756145457.7762": ("billing-question", "medium"),
    # IDX=45: verifying surety bond status = commercial-specialty
    "in-+13363779003-+13365297668-20250722-104112-1753195272.5218": ("commercial-specialty", "high"),
    # IDX=46: DL form with misspelled name = info-update
    "in-+13363779003-+13365491770-20260108-152533-1767903933.5865": ("info-update", "medium"),
    # IDX=49: changing insurance representative = routing-triage
    "in-+13363779003-+13366014476-20250723-113741-1753285061.4944": ("routing-triage", "high"),
    # IDX=50: Joe Silver house-related issue = claims
    "in-+13363779003-+13366024824-20250908-090018-1757336418.65": ("claims", "low"),
    # IDX=53: Spanish-speaking caller needing car insurance info = routing-triage
    "in-+13363779003-+13366181713-20251210-104807-1765381687.1432": ("routing-triage", "high"),
    # IDX=54: confirming home insurance coverage vs mortgage company notice = mortgage-lender
    "in-+13363779003-+13366242164-20250910-164804-1757537284.9867": ("mortgage-lender", "high"),
    # IDX=56: requesting resent quote email = follow-up
    "in-+13363779003-+13366484168-20250731-163700-1753994220.19215": ("follow-up", "high"),
    # IDX=62: trying to reach Gloria = routing-triage
    "in-+13363779003-+13366615429-20251015-145959-1760554799.4825": ("routing-triage", "high"),
    # IDX=66: inspector confirming contact info = routing-triage
    "in-+13363779003-+13366896866-20251118-094954-1763477394.1656": ("routing-triage", "high"),
    # IDX=68: reimbursement for towing = claims
    "in-+13363779003-+13366921779-20260113-145453-1768334093.7545": ("claims", "high"),
    # IDX=69: renewing expired policy = reinstatement
    "in-+13363779003-+13366922318-20250924-130154-1758733314.3348": ("reinstatement", "high"),
    # IDX=70: trying to reach Heather Johnson = routing-triage
    "in-+13363779003-+13366922515-20251003-093801-1759498681.2396": ("routing-triage", "high"),
    # IDX=72: account status + auto payment issue = billing-question
    "in-+13363779003-+13366957957-20251201-125355-1764611635.8101": ("billing-question", "medium"),
    # IDX=74: insurance lapse wrong vehicle canceled = dmv-compliance
    "in-+13363779003-+13367037550-20251002-134432-1759427072.9598": ("dmv-compliance", "medium"),
    # IDX=83: caller wants to speak with Cecilia = routing-triage
    "in-+13363779003-+13367499840-20251218-095207-1766069527.536": ("routing-triage", "high"),
    # IDX=87: wants to speak to homeowners insurance agent = routing-triage
    "in-+13363779003-+13367674751-20250916-145518-1758048918.9944": ("routing-triage", "medium"),
    # IDX=89: confused about auto bank deduction after adding/dropping car = billing-question
    "in-+13363779003-+13367717676-20250807-142948-1754591388.10647": ("billing-question", "high"),
    # IDX=91: canceled policy, needs Spanish support = reinstatement
    "in-+13363779003-+13367768942-20251222-113846-1766421526.2527": ("reinstatement", "medium"),
    # IDX=92: wants to make changes to policy = follow-up
    "in-+13363779003-+13367792101-20251003-111447-1759504487.8368": ("follow-up", "medium"),
    # IDX=105: unsolicited email, not a customer = routing-triage
    "in-+13363779003-+13368993083-20251124-125733-1764007053.3646": ("routing-triage", "high"),
    # IDX=108: Spanish-speaking caller = routing-triage
    "in-+13363779003-+13369181774-20260119-123546-1768844146.2919": ("routing-triage", "high"),
    # IDX=116: auto insurance matter, inquiring about Heather = routing-triage
    "in-+13363779003-+13369262158-20250924-121025-1758730225.2426": ("routing-triage", "medium"),
    # IDX=132: life insurance inquiry = commercial-specialty
    "in-+13363779003-+13369950011-20260116-091538-1768572938.249": ("commercial-specialty", "high"),
    # IDX=134: correcting routing/account number = info-update
    "in-+13363779003-+13369970484-20250909-163555-1757450155.13706": ("info-update", "high"),
    # IDX=135: confirm auto payment setup + delayed claim = claims
    "in-+13363779003-+13369970906-20251201-105853-1764604733.4475": ("claims", "medium"),
    # IDX=138: duplicate payment for reinstatement + requesting documents = reinstatement
    "in-+13363779003-+13369975930-20250903-150432-1756926272.9091": ("reinstatement", "medium"),
    # IDX=145: lien holder canceling policy = cancellation
    "in-+13363779003-+14068314454-20250829-144533-1756493133.6254": ("cancellation", "medium"),
    # IDX=146: Tim from Veris, survey order = routing-triage
    "in-+13363779003-+14238739276-20250930-141122-1759255882.4580": ("routing-triage", "high"),
    # IDX=149: follow up on commercial auto policy = follow-up
    "in-+13363779003-+14409108130-20251009-130100-1760029260.3493": ("follow-up", "high"),
    # IDX=150: letter about certification of higher coverage limits = coverage-question
    "in-+13363779003-+14434170997-20251008-150015-1759950015.6819": ("coverage-question", "medium"),
    # IDX=152: bank insurance tracking checking policy status = mortgage-lender
    "in-+13363779003-+14704810473-20250828-132748-1756402068.5090": ("mortgage-lender", "high"),
    # IDX=153: USLI rep trying to reach Gloria Bell = routing-triage
    "in-+13363779003-+14845854000-20251124-103446-1763998486.1454": ("routing-triage", "high"),
    # IDX=154: flood declaration aid from credit union = mortgage-lender
    "in-+13363779003-+15186148898-20251007-100631-1759845991.1212": ("mortgage-lender", "high"),
    # IDX=157: renewing policies transitioning to new company = renewal-review
    "in-+13363779003-+16107813722-20251008-111720-1759936640.2809": ("renewal-review", "high"),
    # IDX=159: lienholder verification = mortgage-lender
    "in-+13363779003-+16316154991-20250722-145822-1753210702.15315": ("mortgage-lender", "high"),
    # IDX=162: HOA management company coverage rider = commercial-specialty
    "in-+13363779003-+17042008835-20251226-151022-1766779822.2610": ("commercial-specialty", "high"),
    # IDX=164: payment + policy migration = make-payment
    "in-+13363779003-+17044705274-20250827-124543-1756313143.4383": ("make-payment", "medium"),
    # IDX=166: questioning premium amount on old vehicle = billing-question
    "in-+13363779003-+17045001683-20250917-124441-1758127481.2199": ("billing-question", "high"),
    # IDX=168: missing bill for well policy = billing-question
    "in-+13363779003-+17045285483-20260119-095820-1768834700.865": ("billing-question", "medium"),
    # IDX=169: auto insurance inquiry = new-quote
    "in-+13363779003-+17045499908-20250904-093659-1756993019.1117": ("new-quote", "low"),
    # IDX=177: following up on Tracy not responding = follow-up
    "in-+13363779003-+17048539391-20251002-121149-1759421509.8323": ("follow-up", "high"),
    # IDX=179: verifying homeowners renewal = renewal-review
    "in-+13363779003-+17049759120-20250918-135259-1758217975.7937": ("renewal-review", "high"),
    # IDX=181: reaching agent for Homer Auto quote = new-quote
    "in-+13363779003-+17432161857-20250724-131830-1753377510.2992": ("new-quote", "medium"),
    # IDX=186: following up on policy update request = follow-up
    "in-+13363779003-+17706924631-20251010-151811-1760123891.10381": ("follow-up", "high"),
    # IDX=189: inquiring about commercial policy cancellation = cancellation
    "in-+13363779003-+18002430210-20250828-154937-1756410577.9491": ("cancellation", "medium"),
    # IDX=191: premium finance services inquiry = routing-triage
    "in-+13363779003-+18043573177-20251125-111658-1764087418.1353": ("routing-triage", "high"),
    # IDX=193: removing one vehicle, adding another = vehicle-change
    "in-+13363779003-+18106247446-20251218-151142-1766088702.3972": ("vehicle-change", "high"),
    # IDX=197: clarifying confusing document (renewal notice) = billing-question
    "in-+13363779003-+18605591342-20260113-103055-1768318255.3518": ("billing-question", "high"),
    # IDX=198: Vietnamese language request = routing-triage
    "in-+13363779003-+18642436542-20250909-125300-1757436780.8168": ("routing-triage", "high"),
    # IDX=199: Shellpoint Mortgage trying to reach Tracy = mortgage-lender
    "in-+13363779003-+18776340985-20250731-132731-1753982851.10182": ("mortgage-lender", "high"),
    # IDX=200: verify commercial policy premium from mortgage company = mortgage-lender
    "in-+13363779003-+18882609698-20250801-155616-1754078176.6005": ("mortgage-lender", "medium"),
    # IDX=201: Lakeview Loan Servicing verifying homeowner's insurance = mortgage-lender
    "in-+13363779003-+18882609698-20250825-104938-1756133378.2585": ("mortgage-lender", "high"),
    # IDX=205: Bank of America verifying reinstatement doc = mortgage-lender
    "in-+13363779003-+18882609876-20251105-141415-1762370055.5304": ("mortgage-lender", "high"),
    # IDX=206: trying to reach Heather = routing-triage
    "in-+13363779003-+19175395567-20250924-152850-1758742130.6181": ("routing-triage", "high"),
    # IDX=207: new customer checking payment processing = follow-up
    "in-+13363779003-+19176283741-20251215-104810-1765813690.1287": ("follow-up", "medium"),
    # IDX=208: credit union seeking auto insurance documentation = document-request
    "in-+13363779003-+19192311601-20251125-144420-1764099860.6087": ("document-request", "high"),
    # IDX=209: payment + changing driver = make-payment
    "in-+13363779003-+19198687196-20250821-104319-1755787399.1502": ("make-payment", "medium"),
    # IDX=211: following up on commercial auto policy with Gloria = follow-up
    "in-+13363779003-+19199467610-20250723-131423-1753290863.7773": ("follow-up", "high"),
    # IDX=212: NC Home Builders Association trying to reach Joe Jessup = routing-triage
    "in-+13363779003-+19522488089-20250813-094640-1755092800.1207": ("routing-triage", "high"),
    # IDX=221: seeking housing support, not insurance = routing-triage
    "in-+13363779003-+19843901598-20251222-102053-1766416853.1464": ("routing-triage", "high"),
    # IDX=222: trying to reach Holly = routing-triage
    "in-+13363779003-Anonymous-20250902-134057-1756834857.5698": ("routing-triage", "high"),
    # IDX=225: payment + email update = make-payment
    "in-+13365913091-+13364539740-20251020-140518-1760983518.7668": ("make-payment", "high"),
    # IDX=231: policy canceled unexpectedly, seeking replacement = reinstatement
    "in-+13365913091-+13368360102-20250801-162130-1754079690.7077": ("reinstatement", "medium"),
    # IDX=234: inquiring about towing coverage = coverage-question
    "in-+13367861133-+12767544067-20251219-111630-1766160990.3309": ("coverage-question", "high"),
    # IDX=238: trying to reach Rachel Hall = routing-triage
    "in-+13367861133-+13363512107-20251226-103711-1766763431.1063": ("routing-triage", "high"),
    # IDX=243: adding mom's car to policy for savings = vehicle-change
    "in-+13367861133-+13364140963-20250918-105426-1758207266.4406": ("vehicle-change", "medium"),
    # IDX=244: removing Dodge Ram from father's policy = vehicle-change
    "in-+13367861133-+13364685952-20250808-160707-1754683627.14062": ("vehicle-change", "high"),
    # IDX=245: requesting homeowner's declaration page = document-request
    "in-+13367861133-+13365266379-20251014-133145-1760463105.4267": ("document-request", "high"),
    # IDX=246: seeking coverage details for renewal = renewal-review
    "in-+13367861133-+13365393774-20251010-101421-1760105661.924": ("renewal-review", "high"),
    # IDX=251: trying to reach Brandi = routing-triage
    "in-+13367861133-+13366489698-20251008-102241-1759933361.1756": ("routing-triage", "high"),
    # IDX=257: confused about previous message, wants quote = new-quote
    "in-+13367861133-+13367822580-20251007-135522-1759859722.7376": ("new-quote", "low"),
    # IDX=258: Northside Mortgage requesting homeowner's quote = mortgage-lender
    "in-+13367861133-+13367839100-20251008-143512-1759948512.6435": ("mortgage-lender", "high"),
    # IDX=264: confirming 100% replacement cost for condo = coverage-question
    "in-+13367861133-+19133364160-20250819-132615-1755624375.5720": ("coverage-question", "high"),
    # IDX=269: following up on canceled policy case = follow-up
    "internal-406-702-20251008-144647-1759949207.6724": ("follow-up", "high"),
    # IDX=272: payment + billing confusion between entities = billing-question
    "internal-509-206-20250929-160402-1759176242.6520": ("billing-question", "medium"),
    # IDX=273: changing to liability-only on two vehicles = coverage-modification
    "internal-510-201-20251114-141728-1763147848.6570": ("coverage-modification", "high"),
    # IDX=275: settlement approval for accident claim = claims
    "internal-510-702-20251222-122506-1766424306.2856": ("claims", "high"),
    # IDX=278: vehicle inspection exemption = dmv-compliance
    "internal-702-502-20251229-135759-1767034679.9814": ("dmv-compliance", "medium"),
    # IDX=280: confirming cancellation form details = cancellation
    "out-+16073330743-100-20251006-163226-1759782746.14175": ("cancellation", "high"),
    # IDX=283: business income coverage limits on policy = coverage-modification
    "out-12168108766-105-20250919-145756-1758308276.6879": ("coverage-modification", "high"),
    # IDX=286: added full coverage, concerned about high premium = billing-question
    "out-13362011011-114-20251003-114157-1759506117.9970": ("billing-question", "high"),
    # IDX=287: RV claim denied, seeking explanation = claims
    "out-13362027527-114-20251002-123657-1759423017.8700": ("claims", "high"),
    # IDX=290: voicemail about theft coverage = claims
    "out-13362594327-113-20251212-124620-1765561580.1756": ("claims", "high"),
    # IDX=291: payment to Liberty Mutual using cash = make-payment
    "out-13362764167-302-20251226-141720-1766776640.2261": ("make-payment", "high"),
    # IDX=292: reporting car accident = claims
    "out-13363250353-705-20260115-090828-1768486108.427": ("claims", "high"),
    # IDX=293: paying overdue premium = make-payment
    "out-13363250785-702-20250804-103201-1754317921.3407": ("make-payment", "high"),
    # IDX=295: Jeff trying to reach Vicky about email = routing-triage
    "out-13363680668-206-20250822-163234-1755894754.15165": ("routing-triage", "high"),
    # IDX=296: Jeff trying to reach Vicki = routing-triage
    "out-13363680668-206-20250923-125532-1758646532.3126": ("routing-triage", "high"),
    # IDX=297: builder's risk policy = commercial-specialty
    "out-13363680668-207-20251202-120726-1764695246.3482": ("commercial-specialty", "high"),
    # IDX=302: commercial insurance quote for installation crew = new-quote
    "out-13364015705-207-20251124-142728-1764012448.4388": ("new-quote", "high"),
    # IDX=303: following up on review email = follow-up
    "out-13364016855-206-20260119-081938-1768828778.24": ("follow-up", "high"),
    # IDX=304: policy adjustment, removing vehicle = vehicle-change
    "out-13364060349-114-20260107-111909-1767802749.1307": ("vehicle-change", "high"),
    # IDX=305: annual policy review = renewal-review
    "out-13364063009-113-20251216-102636-1765898796.1090": ("renewal-review", "high"),
    # IDX=306: evaluating cost of replacing vehicle = vehicle-change
    "out-13364072580-113-20251226-090256-1766757776.39": ("vehicle-change", "medium"),
    # IDX=307: clarifying premium increase and water event = billing-question
    "out-13364082370-114-20251119-093029-1763562629.651": ("billing-question", "high"),
    # Additional corrections from initial review:
    # IDX=13: updating renter's insurance with new address = info-update
    "in-+13363779003-+13364074381-20250730-131354-1753895634.4792": ("info-update", "high"),
    # IDX=17: trying to reach Chase = routing-triage
    "in-+13363779003-+13364097460-20250826-142956-1756232996.7385": ("routing-triage", "high"),
    # IDX=19: requesting copy of renewed bond = document-request
    "in-+13363779003-+13364144231-20251211-122020-1765473620.2724": ("document-request", "high"),
    # IDX=24: personal + business insurance = new-quote
    "in-+13363779003-+13364302726-20250820-092723-1755696443.599": ("new-quote", "medium"),
    # IDX=36: confirming home insurance paid by mortgage + referring friend = mortgage-lender
    "in-+13363779003-+13364863036-20250825-093758-1756129078.1304": ("mortgage-lender", "high"),
    # IDX=58: confirming recent payment processed = billing-question
    "in-+13363779003-+13366555941-20251114-124910-1763142550.5313": ("billing-question", "high"),
    # IDX=64: banking info for payment + proof of insurance = make-payment
    "in-+13363779003-+13366818701-20251126-103437-1764171277.1564": ("make-payment", "medium"),
    # IDX=85: declined auto payment, card expired = make-payment
    "in-+13363779003-+13367558620-20251007-120441-1759853081.3800": ("make-payment", "high"),
    # IDX=88: attempting car insurance quote = new-quote
    "in-+13363779003-+13367696653-20260115-093643-1768487803.739": ("new-quote", "medium"),
    # IDX=102: hazard insurance requirement from mortgage = mortgage-lender
    "in-+13363779003-+13368750989-20251017-121125-1760717485.2625": ("mortgage-lender", "high"),
    # IDX=103: requesting loss history = document-request
    "in-+13363779003-+13368968600-20251112-100329-1762959809.1496": ("document-request", "high"),
    # IDX=114: following up on audit payment plan = workers-comp
    "in-+13363779003-+13369200018-20250820-160927-1755720567.12677": ("workers-comp", "medium"),
    # IDX=115: commercial auto renewal = renewal-review
    "in-+13363779003-+13369226534-20260106-131344-1767723224.3268": ("renewal-review", "high"),
    # IDX=120: updating personal auto + requesting commercial declaration = document-request
    "in-+13363779003-+13369342800-20251013-123315-1760373195.7359": ("document-request", "medium"),
    # IDX=123: proof of insurance + adding new Jeep = vehicle-change
    "in-+13363779003-+13369441709-20251110-132702-1762799222.3523": ("vehicle-change", "high"),
    # IDX=124: coverage question about buildings/renters = coverage-question
    "in-+13363779003-+13369455827-20260106-160142-1767733302.5960": ("coverage-question", "high"),
    # IDX=129: following up on cancellation request = cancellation
    "in-+13363779003-+13369799585-20250826-111704-1756221424.2010": ("cancellation", "high"),
    # IDX=144: changing mortgagee on policy = mortgage-lender
    "in-+13363779003-+14044240533-20251104-094644-1762267604.1421": ("mortgage-lender", "high"),
    # IDX=147: bundling auto + homeowners = renewal-review
    "in-+13363779003-+14405666930-20251112-102131-1762960891.2046": ("renewal-review", "medium"),
    # IDX=158: windshield coverage inquiry = coverage-question
    "in-+13363779003-+16316036731-20250918-092050-1758201650.625": ("coverage-question", "high"),
    # IDX=171: confirming payment processed / switching banks = make-payment
    "in-+13363779003-+17046210226-20260112-112226-1768234946.1297": ("make-payment", "medium"),
    # IDX=185: commercial quote for box truck = new-quote
    "in-+13363779003-+17438370295-20250812-111509-1755011709.2719": ("new-quote", "high"),
    # IDX=195: canceling totaled car + adding new car = vehicle-change
    "in-+13363779003-+18284550585-20260116-143556-1768592156.4760": ("vehicle-change", "high"),
    # IDX=210: confirming claim documents submitted = claims
    "in-+13363779003-+19199066472-20251208-101536-1765206936.1814": ("claims", "high"),
    # IDX=219: missing email for vehicle added = document-request
    "in-+13363779003-+19803783399-20250909-143705-1757443025.10437": ("document-request", "high"),
    # IDX=220: workers comp policy renewal payment = make-payment
    "in-+13363779003-+19842150785-20251110-131103-1762798263.3329": ("make-payment", "high"),
    # IDX=224: declaration page to remove Sage Stovall = document-request
    "in-+13365913091-+13364535020-20251014-113347-1760456027.2159": ("document-request", "high"),
    # IDX=230: billing discrepancy between bill and policy change letter = billing-question
    "in-+13365913091-+13368164174-20251119-131236-1763575956.3949": ("billing-question", "high"),
    # IDX=232: portal login + car accident settlement = claims
    "in-+13365913091-+13369785337-20251017-155041-1760730641.5191": ("claims", "medium"),
    # IDX=239: canceling builder's risk policy = cancellation
    "in-+13367861133-+13363681155-20251017-131332-1760721212.3677": ("cancellation", "high"),
    # IDX=248: standalone car insurance quote = new-quote
    "in-+13367861133-+13366486810-20260106-141512-1767726912.4310": ("new-quote", "high"),
    # IDX=250: auto insurance quote for Virginia = new-quote
    "in-+13367861133-+13366489233-20250915-162205-1757967725.17621": ("new-quote", "high"),
    # IDX=254: windshield repair coverage question = coverage-question
    "in-+13367861133-+13367104518-20260105-102725-1767626845.2018": ("coverage-question", "high"),
    # IDX=262: payment + health insurance inquiry = make-payment
    "in-+13367861133-+16022849870-20250828-110356-1756393436.2618": ("make-payment", "high"),
    # IDX=266: payment processing for Dale Falk = make-payment
    "internal-201-702-20251201-135340-1764615220.10160": ("make-payment", "high"),
    # IDX=285: motorsports insurance quote = new-quote
    "out-12604595000-206-20250805-151309-1754421189.7151": ("new-quote", "high"),
}


def classify_call(call):
    """Classify a single call. Returns (engagement_type, confidence)."""
    # Check overrides first
    if call['file'] in OVERRIDES:
        return OVERRIDES[call['file']]

    intent = (call.get('caller_intent') or '').lower()
    summary = (call.get('summary') or '').lower()
    text = intent + ' ' + summary
    resolution = ' '.join(call.get('resolution_steps', [])).lower()
    knowledge = ' '.join(call.get('knowledge_required', [])).lower()
    systems = ' '.join(call.get('systems_referenced', [])).lower()
    all_text = text + ' ' + resolution + ' ' + knowledge + ' ' + systems

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
    if re.search(r'\bprocessed.{0,20}(payment|credit card|debit)\b', text): s += 5
    if re.search(r'\bpay.{0,10}(car|auto|home|renters?|insurance)\b', text): s += 7
    if re.search(r'\bpay.{0,10}(their|his|her|my|the)\b.{0,20}\b(bill|premium|insurance|policy)\b', text): s += 8
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
    if re.search(r'\bunexpected.{0,20}(increase|amount|charge|bill)\b', text): s += 8
    if re.search(r'\bpremium\b.{0,20}\b(discrepanc|incorrect|wrong|confus)\b', text): s += 8
    if re.search(r'\bescrow\b', text): s -= 5
    scores['billing-question'] = s

    # === NEW-QUOTE ===
    s = 0
    if re.search(r'\bquote\b', text): s += 6
    if re.search(r'\b(new|get|obtain|request|need|seeking|shop)\b.{0,30}\bquote\b', text): s += 4
    if re.search(r'\bshopping\b', text): s += 7
    if re.search(r'\b(home|auto|renters?|commercial|life|liability|moped|motorcycle|boat|flood|landlord)\b.{0,20}\b(quote|insurance)\b', text) and not re.search(r'\b(cancel|claim|renew|billing)\b', text): s += 5
    if re.search(r'\bprice comparison\b', text): s += 6
    if re.search(r'\bnew (construction |cleaning |landscaping )?(company|business|llc)\b', text): s += 5
    if re.search(r'\bseeking.{0,30}(insurance|quote|coverage)\b', text) and not re.search(r'\b(cancel|change|modif|add|remove|claim)\b', text): s += 5
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
    if re.search(r'\bnewly purchased\b', text): s += 7
    scores['vehicle-change'] = s

    # === DRIVER-CHANGE ===
    s = 0
    if re.search(r'\b(add|adding)\b.{0,30}\b(driver|person)\b', text): s += 9
    if re.search(r'\b(remove|removing)\b.{0,30}\b(driver|person)\b', text): s += 9
    if re.search(r'\b(daughter|son|teen|child)\b.{0,30}\b(license|permit|driving|driver)\b', text): s += 7
    if re.search(r'\blearner.?s? permit\b', text): s += 8
    if re.search(r'\bexclude\b.{0,20}\bdriver\b', text): s += 7
    scores['driver-change'] = s

    # === COVERAGE-MODIFICATION ===
    s = 0
    if re.search(r'\b(change|modify|adjust|increase|decrease|raise|lower|update)\b.{0,30}\b(deductible|coverage|limit|liability)\b', text): s += 9
    if re.search(r'\b(add|remove|drop)\b.{0,30}\b(coverage|collision|comprehensive|comp|towing|roadside|umbrella|uninsured|underinsured|rental|gap|pip|med.?pay)\b', text): s += 9
    if re.search(r'\bdeductible\b', text) and re.search(r'\b(change|modify|adjust|increase|decrease|raise|lower)\b', text): s += 8
    if re.search(r'\bumbrella\b.{0,30}\b(increase|add|raise|from|to)\b', text): s += 7
    if re.search(r'\bcoverage modification\b', text): s += 10
    if re.search(r'\b(increase|decrease)\b.{0,20}\b(limits?|coverage|liability)\b', text): s += 7
    if re.search(r'\bremove.{0,20}(towing|roadside|rental|comp|comprehensive|collision)\b', text): s += 8
    if re.search(r'\bliability only\b', text): s += 5
    scores['coverage-modification'] = s

    # === CANCELLATION ===
    s = 0
    if re.search(r'\bcancel\b.{0,30}\b(policy|insurance|coverage|account)\b', text): s += 10
    if re.search(r'\bcancellation\b', text) and not re.search(r'\breinstat\b', text): s += 7
    if re.search(r'\bwants to cancel\b', text): s += 10
    if re.search(r'\b(cancel|terminat|end|stop)\b.{0,20}\b(policy|insurance|coverage)\b', text): s += 8
    if re.search(r'\breinstat\b', text): s -= 10
    scores['cancellation'] = s

    # === REINSTATEMENT ===
    s = 0
    if re.search(r'\breinstat\b', text): s += 10
    if re.search(r'\b(cancel|lapse)\b.{0,40}\b(reinstat|reactivat|restore)\b', text): s += 9
    if re.search(r'\bnon.?payment\b', text) and re.search(r'\b(reinstat|reactivat)\b', text): s += 8
    if re.search(r'\breinstatement\b', text): s += 10
    scores['reinstatement'] = s

    # === CLAIMS ===
    s = 0
    if re.search(r'\b(file|report|open|submit|make)\b.{0,20}\b(claim|accident|incident)\b', text): s += 9
    if re.search(r'\bclaim\b', text) and re.search(r'\b(file|report|damage|accident|stolen|theft|hit|wreck|crash|collision|flood|fire|hail|storm|vandal|break.?in|burglary)\b', text): s += 8
    if re.search(r'\baccident\b', text) and re.search(r'\b(report|file|claim|insurance)\b', text): s += 7
    if re.search(r'\b(stolen|theft)\b', text) and re.search(r'\b(report|claim|file)\b', text): s += 8
    if re.search(r'\b(adjuster|settlement|claim status|claim number)\b', text): s += 7
    if re.search(r'\bdamage\b.{0,30}\b(claim|report|file)\b', text): s += 7
    if re.search(r'\bhit.{0,10}(a |the |my )?(car|vehicle|truck|deer|pole|tree|mailbox|fence|garage)\b', text): s += 6
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
    scores['renewal-review'] = s

    # === COI-REQUEST ===
    s = 0
    if re.search(r'\bcertificate of insurance\b', text): s += 10
    if re.search(r'\bcoi\b', text): s += 8
    if re.search(r'\bcertificate\b.{0,30}\b(insurance|liability|coverage)\b', text): s += 9
    if re.search(r'\b(additional insured|add.{0,10}insured)\b', text): s += 7
    scores['coi-request'] = s

    # === DOCUMENT-REQUEST ===
    s = 0
    if re.search(r'\b(copy|copies)\b.{0,30}\b(policy|declaration|dec page|id card|proof|document)\b', text): s += 9
    if re.search(r'\b(declaration|dec) page\b', text): s += 8
    if re.search(r'\bproof of (insurance|coverage)\b', text): s += 8
    if re.search(r'\bid card\b', text) and re.search(r'\b(insurance|policy)\b', text): s += 8
    if re.search(r'\bloss run\b', text): s += 9
    if re.search(r'\bbinder\b', text) and re.search(r'\b(send|email|need|provide|request)\b', text): s += 6
    if re.search(r'\binsurance card\b', text): s += 7
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
    if re.search(r'\bclosing\b', text) and re.search(r'\b(mortgage|lender|loan|house|home)\b', text): s += 5
    scores['mortgage-lender'] = s

    # === WORKERS-COMP ===
    s = 0
    if re.search(r'\bworkers?.{0,3}comp\b', text): s += 10
    if re.search(r'\bwork comp\b', text): s += 9
    if re.search(r'\bghost policy\b', text): s += 8
    if re.search(r'\baudit\b', text) and re.search(r'\b(workers|comp|payroll|class code)\b', text): s += 7
    if re.search(r'\bclass code\b', text): s += 5
    scores['workers-comp'] = s

    # === INFO-UPDATE ===
    s = 0
    if re.search(r'\b(update|change|correct|modify)\b.{0,30}\b(address|phone|email|name|contact|mailing)\b', text): s += 9
    if re.search(r'\b(address|phone|email|name)\b.{0,30}\b(update|change|correct|modify|new)\b', text): s += 7
    if re.search(r'\b(moved|new address|address change)\b', text): s += 7
    if re.search(r'\b(divorce|marriage|married|maiden)\b', text) and re.search(r'\b(name|last name)\b', text): s += 8
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
    if re.search(r'\binquir\b.{0,30}\b(coverage|covered)\b', text): s += 7
    scores['coverage-question'] = s

    # === COMMERCIAL-SPECIALTY ===
    s = 0
    if re.search(r"\bbuilder.?s?.{0,3}risk\b", text): s += 9
    if re.search(r'\b(vacant|unoccupied)\b.{0,20}\b(property|building|house)\b', text): s += 8
    if re.search(r'\b(surety )?bond\b', text) and re.search(r'\b(need|request|quote|insurance)\b', text): s += 6
    if re.search(r'\b(hoa|homeowners? association|church|preschool|daycare|school)\b', text) and re.search(r'\b(insurance|policy|coverage|program)\b', text): s += 7
    if re.search(r'\b(dealer|dealership)\b.{0,20}\b(lot|insurance|bond)\b', text): s += 8
    if re.search(r'\b(special event|liquor liability|farm|ranch|crop)\b', text): s += 7
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
    if re.search(r'\b(cancel|payment|add|remove|file|claim|quote|renew)\b', text) and not re.search(r'\bfollow.?up\b', text): s -= 3
    scores['follow-up'] = s

    # === ROUTING-TRIAGE ===
    s = 0
    if re.search(r'\b(speak|talk|reach|connect|transfer)\b.{0,20}\b(with|to)\b.{0,30}\b(agent|representative|person|someone)\b', text): s += 7
    if re.search(r'\breturn(ing)?\b.{0,10}\b(voicemail|call|message)\b', text): s += 6
    if re.search(r'\bspanish\b', text) and re.search(r'\b(assist|help|language|speak)\b', text): s += 8
    if re.search(r'\b(wrong number|non.?insurance|personal|it support|solicitation|vendor|sales pitch)\b', text): s += 8
    if re.search(r'\bcourtesy call\b', text): s += 7
    if re.search(r'\b(unavailable|not available|out of office|on vacation|voicemail)\b', text) and re.search(r'\b(agent|representative|staff|person)\b', text): s += 5
    if re.search(r'\blanguage\b.{0,20}\b(barrier|assist|spanish|interpret)\b', text): s += 7
    if re.search(r'\bwrong (number|department|office|company)\b', text): s += 8
    if re.search(r'\bspam\b', text): s += 8
    if re.search(r'\bnon.?insurance\b', text): s += 7
    if re.search(r'\b(no (one|answer)|hang up|hung up|disconnect|dropped|silence|dead air)\b', text): s += 4
    scores['routing-triage'] = s

    # Find best
    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    if best_score <= 0:
        if re.search(r'\bpayment\b', text):
            best_type = 'make-payment'; best_score = 2
        elif re.search(r'\bquote\b', text):
            best_type = 'new-quote'; best_score = 2
        elif re.search(r'\bclaim\b', text):
            best_type = 'claims'; best_score = 2
        elif re.search(r'\bcancel\b', text):
            best_type = 'cancellation'; best_score = 2
        elif re.search(r'\bcoverage\b', text):
            best_type = 'coverage-question'; best_score = 2
        elif re.search(r'\bpolicy\b', text):
            best_type = 'follow-up'; best_score = 1
        else:
            best_type = 'routing-triage'; best_score = 1

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


# ===== CLASSIFY ALL CALLS =====
classifications = []
for call in calls:
    etype, confidence = classify_call(call)
    classifications.append({
        'file': call['file'],
        'engagement_type': etype,
        'confidence': confidence
    })

# Verify all types are valid
for c in classifications:
    assert c['engagement_type'] in type_ids, f"Invalid type: {c['engagement_type']} for {c['file']}"

# ===== BUILD TYPE DIGESTS =====
# Group calls by type
by_type = defaultdict(list)
for call, cls in zip(calls, classifications):
    by_type[cls['engagement_type']].append((call, cls))

type_digests = {}
for etype, items in sorted(by_type.items()):
    count = len(items)

    # Outcome distribution
    outcomes = Counter(call.get('outcome', 'unknown') for call, _ in items)

    # Knowledge required (aggregate)
    all_knowledge = set()
    for call, _ in items:
        for k in call.get('knowledge_required', []):
            all_knowledge.add(k)

    # Systems referenced (aggregate)
    all_systems = set()
    for call, _ in items:
        for s in call.get('systems_referenced', []):
            all_systems.add(s)

    # Resolution patterns (synthesize from resolution_steps)
    resolution_step_counts = Counter()
    for call, _ in items:
        for step in call.get('resolution_steps', []):
            step_lower = step.lower()
            # Categorize steps
            if 'transfer' in step_lower or 'connect' in step_lower:
                resolution_step_counts['Transferred/connected caller to specialist agent'] += 1
            elif 'verify' in step_lower or 'confirm' in step_lower or 'check' in step_lower:
                resolution_step_counts['Verified caller identity and policy details'] += 1
            elif 'process' in step_lower and 'payment' in step_lower:
                resolution_step_counts['Processed payment transaction'] += 1
            elif 'email' in step_lower and ('sent' in step_lower or 'send' in step_lower or 'confirm' in step_lower):
                resolution_step_counts['Sent confirmation/documentation via email'] += 1
            elif 'voicemail' in step_lower or 'message' in step_lower:
                resolution_step_counts['Left voicemail or took message for callback'] += 1
            elif 'explain' in step_lower or 'clarif' in step_lower:
                resolution_step_counts['Explained policy details or procedures to caller'] += 1
            elif 'hold' in step_lower:
                resolution_step_counts['Placed caller on hold to research'] += 1
            elif 'callback' in step_lower or 'follow up' in step_lower or 'follow-up' in step_lower:
                resolution_step_counts['Arranged callback or follow-up'] += 1
            elif 'collect' in step_lower or 'gather' in step_lower:
                resolution_step_counts['Collected caller information and details'] += 1
            elif 'quote' in step_lower:
                resolution_step_counts['Initiated or provided quote'] += 1
            elif 'cancel' in step_lower:
                resolution_step_counts['Initiated cancellation process'] += 1
            elif 'claim' in step_lower:
                resolution_step_counts['Initiated or processed claim'] += 1

    # Top resolution patterns
    resolution_patterns = [pattern for pattern, _ in resolution_step_counts.most_common(5) if resolution_step_counts[pattern] >= 2]
    if not resolution_patterns:
        resolution_patterns = [pattern for pattern, _ in resolution_step_counts.most_common(3)]

    # Edge cases
    edge_cases = []
    for call, cls in items:
        if cls['confidence'] == 'low':
            edge_cases.append(f"Low-confidence classification: {call['caller_intent'][:100]}... (file: {call['file']})")
        # Multi-intent detection
        intent_lower = call.get('caller_intent', '').lower()
        multi_signals = sum([
            bool(re.search(r'\band\b.{0,30}\b(also|additionally|as well)\b', intent_lower)),
            bool(re.search(r'\bboth\b', intent_lower)),
            bool(re.search(r'\balso\b', intent_lower)),
        ])
        if multi_signals >= 1 and 'and' in intent_lower:
            # Check for actual multiple intents
            summary_lower = call.get('summary', '').lower()
            intent_keywords = ['payment', 'quote', 'claim', 'cancel', 'add', 'remove', 'update', 'coverage', 'renew']
            found = [kw for kw in intent_keywords if kw in intent_lower]
            if len(found) >= 2:
                edge_cases.append(f"Multi-intent call ({', '.join(found)}): {call['caller_intent'][:100]}... (file: {call['file']})")

    # Limit edge cases
    edge_cases = edge_cases[:5]

    # Pick 3 representative examples (prefer high confidence)
    high_conf = [(call, cls) for call, cls in items if cls['confidence'] == 'high']
    med_conf = [(call, cls) for call, cls in items if cls['confidence'] == 'medium']
    low_conf = [(call, cls) for call, cls in items if cls['confidence'] == 'low']

    examples_pool = high_conf[:3] if len(high_conf) >= 3 else high_conf + med_conf[:3-len(high_conf)]
    if len(examples_pool) < 3:
        examples_pool += low_conf[:3-len(examples_pool)]
    examples_pool = examples_pool[:3]

    examples = []
    for call, cls in examples_pool:
        examples.append({
            'file': call['file'],
            'intent': call['caller_intent'],
            'summary': call['summary']
        })

    type_digests[etype] = {
        'count': count,
        'resolution_patterns': resolution_patterns,
        'knowledge_required': sorted(list(all_knowledge)),
        'systems_referenced': sorted(list(all_systems)),
        'outcome_distribution': dict(outcomes),
        'edge_cases': edge_cases,
        'examples': examples
    }

# ===== BUILD OUTPUT =====
output = {
    'batch': 3,
    'total_classified': len(classifications),
    'classifications': classifications,
    'type_digests': type_digests
}

with open(OUTPUT_FILE, 'w') as f:
    json.dump(output, f, indent=2)

# Print summary
print(f"\nTotal classified: {len(classifications)}")
print(f"\nDistribution:")
dist = Counter(c['engagement_type'] for c in classifications)
for k, v in sorted(dist.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

conf_dist = Counter(c['confidence'] for c in classifications)
print(f"\nConfidence: {dict(conf_dist)}")
print(f"\nOutput written to: {OUTPUT_FILE}")
