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

print('creating archive')
zf = zipfile.ZipFile('zipfile_write_compression.zip', mode='w')
try:
    print('adding files with compression mode={}'.format(modes[compression]))
    zf.write('x', compress_type=compression)
    zf.write('a/x', compress_type=compression)
finally:
    print('closing')
    zf.close()
