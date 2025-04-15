#!/usr/bin/env python3

import json
import sys
from typing import List, Dict, Set, Tuple
from pathlib import Path

class LegalCaseParser:
    def __init__(self):
        # Define all possible headers with both period and non-period variants
        self.headers = {
            'Number:', 'Settlement Date:', 'Settlement Dates:', 'Trial Date:', 
            'Arbitration Date:', 'Mediation Date:', 
            'Plff Atty:', 'Plff Atty.:', 
            'Def. Atty:', 'Def. Atty.:', 
            'Insurance Co:', 'Insurance Co.:', 
            'Plff Med:', 'Plff Med.:', 
            'Plff Exp:', 'Plff Exp.:', 
            'Def. Exp:', 'Def. Exp.:', 
            'Def. Med:', 'Def. Med.:', 
            'Trial Judge:', 'Arbitrator:', 'Mediator:', 'Judge:', 
            'Injuries:', 'Specials:', 'Result:', 'Settlement:', 
            'Settlement Judge:', 'Arbitration Judge:', 'Mediation Judge:'
        }
        
        # Map headers to field names
        self.header_to_field = {
            'Number:': 'case_number',
            'Settlement Date:': 'date',
            'Settlement Dates:': 'date',
            'Trial Date:': 'date',
            'Arbitration Date:': 'date',
            'Mediation Date:': 'date',
            'Plff Atty:': 'plaintiff_attorney',
            'Plff Atty.:': 'plaintiff_attorney',
            'Def. Atty:': 'defense_attorney',
            'Def. Atty.:': 'defense_attorney',
            'Insurance Co:': 'insurance_company',
            'Insurance Co.:': 'insurance_company',
            'Plff Med:': 'plaintiff_medical_expert',
            'Plff Med.:': 'plaintiff_medical_expert',
            'Def. Med:': 'defense_medical_expert',
            'Def. Med.:': 'defense_medical_expert',
            'Plff Exp:': 'plaintiff_expert',
            'Plff Exp.:': 'plaintiff_expert',
            'Def. Exp:': 'defense_expert',
            'Def. Exp.:': 'defense_expert',
            'Trial Judge:': 'judge_arbitrator_mediator',
            'Judge:': 'judge_arbitrator_mediator',
            'Settlement Judge:': 'judge_arbitrator_mediator',
            'Arbitration Judge:': 'judge_arbitrator_mediator',
            'Mediation Judge:': 'judge_arbitrator_mediator',
            'Arbitrator:': 'judge_arbitrator_mediator',
            'Mediator:': 'judge_arbitrator_mediator',
            'Injuries:': 'injuries',
            'Specials:': 'specials',
            'Settlement:': 'settlement',
            'Result:': 'result'
        }

    def find_next_header(self, text: str, start_pos: int = 0) -> Tuple[int, str]:
        """Find the next header in text starting from start_pos."""
        next_pos = len(text)
        found_header = None
        
        for header in sorted(self.headers, key=len, reverse=True):
            pos = text.find(header, start_pos)
            if pos != -1 and pos < next_pos:
                # Verify it's a standalone header (not part of another word)
                if pos == 0 or not text[pos-1].isalpha():
                    next_pos = pos
                    found_header = header
        
        return next_pos, found_header

    def extract_headers_and_content(self, line: str) -> List[Tuple[str, str]]:
        """Extract all headers and their associated content from a line."""
        results = []
        current_pos = 0
        
        while current_pos < len(line):
            # Find next header
            next_header_pos = len(line)
            found_header = None
            
            for header in sorted(self.headers, key=len, reverse=True):
                pos = line.find(header, current_pos)
                if pos != -1 and pos < next_header_pos:
                    # Verify it's not part of another word
                    if pos == 0 or not line[pos-1].isalpha():
                        next_header_pos = pos
                        found_header = header
            
            if not found_header:
                break
                
            # Move position to after header
            content_start = next_header_pos + len(found_header)
            
            # Find where this header's content ends (at next header or end of line)
            content_end = len(line)
            for header in self.headers:
                pos = line.find(header, content_start)
                if pos != -1 and pos < content_end:
                    content_end = pos
            
            # Extract content for this header
            content = line[content_start:content_end].strip()
            results.append((found_header, content))
            
            # Move to position after current content
            current_pos = content_end
        
        return results

    def is_all_caps_line(self, line: str) -> bool:
        """Check if line contains all uppercase letters (excluding punctuation)."""
        alpha_chars = ''.join(c for c in line if c.isalpha())
        return bool(alpha_chars and alpha_chars.isupper())

    def parse_legal_cases(self, text: str) -> List[Dict]:
        cases = [case.strip() for case in text.split('\n\n') if case.strip()]
        parsed_cases = []
        
        for case in cases:
            case_data = {
                'court': '',
                'case_name': '',
                'case_number': '',
                'date': '',
                'plaintiff_attorney': '',
                'defense_attorney': '',
                'plaintiff_medical_expert': '',
                'defense_medical_expert': '',
                'plaintiff_expert': '',
                'defense_expert': '',
                'judge_arbitrator_mediator': '',
                'insurance_company': '',
                'claim_type': '',
                'injury_type': '',
                'facts': '',
                'injuries': '',
                'specials': '',
                'settlement': '',
                'result': ''
            }
            
            lines = case.split('\n')
            if not lines:
                continue
            
            # First line is always court
            case_data['court'] = lines[0].strip()
            
            current_field = None
            collecting_case_name = True
            facts_started = False
            i = 1
            
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue
                
                # Check for headers in the line
                headers_and_content = self.extract_headers_and_content(line)
                
                if collecting_case_name:
                    if headers_and_content:
                        collecting_case_name = False
                        for header, content in headers_and_content:
                            field = self.header_to_field[header]
                            if field == 'judge_arbitrator_mediator' and case_data[field]:
                                case_data[field] += '; ' + header + ' ' + content
                            elif field == 'date' and case_data[field]:
                                case_data[field] += '; ' + header + ' ' + content
                            else:
                                case_data[field] = content
                    else:
                        if case_data['case_name']:
                            case_data['case_name'] += ' ' + line
                        else:
                            case_data['case_name'] = line
                
                elif headers_and_content:
                    current_field = None
                    for header, content in headers_and_content:
                        field = self.header_to_field[header]
                        if field == 'judge_arbitrator_mediator' and case_data[field]:
                            case_data[field] += '; ' + header + ' ' + content
                        elif field == 'date' and case_data[field]:
                            case_data[field] += '; ' + header + ' ' + content
                        else:
                            case_data[field] = content
                        current_field = field
                
                elif self.is_all_caps_line(line) and not facts_started:
                    current_field = None
                    if not case_data['claim_type']:
                        case_data['claim_type'] = line
                    elif not case_data['injury_type']:
                        case_data['injury_type'] = line
                        facts_started = True
                        current_field = 'facts'
                
                else:
                    # Continue collecting content for current field
                    if current_field:
                        if case_data[current_field]:
                            case_data[current_field] += ' ' + line
                        else:
                            case_data[current_field] = line
                    elif facts_started:
                        if case_data['facts']:
                            case_data['facts'] += ' ' + line
                        else:
                            case_data['facts'] = line
                
                i += 1
            
            parsed_cases.append(case_data)
        
        return parsed_cases

def main():
    input_file = Path('Cases.txt')
    output_file = Path('parsed_cases.json')
    
    # Check if input file exists
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    try:
        # Read input file
        print(f"Reading cases from {input_file}...")
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Parse cases
        print("Parsing cases...")
        parser = LegalCaseParser()
        parsed_cases = parser.parse_legal_cases(text)
        
        # Save to JSON
        print(f"Writing output to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_cases, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully parsed {len(parsed_cases)} cases to {output_file}")
        
    except Exception as e:
        print(f"Error processing files: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
