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
from PIL import Image, ExifTags
from datetime import datetime


logger = logging.getLogger(__name__)
logger.info("start file")

import_types = [".png", ".jpg", ".mov", ".jpeg", ".gif", ]

catalog_file = Path("D:/#IT/03_Python/PyPhotopfleger/PhotoImport_photoindex.p")

source_path = Path("D:/#IT/03_Python/PyPhotopfleger/PhotoSync_source")  # neue Files
#D:\#Fotos\iPhone_Import\111APPLE

target_path = Path("D:/#IT/03_Python/PyPhotopfleger")  # hier einsortieren
target_folders = ["PhotoSync_target"]




class PictureSync:

    def __init__(self, catalog_file: Path, targetfolders_path: List[Path]):
        """
            Load list of all existing files from pickled catalog.
        :param catalog_file:      here is the pickle file
        :param targetfolders_path:    list of Folders target photos
        """

        self.targetfolders_path = targetfolders_path
        self.catalog_file = catalog_file
        print(self.catalog_file)

        try:
            self.catalog = pickle.load(open(self.catalog_file, "rb"))
            logger.info("Loaded pickled files: {0}, {1}, {2}"
                        .format(len(self.catalog), self.catalog_file, type(self.catalog)))

            for i in self.catalog.items():
                print(i)

        except Exception as e:
            logger.warning("No index-file to read here.")
            print(e)
            self.catalog = dict()
            logger.warning("Empty catalog created, {}".format(self.catalog))


    def update_catalog(self, path):
        """
           Adds (new) files from given folders to list of catalog.
        """
        collect_files = []
        collect_files.extend(PictureSync.get_files_from_dir(path))         # added all files in dir and subdirectories.
        logger.info("Found {} files in targetfolders_path".format(len(collect_files)))

        # add new files to catalog, if existing
        for f in collect_files:
            if f not in self.catalog:
                metadata = PictureSync.get_image_metadata(f)
                self.catalog[f] = metadata
            elif f in self.catalog:
                self.catalog[f]["import_counter"] += 1

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
        for p in path.iterdir():
            logger.debug("Path: {}".format(p))
            if p.is_dir():
                file_list.extend(PictureSync.get_files_from_dir(p))
            elif p.suffix.lower() in import_types:
                file_list.append(p.as_posix())

        return file_list


    def load_files(self, source_path, targetfolder_path):
        """
            Iterates over load-path to find new files.
            Load files if not exits.
            Copies new files into structure.
        :param source_path:
        :param target_path:
        :return:
        """
        new_files = PictureSync.get_files_from_dir(source_path)
        logger.info("Found files in Source: {} in {}".format(len(new_files), source_path))

        catalog_files = [Path(f).name for f in self.catalog]
        catalog_file_path = [(Path(f).name, f) for f in self.catalog]

        # iterate new files:
        for f in new_files:
            metadata = PictureSync.get_image_metadata(f)

            if f.name not in catalog_files:
                logger.info("New file found: {}".format(f))
                #ToDo: copy_new_file(pfile, metadata)
                #ToDo: add file to catalog

            elif metadata["filesize (MB)"] == f["filesize (MB)"]:
                pass


    def copy_new_file(self, pfile: Path, metadata: Dict):

        self.catalog[pfile.as_posix()] = metadata

        #ToDo: derive path-information as copy target
        #       * jpg: by data and size
        #       * rest: by exec data

        pass



    @staticmethod
    def get_image_metadata(fpath: Text):
        fpath = Path(fpath)
        logger.debug("get metadata of {}".format(fpath.as_posix()))

        metadata = {"filename": fpath.name,
                    "filetype": fpath.suffix,
                    "filesize (MB)": str(round(fpath.stat().st_size/1024/1024, 3)),
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

        for e in exif_tags:
            metadata[e] = exif_info[e]

        return metadata #self.classify_media(metadata)


    @staticmethod
    def read_exif(fpath: Path, tag_list: List[Text]):
        img = Image.open(fpath)
        try:
            exif = {ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}
        except Exception as e:
            logger.warning('No exif in file, {}'.format(e))
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
        if metadata filetype ==
            ...
        size...


        metadata['MediaClass'] = ''
        return metadata



def main():

    targetfolders_path = [target_path.joinpath(x) for x in target_folders]
    logging.info("Target-Folders: {}".format(targetfolders_path))

    # 1a) Load index
    ps = PictureSync(catalog_file, targetfolders_path)

    # 1b) Update catalog
    #ps.update_catalog(source_path)

    # 2b) Initially create index (1x)
    for p in targetfolders_path:
        ps.update_catalog(p)

    # 3) Load new files
    ps.load_files(source_path, targetfolders_path)




if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        )
    main()
