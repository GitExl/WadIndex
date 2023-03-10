from typing import List, Optional

from archives.archivebase import ArchiveBase
from archives.archivefilebase import ArchiveFileBase


class ArchiveList:

    def __init__(self):
        self.archives: List[ArchiveBase] = []

    def append(self, archive: ArchiveBase):
        self.archives.append(archive)

    def file_find_basename(self, file_basename: str, include_main: bool = True) -> Optional[ArchiveFileBase]:
        for archive in reversed(self.archives):
            if not include_main and archive.is_main:
                continue

            file = archive.file_find_basename(file_basename)
            if file is not None:
                return file

        return None

    def file_find_all_basename(self, file_basename: str, include_main: bool = True) -> List[ArchiveFileBase]:
        files: List[ArchiveFileBase] = []

        for archive in reversed(self.archives):
            if not include_main and archive.is_main:
                continue

            file = archive.file_find_basename(file_basename)
            if file is not None:
                files.append(file)

        return files

    def file_find_regexp(self, regexp: str, include_main: bool = True) -> Optional[ArchiveFileBase]:
        for archive in reversed(self.archives):
            if not include_main and archive.is_main:
                continue

            file = archive.file_find_regexp(regexp)
            if file is not None:
                return file

        return None

    def file_find_all_regexp(self, regexp: str, include_main: bool = True) -> List[ArchiveFileBase]:
        files = []

        for archive in reversed(self.archives):
            if not include_main and archive.is_main:
                continue

            archive_files = archive.file_find_all_regexp(regexp)
            if archive_files is not None:
                files.extend(archive_files)

        return files

    def close(self, iwads: bool = True):
        for archive in self.archives:
            if (archive.is_main and iwads) or not archive.is_main:
                archive.close()
