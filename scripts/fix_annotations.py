"""Fix mitdb_annotations.mat: rename numeric variables to r_ prefix."""
import scipy.io as sio
import sys
import os

matfile = sys.argv[1]
backup = matfile.replace('.mat', '_backup.mat')

# Backup
import shutil
shutil.copy2(matfile, backup)

# Read
data = sio.loadmat(matfile)
keep = {k: v for k, v in data.items() if not k.startswith('__')}

# Rename
renamed = {}
for k, v in keep.items():
    renamed['r_' + k] = v

# Save
sio.savemat(matfile, renamed)
print('Converted %d variables, backup at %s' % (len(renamed), backup))
print('Variables:', sorted(renamed.keys()))
