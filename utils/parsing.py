import re

def parse_structured_sections(text: str):
    sections = re.split(r'###\s*', text)
    result = {}
    for section in sections:
        if not section.strip():
            continue
        header, *content = section.split('###', 1)
        header = header.strip().replace(' ', '_').lower()
        result[header] = '###'.join(content).strip()
    return result
