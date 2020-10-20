from PIL import Image, ExifTags
from pathlib import Path


test_file = Path("D:/#IT/03_Python/PyPhotopfleger/PhotoSync_target/best of no017.jpg")
test_file = Path("D:/#IT/03_Python/PyPhotopfleger/PhotoSync_target/2000/best of no011.jpg")
test_file = Path("D:/#IT/03_Python/PyPhotopfleger/PhotoSync_source/iPhone/IMG_0089.JPG")

img = Image.open(test_file)
exif_data = img._getexif()
exif_data


"""
exif = {
    ExifTags.TAGS[k]: v
    for k, v in img._getexif().items()
    if k in ExifTags.TAGS
}

for item in exif.items():
    print(item)

tag_list = ['DateTimeOriginal', 'ExifImageWidth', 'ExifImageHeight', 'Model']
tags = {key: exif[key] for key in exif if key in tag_list}

tags

type(tags)
"""


## get creation date of file ##
def get_mtime():
    p = Path("D:/#IT/03_Python/PyPhotopfleger/PhotoSync_target/best of no017 - Kopie.jpg")
    p = Path("D:/#IT/03_Python/PyPhotopfleger/PhotoSync_target/IMG_6544.MOV")

    print(dir(p.stat()))
    ctime = p.stat().st_mtime

    from datetime import datetime
    cdatetime = datetime.fromtimestamp(ctime).strftime("%Y-%m-%d_%H:%M:%S")
    print(cdatetime)


import hashlib
p = Path("D:/#IT/03_Python/PyPhotopfleger/PhotoSync_target/IMG_6544.MOV")

hasher = hashlib.md5()
with open(p, 'rb') as afile:
    buf = afile.read()
    hasher.update(buf)
print(hasher.hexdigest())


