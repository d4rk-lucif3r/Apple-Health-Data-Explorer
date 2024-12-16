import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import json
import os
from tqdm.auto import tqdm
import sys
from collections import defaultdict

BATCH_SIZE = 1000  # Process records in batches

def safe_float(value, default=0.0):
    """Safely convert value to float"""
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default

def safe_parse_date(date_str):
    """Safely parse date string"""
    try:
        if not date_str:
            return None
        # Direct datetime parsing for known format: "YYYY-MM-DD HH:MM:SS +ZZZZ"
        return datetime.strptime(date_str.split('+')[0].strip(), '%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError, IndexError):
        return None

def create_directory(path):
    """Create directory if it doesn't exist"""
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        print(f"Error creating directory: {str(e)}")
        raise

def save_batch(records, filename):
    """Save a batch of records to CSV"""
    try:
        df = pd.DataFrame(records)
        mode = 'a' if os.path.exists(filename) else 'w'
        header = not os.path.exists(filename)
        df.to_csv(filename, mode=mode, header=header, index=False)
    except Exception as e:
        print(f"Error saving batch: {str(e)}")
        raise

def count_elements(xml_path):
    """Count total number of records and workouts"""
    print("Counting total records (this might take a moment)...")
    count = 0
    for _, elem in ET.iterparse(xml_path, events=('end',)):
        if elem.tag in ('Record', 'Workout'):
            count += 1
        elem.clear()
    return count

def preprocess_health_data(xml_path, output_dir='processed_data'):
    """Preprocess Apple Health data and save to CSV files"""
    try:
        print("\n🏥 Apple Health Data Preprocessing")
        print("=" * 40)
        
        if not os.path.exists(xml_path):
            raise FileNotFoundError(f"Input file not found: {xml_path}")
        
        create_directory(output_dir)
        
        # Initialize data containers for batches
        batches = {
            'heart_rate': [],
            'resting_heart_rate': [],
            'heart_rate_variability': [],
            'steps': [],
            'distance': [],
            'active_energy': [],
            'sleep': [],
            'workouts': []
        }
        
        # Track metadata
        all_data_types = set()
        data_ranges = defaultdict(lambda: {'min_date': None, 'max_date': None})
        record_counts = defaultdict(int)
        
        # Get total count for progress bar
        total_records = count_elements(xml_path)
        print(f"\nFound {total_records:,} records to process")
        
        def update_date_range(data_type, date):
            if date:
                if not data_ranges[data_type]['min_date']:
                    data_ranges[data_type]['min_date'] = date
                if not data_ranges[data_type]['max_date']:
                    data_ranges[data_type]['max_date'] = date
                data_ranges[data_type]['min_date'] = min(data_ranges[data_type]['min_date'], date)
                data_ranges[data_type]['max_date'] = max(data_ranges[data_type]['max_date'], date)

        def save_batch_if_full(data_type):
            if len(batches[data_type]) >= BATCH_SIZE:
                save_batch(batches[data_type], os.path.join(output_dir, f"{data_type}.csv"))
                batches[data_type] = []

        print("\n1. Processing XML file...")
        with tqdm(total=total_records, desc="Reading records", unit="records") as pbar:
            for event, elem in ET.iterparse(xml_path, events=('end',)):
                try:
                    if elem.tag == 'Record':
                        record_type = elem.get('type')
                        if record_type:
                            all_data_types.add(record_type)
                            date = safe_parse_date(elem.get('startDate'))
                            
                            if date:  # Only process records with valid dates
                                base_record = {
                                    'date': date,
                                    'endDate': safe_parse_date(elem.get('endDate')),
                                    'value': safe_float(elem.get('value')),
                                    'unit': elem.get('unit', ''),
                                    'source': elem.get('sourceName', '')
                                }
                                
                                update_date_range(record_type, date)
                                
                                # Sort records into appropriate containers
                                if record_type == 'HKQuantityTypeIdentifierHeartRate':
                                    batches['heart_rate'].append(base_record)
                                    save_batch_if_full('heart_rate')
                                elif record_type == 'HKQuantityTypeIdentifierRestingHeartRate':
                                    batches['resting_heart_rate'].append(base_record)
                                    save_batch_if_full('resting_heart_rate')
                                elif record_type == 'HKQuantityTypeIdentifierHeartRateVariabilitySDNN':
                                    batches['heart_rate_variability'].append(base_record)
                                    save_batch_if_full('heart_rate_variability')
                                elif record_type == 'HKQuantityTypeIdentifierStepCount':
                                    batches['steps'].append(base_record)
                                    save_batch_if_full('steps')
                                elif record_type == 'HKQuantityTypeIdentifierDistanceWalkingRunning':
                                    batches['distance'].append(base_record)
                                    save_batch_if_full('distance')
                                elif record_type == 'HKQuantityTypeIdentifierActiveEnergyBurned':
                                    batches['active_energy'].append(base_record)
                                    save_batch_if_full('active_energy')
                                elif record_type == 'HKCategoryTypeIdentifierSleepAnalysis':
                                    batches['sleep'].append(base_record)
                                    save_batch_if_full('sleep')
                                
                                record_counts[record_type] += 1
                                pbar.update(1)
                    
                    elif elem.tag == 'Workout':
                        date = safe_parse_date(elem.get('startDate'))
                        if date:
                            workout = {
                                'type': elem.get('workoutActivityType'),
                                'duration': safe_float(elem.get('duration')),
                                'date': date,
                                'endDate': safe_parse_date(elem.get('endDate')),
                                'distance': safe_float(elem.get('totalDistance')),
                                'energy': safe_float(elem.get('totalEnergyBurned')),
                                'source': elem.get('sourceName', '')
                            }
                            
                            batches['workouts'].append(workout)
                            save_batch_if_full('workouts')
                            
                            update_date_range('workouts', date)
                            record_counts['workouts'] += 1
                            pbar.update(1)
                
                finally:
                    elem.clear()
        
        # Save any remaining batches
        print("\n2. Saving remaining records...")
        with tqdm(total=len(batches), desc="Saving data files", unit="files") as pbar:
            for data_type, records in batches.items():
                if records:
                    save_batch(records, os.path.join(output_dir, f"{data_type}.csv"))
                pbar.update(1)
        
        # Save metadata
        print("\n3. Saving metadata...")
        metadata = {
            'last_processed': datetime.now().isoformat(),
            'data_types': list(all_data_types),
            'record_counts': record_counts,
            'data_ranges': {
                k: {
                    'min_date': v['min_date'].isoformat() if v['min_date'] else None,
                    'max_date': v['max_date'].isoformat() if v['max_date'] else None
                } for k, v in data_ranges.items()
            }
        }
        
        with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("\n✅ Preprocessing complete!")
        print("\nSummary:")
        print("-" * 40)
        for data_type, count in record_counts.items():
            print(f"• {data_type}: {count:,} records")
        print("-" * 40)
        print(f"Data saved in '{output_dir}' directory")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Processing interrupted by user. Saving progress...")
        # Save any remaining batches before exiting
        for data_type, records in batches.items():
            if records:
                save_batch(records, os.path.join(output_dir, f"{data_type}.csv"))
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error during preprocessing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    xml_path = 'apple_health_export/export.xml'
    preprocess_health_data(xml_path)