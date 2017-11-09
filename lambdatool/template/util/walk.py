import os


def find_data(starting_dir, the_dir):
    original_cwd = os.getcwd()
    tree = []
    try:
        os.chdir(starting_dir)
        for folder, subs, files in os.walk(the_dir):
            for file in files:
                tree.append('{}/{}'.format(folder, file))
    except Exception:
        pass

    os.chdir(original_cwd)
    return tree

if __name__ == '__main__':
    tree = find_data('aaa', 'bbb')
    for f in tree:
        print(f)
