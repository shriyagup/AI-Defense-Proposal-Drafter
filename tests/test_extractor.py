from app.services.extractor import extract_solicitation_data

sample_text = """
VALVE,SOLENOID
Active Opportunity
Notice ID
N0010426QLB05
Contract Opportunity Type
Solicitation
Date Offers Due
Mar 30, 2026 4:30 PM EDT
Published Date
Mar 13, 2026 7:12 PM EDT
Department/Ind. Agency
DEPT OF DEFENSE
Sub-tier
DEPT OF THE NAVY
Office
NAVSUP WEAPON SYSTEMS SUPPORT MECH
Product Service Code
4810 - VALVES, POWERED
NAICS Code
332919 - Other Metal Valve and Pipe Fitting Manufacturing
Description
This RFQ is for repair. The Government is seeking a Repair Turnaround Time (RTAT) of: 180 Days.
Government Source Inspection (GSI) is required.
BUY AMERICAN-FREE TRADE AGREEMENTS-BALANCE OF PAYMENTS PROGRAM-BASIC
NOTICE OF CYBERSECURITY MATURITY MODEL CERTIFICATION LEVEL REQUIREMENTS
SMALL BUSINESS SUBCONTRACTING PLAN
"""

result = extract_solicitation_data(sample_text)

print(result)