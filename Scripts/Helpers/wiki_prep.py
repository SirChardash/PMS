import bz2
import shutil
import subprocess
import urllib.request

from tqdm import tqdm


class DownloadProgressBar(tqdm):
    """This class is a copy paste from some stackoverflow answer. It renders download progress, as wiki files can take a
    while, especially if your network provider has an unfair implementation of 'fair play' network balancing."""

    def update_to(self, b=1, bsize=1, total_size=None):
        if total_size is not None:
            self.total = total_size
        self.update(b * bsize - self.n)


def download(url, output_path):
    """Downloads a file, utilizing DownloadProgressBar for progress display."""
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)


def extract_bz2(source, destination):
    """Extracts bz2 archives. Expect it to take a while."""
    with bz2.BZ2File(source) as fr, open(destination, "wb") as fw:
        shutil.copyfileobj(fr, fw)


def extract_docs(source, destination):
    """Calls a WikiExtractor script, since it doesn't have an easy usage flow as an import. It performs almost full
    plain-text extraction. It doesn't retain categories, only doc ids. Parameters don't need to be tinkered with. It
    is set to split output into 50Mb chunks, allowing for plain text inspection with most text editors. WikiExtractor
    doesn't work on Windows, and is the only component that doesn't."""
    subprocess.call(['python', '-m', 'wikiextractor.WikiExtractor',
                     '--quiet',
                     source,
                     '-b', '50M',
                     '-o', destination])
