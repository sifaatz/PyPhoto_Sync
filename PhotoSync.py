"""

For every file in Sync:

    1) Index target-folgders of existing files
        file: (name, size)

    2) read new files
        * get metadata of file
        * check if file exists in index
        * compute Target-Path for file
        * Copy file and add to index

"""

from pathlib import Path
import logging
from typing import Text, List, Dict
import pickle
import os
from shutil import copyfile
from PIL import Image, ExifTags
from datetime import datetime
import hashlib

import conf

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    #filename='PhotoSync.log',
                    )

logger.info("start file")

# Config:
print(conf.import_types)
print(conf.catalog_file)
print(conf.exclude_targetfolders)

target_path = Path(conf.target_path)
source_path = Path(conf.source_path)


class PictureSync:

    def __init__(self, catalog_file: Path):
        """
            Load pickled catalog with file list.

        :param catalog_file:      here is the pickle file
        :param targetfolders_path:    list of Folders target photos
        """

        self.catalog_file = catalog_file
        copyfile(self.catalog_file, self.catalog_file+"_Backup")
        logger.info(self.catalog_file)

        try:
            self.catalog = pickle.load(open(self.catalog_file, "rb"))
            logger.info("Loaded pickled files: {0}, {1}, {2}"
                        .format(len(self.catalog), self.catalog_file, type(self.catalog)))

            for i in self.catalog.items():          # for dev only
                print(i)

        except Exception as e:
            logger.warning("No index-file to read here.")
            print(e)
            self.catalog = dict()
            logger.warning("Empty catalog created, {}".format(self.catalog))


    def update_catalog(self, path: Path):
        """
           Adds (new) files from given folders to list of catalog.
        """
        collect_files = []
        collect_files.extend(PictureSync.get_files_from_dir(path))         # added all files in dir and subdirectories.
        logger.info("UPDATE CATALOG: Found {} files in targetfolders".format(len(collect_files)))

        # add new files to catalog, if existing
        for f in collect_files:
            f_hash = self.get_hash(f)
            if f_hash not in self.catalog:
                metadata = PictureSync.get_image_metadata(f)
                self.catalog[f_hash] = metadata                     # append to catalog
            elif f_hash in self.catalog:
                self.catalog[f_hash]["import_counter"] += 1

        # load existing Files from pickle into list
        self.dump_catalog()

        return collect_files


    def dump_catalog(self):
        pickle.dump(self.catalog, open(self.catalog_file, "wb"))
        logger.info("Pickled file-list of {} into {}".format(len(self.catalog), self.catalog_file))


    @staticmethod
    def get_files_from_dir(path: Path):
        """
            Returns files of path filtered for import-types.
        :param mode:    take file-name (none or "filename") OR return file+path
        :return: list of filenames as Text
        """
        file_list = []
        logger.info("directory: {}".format(path))
        for p in path.iterdir():
            logger.debug("Path: {}".format(p))
            if p.is_dir() and not p.parts[-1] in conf.exclude_targetfolders:
                file_list.extend(PictureSync.get_files_from_dir(p))
            elif p.suffix.lower() in conf.import_types:
                file_list.append(p)

        return file_list

    def import_files(self, source_path: Path):
        """
            Iterates over import-path to find new files.
            Load files if not exits.
            Copies new files into structure.
        :param source_path:
        """
        new_files = PictureSync.get_files_from_dir(source_path)
        logger.info("IMPORT: Found files in Source: {} in {}".format(len(new_files), source_path))

        # iterate new files:
        for f in new_files:
            f_hash = self.get_hash(f)

            if f_hash not in self.catalog:
                metadata = PictureSync.get_image_metadata(f)
                logger.debug("New file found: {}".format(f))

                #ToDo: copy_new_file(pfile, metadata)
                #ToDo: add file to catalog



    def copy_new_file(self, pfile: Path, metadata: Dict):

        self.catalog[pfile.as_posix()] = metadata

        #ToDo: derive path-information as copy target
        #       * jpg: by data and size
        #       * rest: by exec data

        pass


    @staticmethod
    def get_image_metadata(fpath: Text):
        fpath =  Path(fpath)
        logger.debug("get metadata of {}".format(fpath.as_posix()))
        st_mtime = fpath.stat().st_mtime
        st_mdatetime = datetime.fromtimestamp(st_mtime).strftime("%Y-%m-%d_%H:%M:%S")

        metadata = {"filename": fpath.name,
                    "filetype": fpath.suffix,
                    "filesize (MB)": str(round(fpath.stat().st_size/1024/1024, 3)),
                    "file_mtime": st_mdatetime,
                    "catalog_path": fpath,
                    "catalog_inserted_at": datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
                    "catalog_deleted_at": None,
                    "import_counter": 0,
                    }
        if fpath.suffix.lower() not in [".jpg", ".jpeg"]:
            logger.info('no picture, no exif')
            return metadata

        exif_tags = ['DateTimeOriginal', 'ExifImageWidth', 'ExifImageHeight', 'Make', 'Model',
                     'GPSInfo', 'LensModel', 'Orientation']
        exif_info = PictureSync.read_exif(fpath, exif_tags)

        if not exif_info is None:           # return only if file is valid / openable
            for e in exif_tags:
                metadata[e] = exif_info[e]

            return metadata

    @staticmethod
    def get_hash(fpath: Path):
        hasher = hashlib.md5()
        with open(fpath, 'rb') as afile:
            buf = afile.read()
            hasher.update(buf)
        return hasher.hexdigest()

    @staticmethod
    def read_exif(fpath: Path, tag_list: List[Text]):
        try:
            img = Image.open(fpath)
        except:
            logger.warning('Corrupt file: {}'.format(fpath))
            return None

        try:
            exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
        except Exception as e:
            logger.warning('No exif in file {}, {}'.format(fpath, e))
            exif = dict()

        tags = {key: exif[key] for key in exif if key in tag_list}      # add existing tags
        no_tags = {tag: None for tag in tag_list if tag not in tags}
        tags.update(no_tags)
        logger.debug("exif: {}".format(tags))
        return tags


    def classify_media(self, metadata):
        """
            Classifies the file in categories: photo, video, screenshot, gif, other...
            Later: copy into folder by this categories.
        :param metadata:
        :return:
        """
        #if metadata filetype ==
        #    ...
        #size...


        #metadata['MediaClass'] = ''
        #return metadata

        pass


def main():

    # 1) Initialize and load Catalog
    ps = PictureSync(conf.catalog_file)

    # 2) Update catalog by source-folder
    ps.update_catalog(Path(conf.target_path))

    # 3) Load new files
    ps.import_files(source_path)


    # 4) Maintain catalog: mark deleted files (but keep)


if __name__ == "__main__":
    main()
