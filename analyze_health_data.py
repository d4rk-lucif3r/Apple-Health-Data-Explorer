import xml.etree.ElementTree as ET
from collections import defaultdict
import datetime
import json

def analyze_xml_structure(file_path):
    """
    Analyze the structure of the Apple Health XML file and count record types
    """
    record_types = defaultdict(int)
    unique_attributes = defaultdict(set)
    date_ranges = defaultdict(lambda: {'min': None, 'max': None})
    
    try:
        # Iterate through XML using iterparse to handle large files
        for event, elem in ET.iterparse(file_path, events=('end',)):
            if elem.tag in ('Record', 'Workout', 'ActivitySummary'):
                # Count record types
                record_type = elem.get('type') if elem.tag == 'Record' else elem.tag
                record_types[record_type] += 1
                
                # Collect unique attributes
                for attr in elem.attrib:
                    unique_attributes[elem.tag].add(attr)
                
                # Track date ranges
                if 'startDate' in elem.attrib:
                    date = datetime.datetime.strptime(
                        elem.get('startDate').split()[0], 
                        '%Y-%m-%d'
                    )
                    if date_ranges[record_type]['min'] is None:
                        date_ranges[record_type]['min'] = date
                    if date_ranges[record_type]['max'] is None:
                        date_ranges[record_type]['max'] = date
                    date_ranges[record_type]['min'] = min(date_ranges[record_type]['min'], date)
                    date_ranges[record_type]['max'] = max(date_ranges[record_type]['max'], date)
            
            # Clear element to free memory
            elem.clear()
    
    except Exception as e:
        print(f"Error processing file: {e}")
        return None
    
    # Convert date ranges to string format
    for record_type in date_ranges:
        if date_ranges[record_type]['min']:
            date_ranges[record_type]['min'] = date_ranges[record_type]['min'].strftime('%Y-%m-%d')
        if date_ranges[record_type]['max']:
            date_ranges[record_type]['max'] = date_ranges[record_type]['max'].strftime('%Y-%m-%d')
    
    # Prepare results
    analysis = {
        'record_counts': dict(record_types),
        'attributes': {k: list(v) for k, v in unique_attributes.items()},
        'date_ranges': date_ranges
    }
    
    # Save results to file
    with open('health_data_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    return analysis

if __name__ == "__main__":
    print("Analyzing Apple Health Export...")
    results = analyze_xml_structure('apple_health_export/export.xml')
    if results:
        print("\nAnalysis complete! Results saved to health_data_analysis.json")
        print("\nRecord Types and Counts:")
        for record_type, count in results['record_counts'].items():
            print(f"{record_type}: {count:,}")