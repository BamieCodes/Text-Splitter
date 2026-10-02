
import os
import sys

print("=== Multi-Functional Test File Generator ===")
print("Choose an option:")
print("[1] Generate using the default English template (This creates 'big_test_data.txt')")
print("[2] Generate by reading a real external file (e.g., 'external_source.txt')")

choice = input("Select option (1 or 2): ").strip()

real_content_pool = []

# --- OPTION 1: THE DEFAULT GENERATION ---
if choice == "1":
    print("Using default English template.")
    real_content_pool = ["Line of sample text featuring standard test formatting and emojis 🚀.\n"]

# --- OPTION 2: THE EXTERNAL FILE ACCESSIBILITY ---
elif choice == "2":
    source_filename = input("Enter the path of the real file to read from: ").strip()
    
    # Verify the file actually exists before proceeding
    if not os.path.isfile(source_filename):
        print(f"Error: The file '{source_filename}' does not exist! Check the name.")
        sys.exit(0)
        
    print(f"Reading content tokens from '{source_filename}'...")
    with open(source_filename, 'r', encoding='utf-8') as src:
        real_content_pool = src.readlines()
        
    if len(real_content_pool) == 0:
        print("Error: The source file you provided is completely empty!")
        sys.exit(0)
else:
    print("Invalid selection. Exiting program.")
    sys.exit(0)

# ----------------------------------------------------------------------
# DETERMINING THE OUTPUT TARGET FILENAME
# ----------------------------------------------------------------------
pool_size = len(real_content_pool)

output_filename = input("\nEnter the name for your new massive text file: ").strip()
if not output_filename:
    output_filename = "big_test_data.txt"  # Safe fallback default

print(f"\n🚀 Writing 30,000,000 lines to '{output_filename}'...")

# The main high-speed loop block
with open(output_filename, 'w', encoding='utf-8') as f:
    for i in range(1, 30000001):  # Generates exactly 30,000,000 lines
        
        # Sequentially cycle through whatever data is inside the pool i.e. if its just 3 senetenes, it loops through the sentences and cycles back to the first one again to continue
        current_line = real_content_pool[i % pool_size]
        
        # If the external line already contains a text prefix (e.g. line already exists just overwrite the line with the "Line "), we write it natively, 
        # otherwise we format it with the current line count index
        if current_line.startswith("Line "):
            f.write(current_line)
        else:
            f.write(f"Line {i}: {current_line}")
        
        # Milestone dashboard logging metric
        if i % 1000000 == 0:   # The remainder must always be zero else it'll be ignored
            print(f"Generated {i // 1000000}M lines...")  # i // 1000000 means divide i by 1000000 and keep only the integer neglecting the decimal

print(f"✅ Success! Created your massive file: '{output_filename}'.")


