with open('test_file.txt', 'r') as f:
    for line in f:
        line = line.split('#')[0].strip()
        print(line)
