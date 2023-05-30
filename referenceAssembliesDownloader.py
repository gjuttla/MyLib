import argparse
from enum import Enum
import os
import requests
from distutils.dir_util import copy_tree
import tempfile
import zipfile

DOTNET_FRAMEWORK_TFMS = [
    # 'net20',
    # 'net35',
    'net40',
    # 'net45',
    # 'net451',
    # 'net452',
    # 'net46',
    # 'net461',
    # 'net462',
    # 'net47',
    # 'net471',
    # 'net472',
    # 'net48',
    # 'net481'
]


MARKER_FILE = 'ref_assemblies_downloaded.txt'
PROGRESS_MARKER_FILE = 'in_progress.txt'

class ReferenceAssembliesSource(Enum):
    LOCAL = 'local'
    ARTIFACTORY = 'artifactory'
    NUGET = 'nuget'

    def __str__(self):
        return self.value

def log(msg: str):
    print(f'[ReferenceAssembliesDownloader] {msg}', flush=True)


def get_version_from_tfm(tfm):
    version = '.'.join(tfm[3:])
    return f'v{version}'


def ensure_target_dir(target_dir: str):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)


def clear_dir(dir: str):
    if os.path.exists(dir):
        shutil.rmtree(dir)

    ensure_target_dir(dir)


def nuget_download(target_dir: str):
    REF_ASS_VER = '1.0.3'
    temp_dir = tempfile.gettempdir()
    target_dir_base = os.path.join(target_dir, '.NETFramework')

    log('Downloading reference assemblies from NuGet\n'
        f'  - target_dir = {target_dir}\n'
        f'  - temp_dir = {temp_dir}'
    )

    for framework_ver in DOTNET_FRAMEWORK_TFMS:
        version_str = get_version_from_tfm(framework_ver)
        target_dir_for_framework = os.path.join(target_dir_base, version_str)

        clear_dir(target_dir_for_framework)

        url = f'https://www.nuget.org/api/v2/package/Microsoft.NETFramework.ReferenceAssemblies.{framework_ver}/{REF_ASS_VER}'

        log(f'downloading reference assemblies for {framework_ver} from {url}')
        response = requests.get(url, stream=True, allow_redirects=True)

        base_name = f'ref_{framework_ver}'
        download_filename = f'{base_name}.zip'
        download_filepath = f'{os.path.join(temp_dir, download_filename)}'
        extract_folder = os.path.join(temp_dir, base_name)

        with open(download_filepath, 'wb') as f:
            f.write(response.content)

        with zipfile.ZipFile(download_filepath) as zip:
            zip.extractall(extract_folder)

        ref_ass_source_dir = os.path.join(extract_folder, 'build', '.NETFramework')
        dirlist = [ item for item in os.listdir(ref_ass_source_dir) if os.path.isdir(os.path.join(ref_ass_source_dir, item)) ]
        dir_for_framework = dirlist[0] # last part of build/.NETFramework/v1.2.3, there must be only one dir
        
        copy_tree(os.path.join(ref_ass_source_dir, dir_for_framework), target_dir_for_framework)

    with open(os.path.join(target_dir, MARKER_FILE), 'w') as marker:
        marker.write('done')


def mark_progress(file):
    with open(file, 'w') as marker:
        marker.write('')


def del_progress_marker(file):
    if (os.path.exists(file)):
        os.remove(file)


def main():
    parser = argparse.ArgumentParser(description='.NET Framework reference assemblies downloader', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--source', type=ReferenceAssembliesSource, choices=list(ReferenceAssembliesSource), help='Reference assemblies source', required=True)
    parser.add_argument('--target', type=str, help='Reference assemblies target directory', required=True)
    args = parser.parse_args()

    if len(args.target) == 0:
        raise ValueError('empty target dir')

    ensure_target_dir(args.target)
    progress_marker = os.path.join(args.target, PROGRESS_MARKER_FILE)
    if (os.path.exists(progress_marker)):
        exit(0)

    mark_progress(progress_marker)

    match args.source:
        case ReferenceAssembliesSource.LOCAL:
            raise NotImplementedError(f'source {args.source} not yet supported')
        case ReferenceAssembliesSource.ARTIFACTORY:
            raise NotImplementedError(f'source {args.source} not yet supported')
        case ReferenceAssembliesSource.NUGET:
            nuget_download(args.target)
        case None:
            raise ValueError('no source provided, see help')

    del_progress_marker(progress_marker)


if __name__ == "__main__":
    main()
