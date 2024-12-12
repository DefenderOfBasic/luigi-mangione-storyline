import os
import re
from pathlib import Path
script_dir = os.path.dirname(os.path.abspath(__file__))
from datetime import datetime

def create_header_note():
    now = datetime.now()
    return f"""# Full Reddit Archive

Extracted by hezirel Dec 11 6pm EST ([see PR here](https://github.com/DefenderOfBasic/luigi-mangione-storyline/pull/3)). This markdown page is generated from the directory of reddit comments in the GitHub repo.

---

"""

def extract_date(file_content):
    # Look for date in format: Date: YYYY-MM-DD HH:MM:SS
    match = re.search(r'Date: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', file_content)
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.min
    return datetime.min

def convert_urls_to_links(text):
    # This regex finds URLs that aren't already part of a markdown link
    # It looks for URLs that don't follow '](' (which would indicate it's already in a markdown link)
    url_pattern = r'(?<!\]\()(https?://[^\s\)]+)'
    
    # Replace each URL with a markdown link version
    return re.sub(url_pattern, r'[\g<0>](\g<0>)', text)

def add_line_spaces_until_content(text):
    lines = text.split('\n')
    modified_lines = []
    
    for line in lines:
        if line.strip() == '## Content':
            modified_lines.append(line)
            # Stop adding spaces after this point
            modified_lines.extend(lines[len(modified_lines):])
            break
        else:
            # Add two spaces to the end of non-empty lines
            if line.strip():
                modified_lines.append(line + '  ')
            else:
                modified_lines.append(line)
                
    return '\n'.join(modified_lines)


def concat_md_files(directory, output_file='combined.md'):
    # Convert string path to Path object if needed
    dir_path = Path(directory)

    files_with_dates = []
    for md_file in dir_path.rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as infile:
                content = infile.read()
                date = extract_date(content)
                files_with_dates.append((date, md_file, content))
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
    
    # Sort by date
    files_with_dates.sort(key=lambda x: x[0], reverse=True)  # reverse=True for newest first

    # Combine all files
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(create_header_note())
        for date, md_file, content in files_with_dates:
            print(f'Adding: {md_file}')
            # Add file contents
            try:
                with open(md_file, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    new_content = convert_urls_to_links(content)
                    new_content = add_line_spaces_until_content(new_content)
                    outfile.write(new_content)
            except Exception as e:
                print(f"Error reading {md_file}: {e}")

# Example usage
directory = os.path.join(script_dir, 'reddit_archive') 
outpath = os.path.join(script_dir, 'reddit_archive.md')
concat_md_files(directory, outpath)
