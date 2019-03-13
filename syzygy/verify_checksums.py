"""
Verify the checksum of a downloaded set of files (meant for tablebase).

The format of the checksum file to compare with is as follows:

    md5-hash  name-of-file
"""
import tqdm
import os
import argparse
import hashlib

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument('-c', '--checksum-file', help="Path to file containing checksums")
parser.add_argument('-d', '--root-folder', help="Path to folder containing all files to check")

args = parser.parse_args()

checksums = dict()
with open(args.checksum_file, 'r') as f:
    for line in f:
        if line.strip():
             checksum, name = line.strip().split()
             checksums[name] = checksum


for path in tqdm.tqdm(os.listdir(args.root_folder)):
    try:
        checksum = checksums[path]
    except KeyError:
        if not path == __file__ and not path == args.checksum_file:
            print(f'Missing checksum for file: {path}')
        continue

    if checksum != md5(path):
        print(f'{path}: Incorrect checksum. Expected {checksum[:10]}, got {md5(path)[:10]}')


