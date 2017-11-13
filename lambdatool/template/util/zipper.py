import os
import zipfile
try:
    import zlib #noqa
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

modes = {
    zipfile.ZIP_DEFLATED: 'deflated',
    zipfile.ZIP_STORED:   'stored'
}


def create_zipfile():
    print('creating archive')
    zf = zipfile.ZipFile('/tmp/zipfile_write_compression.zip', mode='w')
    try:
        print('adding files with compression mode={}'.format(modes[compression]))
        zf.write('.', compress_type=compression)
        for f in find_data('.'):
            zf.write(f, compress_type=compression)
    finally:
        print('closing')
        zf.close()


def find_data(the_dir):
    tree = []
    try:
        for folder, subs, files in os.walk(the_dir):
            for file in files:
                tree.append('{}/{}'.format(folder, file))
    except Exception:
        pass

    return tree

if __name__ == '__main__':
    create_zipfile()
