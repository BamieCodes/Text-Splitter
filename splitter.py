import os
import sys
import math

def get_valid_input(prompt, validation_func, error_msg):
    """Helper function to repeatedly prompt user until valid input is given."""
    while True:
        try:
            val = input(prompt).strip()
            if validation_func(val):
                return val
            print(error_msg)
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled by user.")
            sys.exit(0)

def check_overwrite(filename):
    """Checks if a file exists and asks the user for permission to overwrite."""
    if os.path.exists(filename):
        choice = input(f"Warning: '{filename}' already exists. Overwrite? (y/n): ").strip().lower()
        if choice != 'y':
            print("Operation aborted by user.")
            sys.exit(0)

def generate_filename(prefix, index, total_parts, ext=".txt"):
    """Generates a zero-padded filename based on the total number of parts."""
    padding = max(2, len(str(total_parts)))
    return f"{prefix}_{str(index).zfill(padding)}{ext}"

def count_total_lines(filepath):
    """Counts total lines safely by streaming binary blocks instead of text loops."""
    print("Analyzing file structure...")
    count = 0
    with open(filepath, 'rb') as f:
        while True:
            buffer = f.read(1024 * 1024) # Read in 1MB chunks
            if not buffer:
                break
            count += buffer.count(b'\n')
    return count

def split_file(filepath, mode, chunk_limit, prefix):
    """
    Unified splitter engine. Reads raw blocks to remain immune to huge single lines,
    but inspects boundaries to ensure formatting and emojis stay perfect.
    """
    file_bytes = os.path.getsize(filepath)
    if file_bytes == 0:
        print("The source file is empty.")
        return

    # 1. Metric Pre-calculation
    if mode == '1': # Line Count Mode
        total_lines = count_total_lines(filepath)
        if total_lines == 0:
            print("No line breaks found. Defaulting to single file or size mode.")
            total_parts = 1
        else:
            total_parts = math.ceil(total_lines / chunk_limit)
    else: # File Size Mode
        limit_bytes = int(chunk_limit * 1024 * 1024)
        total_parts = math.ceil(file_bytes / limit_bytes)

    first_file = generate_filename(prefix, 1, total_parts)
    check_overwrite(first_file)

    # 2. Main Streaming Loop
    part_index = 1
    bytes_processed = 0
    buffer_size = 64 * 1024  # 64KB safe block limits
    out_f = None
    current_chunk_measure = 0  # Tracks lines (Mode 1) or bytes (Mode 2)

    with open(filepath, 'rb') as in_f:
        while bytes_processed < file_bytes:
            
            # Open a new file if needed
            if out_f is None:
                out_filename = generate_filename(prefix, part_index, total_parts)
                print(f"Creating {out_filename}...")
                out_f = open(out_filename, 'wb')

            # Read a tiny piece of the file
            data_block = in_f.read(buffer_size)
            if not data_block:
                break

            out_f.write(data_block)
            bytes_processed += len(data_block)

            # Update tracking metric
            if mode == '1':
                current_chunk_measure += data_block.count(b'\n')
                # Progress display for Line Mode
                print(f"\rStreaming bytes... {bytes_processed // 1024} KB processed", end="", flush=True)
            else:
                current_chunk_measure += len(data_block)
                # Progress display for Size Mode
                percent = (bytes_processed / file_bytes) * 100
                print(f"\rProgress: {percent:.1f}% ({bytes_processed // 1024} KB processed)...", end="", flush=True)

            # Check if we have met or exceeded our target chunk capacity
            target_limit = chunk_limit if mode == '1' else limit_bytes
            if current_chunk_measure >= target_limit:
                
                # --- THE UTF-8 & NEWLINE BOUNDARY SHIELD ---
                # Keep reading byte-by-byte to find a safe boundary
                while True:
                    next_byte = in_f.read(1)
                    if not next_byte:
                        break  # End of file reached
                    
                    out_f.write(next_byte)
                    bytes_processed += 1

                    # Condition A: Protect multi-byte UTF-8 structures (like emojis)
                    if 128 <= next_byte[0] <= 191:
                        continue # Continue reading until the character is whole

                    # Condition B: If in line mode, keep reading until the exact end of the line
                    if mode == '1' and next_byte != b'\n':
                        continue # Keep reading until the text sentence naturally hits a break

                    # Safe boundary confirmed, exit the protection loop
                    break

                # Close file and cycle trackers
                out_f.close()
                out_f = None
                current_chunk_measure = 0
                part_index += 1

        # Final loop cleanup safety step
        if out_f:
            out_f.close()

    print(f"\n\nSplit complete! Created {part_index if out_f is None else part_index - 1} files.")

def main():
    print("=== Ultimate Crash-Proof File Splitter ===")
    
    filepath = get_valid_input(
        prompt="Enter the path to the .txt file: ",
        validation_func=lambda p: os.path.isfile(p),
        error_msg="Error: File not found. Please enter a valid file path."
    )
    
    print("\nChoose Split Strategy:")
    print("[1] Split by Line Count (Safe for huge single lines too!)")
    print("[2] Split by File Size (MB)")
    strategy = get_valid_input(
        prompt="Select option (1 or 2): ",
        validation_func=lambda s: s in ['1', '2'],
        error_msg="Invalid selection. Type 1 or 2."
    )

    prefix = input("Enter naming convention prefix (Default: 'part'): ").strip() or "part"

    if strategy == '1':
        line_count = get_valid_input(
            prompt="Enter chunk size (number of lines per file): ",
            validation_func=lambda n: n.isdigit() and int(n) > 0,
            error_msg="Error: Please enter a positive integer greater than 0."
        )
        split_file(filepath, strategy, int(line_count), prefix)
        
    elif strategy == '2':
        size_mb = get_valid_input(
            prompt="Enter chunk size in MB (e.g., 1 or 0.5): ",
            validation_func=lambda s: float(s) > 0 if s.replace('.', '', 1).isdigit() else False,
            error_msg="Error: Please enter a positive numerical size value."
        )
        split_file(filepath, strategy, float(size_mb), prefix)

if __name__ == "__main__":
    main()