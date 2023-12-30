import difflib

def compare_files(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    differ = difflib.Differ()
    diff = differ.compare(lines1, lines2)

    with open('output.html', 'w') as output:
        output.write('<html><body><pre>\n')
        for line in diff:
            if line.startswith(' '):
                output.write(line)
            elif line.startswith('-'):
                output.write(f'<span style="color: red;">{line}</span>')  # Red for deleted lines
            elif line.startswith('+'):
                output.write(f'<span style="color: green;">{line}</span>')  # Green for added lines
        output.write('</pre></body></html>\n')

if __name__ == "__main__":
    compare_files("bot1.py", "bot5.py")
