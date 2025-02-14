import csv
from datetime import datetime

class FileHandler:
    def __init__(self, record_file, keywords_file):
        self.record_file = record_file
        self.keywords_file = keywords_file

    def load_keywords(self):
        try:
            with open(self.keywords_file, 'r') as file:
                reader = csv.reader(file)
                return [row[0] for row in reader if row and row[0].strip()]
        except FileNotFoundError:
            return []

    def save_keywords(self, keywords):
        with open(self.keywords_file, 'w', newline='') as file:
            writer = csv.writer(file)
            for kw in keywords:
                writer.writerow([kw])

    def load_recorded(self):
        try:
            records = []
            try:
                with open(self.record_file, 'r') as file:
                    # Check if file is empty
                    first_line = file.readline().strip()
                    if not first_line:  # File is empty
                        self.create_file_with_header()
                        return []
                    
                    # Reset file pointer to start
                    file.seek(0)
                    
                    # Check if header exists
                    reader = csv.reader(file)
                    headers = next(reader)
                    if len(headers) < 2 or headers != ['Timestamp', 'Text']:
                        # No proper header, treat first line as data
                        file.seek(0)
                        
                    # Read all records
                    for row in reader:
                        if len(row) >= 2:
                            text = row[1]
                            if text.startswith('[') and '] ' in text:
                                text = text.split('] ', 1)[1]
                            records.append({'timestamp': row[0], 'text': text})
                        elif len(row) == 1:
                            records.append({
                                'timestamp': datetime.now().strftime("%H:%M:%S"),
                                'text': row[0]
                            })
                            
                    return records
                    
            except FileNotFoundError:
                self.create_file_with_header()
                return []
                
        except Exception as e:
            print(f"Error loading records: {str(e)}")
            self.create_file_with_header()
            return []

    def create_file_with_header(self):
        with open(self.record_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Text'])

    def save_recorded(self, recorded_logs):
        with open(self.record_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Text'])
            for record in recorded_logs:
                writer.writerow([record['timestamp'], record['text']])