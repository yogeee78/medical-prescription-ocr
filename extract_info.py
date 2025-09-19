import re

def extract_fields(text):
    fields = {}

    # Medicine (e.g., "Olabel 500mg" or "Paracetamol 250mg")
    med_match = re.search(r'([A-Za-z]+)\s*\d+mg', text, re.IGNORECASE)
    if med_match:
        fields["Medicine"] = med_match.group(0)

    # Dosage (e.g., "1 tab daily" or "2 tablets twice")
    dose_match = re.search(r'(\d+\s*(tab|tablet|capsule)\s*\w+)', text, re.IGNORECASE)
    if dose_match:
        fields["Dosage"] = dose_match.group(0)

    # Phone Number (formats like 123-456-7890 or 9876543210)
    phone_match = re.search(r'(\+?\d{2,3}[- ]?)?\d{3}[- ]?\d{3}[- ]?\d{4}', text)
    if phone_match:
        fields["Phone"] = phone_match.group(0)

    # Doctor (looks for "Dr." prefix)
    doctor_match = re.search(r'(Dr\.\s*[A-Za-z]+)', text)
    if doctor_match:
        fields["Doctor"] = doctor_match.group(0)

    return fields
