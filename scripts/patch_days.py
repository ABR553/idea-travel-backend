"""Patch seed_data.py to add days= to _dest calls and nights= to _make_accommodation calls."""
import re

SEED_PATH = "/app/app/seeds/seed_data.py"

# photo_id_fragment -> days for each destination
DEST_DAYS = {
    "photo-1502602898657": 5,   # Paris
    "photo-1552832230": 3,      # Roma
    "photo-1541370976299": 3,   # Florencia
    "photo-1523906834658": 2,   # Venecia
    "photo-1533606688076": 2,   # Amalfi
    "photo-1543783207": 3,      # Madrid
    "photo-1583422409516": 4,   # Barcelona
    "photo-1569347204803": 2,   # Ljubljana
    "photo-1583425423320": 1,   # Bled
    "photo-1555990538-1a": 1,   # Plitvice
    "photo-1555990538-70": 3,   # Dubrovnik
    "photo-1540959733332": 5,   # Tokyo
    "photo-1493976040374": 4,   # Kyoto
    "photo-1590559899731": 3,   # Osaka
    "photo-1529655683826": 5,   # London
    "photo-1531366936337": 2,   # Bergen
    "photo-1601581875309": 2,   # Geiranger
    "photo-1506905925346": 1,   # Flam
    "photo-1535083783855": 2,   # Stavanger
    "photo-1611348524140": 1,   # Nairobi
    "photo-1547471080": 3,      # Masai Mara
    "photo-1516426122078": 1,   # Nakuru
    "photo-1535941339077": 2,   # Amboseli
}

with open(SEED_PATH, "r") as f:
    lines = f.readlines()

new_lines = []
current_dest_days = None
i = 0
while i < len(lines):
    line = lines[i]

    # Detect _dest(pk, call and find its days
    if "_dest(pk," in line and "days=" not in line:
        for photo_frag, days in DEST_DAYS.items():
            if photo_frag in line:
                current_dest_days = days
                break
        else:
            current_dest_days = None

    # If we're inside a _dest call that needs days=, find the closing line
    # The _dest calls end with one of these patterns:
    #   )   (no accs, no exps - like original Nairobi)
    #   ],  (closing accs= or exps=)
    # We add days=N by modifying the _dest( line itself
    if current_dest_days and "_dest(pk," in line:
        # Replace _dest(pk, N, "url", to _dest(pk, N, "url", days=D,
        # by finding the closing quote + comma of the URL
        # Pattern: _dest(pk, 0, "https://...?w=800",
        new_line = re.sub(
            r'(_dest\(pk, \d+, "https://[^"]+",)',
            rf'\1 days={current_dest_days},',
            line
        )
        if new_line != line:
            new_lines.append(new_line)
            current_dest_days = None
            i += 1
            continue

    new_lines.append(line)
    i += 1

# Now handle nights in accommodations
# Each accommodation is within a destination. We need to figure out the nights
# from the destination's days. The approach: when we see a _dest call with days=N,
# all _make_accommodation calls within that dest should get nights=N
content = "".join(new_lines)

# Find all _dest calls with days=N, then set nights=N on their accommodations
# We'll do a simpler approach: scan through and track current days
final_lines = content.split("\n")
result = []
current_nights = 1
for line in final_lines:
    # Detect days= in _dest calls
    m = re.search(r"days=(\d+)", line)
    if m and "_dest(pk," in line:
        current_nights = int(m.group(1))

    # Add nights= to _make_accommodation calls that don't have it
    if "_make_accommodation(" in line and "nights=" not in line and "def " not in line:
        # This is a call to _make_accommodation - add nights at the booking_url line
        pass  # We'll handle this differently

    result.append(line)

# Better approach for nights: find each booking_url="..."), and add nights=N before )
content2 = "\n".join(result)

# Track which destination context we're in by finding days=N in _dest calls
# Then replace all booking_url=... ) within that context
parts = re.split(r"(days=\d+,)", content2)
output_parts = []
current_n = 1
for part in parts:
    m = re.match(r"days=(\d+),", part)
    if m:
        current_n = int(m.group(1))
        output_parts.append(part)
    else:
        # Replace booking_url="..."), with booking_url="...", nights=N),
        # But only for _make_accommodation calls (not add_pack or others)
        modified = re.sub(
            r'(booking_url="[^"]*")\)',
            rf'\1, nights={current_n})',
            part
        )
        output_parts.append(modified)

final = "".join(output_parts)

with open(SEED_PATH, "w") as f:
    f.write(final)

# Count changes
days_count = len(re.findall(r"days=\d+", final))
nights_count = len(re.findall(r"nights=\d+", final))
print(f"Patched: {days_count} days= values, {nights_count} nights= values (includes defaults in func def)")
