"""Drop this file on Maya's viewport to rig the character next to it.

It came from https://mutanttools.com/web-to-rig/ with the character, Unreal's
Manny skeleton fitted to it, its skin, and the Mutant Tools template guides.

If this Maya has no Mutant Tools yet, or one too old to have the WebToRig tool,
it first installs the latest release from GitHub, showing what it is doing.
Then it opens WebToRig on this folder, which imports the character, places the
template and builds the rig, one stage at a time.
"""
from __future__ import absolute_import, print_function

import json
import os
import shutil
import sys
import tempfile
import time
import zipfile

import maya.cmds as cmds

try:
    from importlib import reload
except ImportError:  # Python 2
    pass

try:
    from urllib.request import Request, urlopen
except ImportError:  # Python 2
    from urllib2 import Request, urlopen

REPO = 'RenderDeMartes/Mutant_Tools'
LATEST = 'https://api.github.com/repos/{}/releases/latest'.format(REPO)
HERE = os.path.dirname(os.path.abspath(__file__))
WINDOW = 'mutantWebToRigInstall'
CHUNK = 1024 * 512


def onMayaDroppedPythonFile(*args):
    # Maya imports a dropped file as a module and would hand this one back for
    # the next download dropped: forget it, so every drop reads its own folder
    sys.modules.pop(__name__, None)
    if web_to_rig_ready():
        open_web_to_rig()
    else:
        InstallWindow().show()


# ---------------------------------------------------------------------------

def scripts_dir():
    return cmds.internalVar(userScriptDir=True)


def install_dir():
    """Where Mutant Tools is, or goes: where this Maya imports it from, else
    the scripts folder its own easy_install.py uses."""
    try:
        import importlib.util
        spec = importlib.util.find_spec('Mutant_Tools')
        if spec and spec.submodule_search_locations:
            return list(spec.submodule_search_locations)[0]
    except Exception:
        pass
    return os.path.join(scripts_dir(), 'Mutant_Tools')


def web_to_rig_ready():
    return os.path.isfile(os.path.join(install_dir(), 'UI', 'WebToRig', 'load_web_to_rig.py'))


def forget_mutant_tools():
    """Drop the Mutant Tools modules imported before an install, so what runs
    next is the version just put in place."""
    for name in list(sys.modules):
        if name == 'Mutant_Tools' or name.startswith('Mutant_Tools.'):
            del sys.modules[name]
    try:
        import importlib
        importlib.invalidate_caches()
    except Exception:
        pass


def open_web_to_rig():
    if scripts_dir() not in sys.path:
        sys.path.append(scripts_dir())
    from Mutant_Tools.UI.WebToRig import load_web_to_rig
    reload(load_web_to_rig)
    load_web_to_rig.open_window(HERE)


def request(url):
    return urlopen(Request(url, headers={'User-Agent': 'Mutant-Tools-WebToRig'}), timeout=60)


# ---------------------------------------------------------------------------

class InstallWindow(object):
    """Stage 1: get Mutant Tools onto this Maya, with a progress bar for every
    part of it, then hand over to WebToRig."""

    def show(self):
        if cmds.window(WINDOW, exists=True):
            cmds.deleteUI(WINDOW)
        installed = os.path.isdir(install_dir())
        cmds.window(WINDOW, title='Mutant Tools - rig your character', widthHeight=(440, 236), sizeable=False)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnAttach=('both', 16))
        cmds.separator(style='none', height=8)
        cmds.text(label='Stage 1 of 4  -  Install Mutant Tools', font='boldLabelFont', align='left')
        cmds.text(align='left', wordWrap=True, label=(
            'Your Mutant Tools is too old for this workflow. The latest release will be installed '
            'over it; the old one is kept as a backup next to it.' if installed else
            'Mutant Tools is not installed in this Maya yet. The latest release will be downloaded '
            'from GitHub and installed in your scripts folder.'))
        self.bar = cmds.progressBar(maxValue=100, height=18)
        self.status = cmds.text(label='Ready.', align='left')
        self.button = cmds.button(label='Install Mutant Tools', height=36, command=lambda *a: self.install())
        cmds.separator(style='none', height=4)
        cmds.showWindow(WINDOW)

    def report(self, progress, text):
        cmds.progressBar(self.bar, edit=True, progress=int(progress))
        cmds.text(self.status, edit=True, label=text)
        cmds.refresh(force=True)

    def install(self):
        cmds.button(self.button, edit=True, enable=False)
        work = tempfile.mkdtemp(prefix='mutant_tools_')
        try:
            self.report(1, 'Asking GitHub for the latest release...')
            release = json.loads(request(LATEST).read().decode('utf-8'))
            assets = [a for a in release.get('assets', []) if a['name'].lower().endswith('.zip')]
            url = assets[0]['browser_download_url'] if assets else release['zipball_url']
            archive = os.path.join(work, 'Mutant_Tools.zip')
            self.download(url, archive, release.get('tag_name', 'latest'))
            source = self.extract(archive, os.path.join(work, 'unpacked'))
            self.put_in_place(source)
            self.finish_install()
            self.report(100, 'Mutant Tools {} is installed.'.format(release.get('tag_name', '')))
        except Exception as error:
            cmds.button(self.button, edit=True, enable=True, label='Try again')
            self.report(0, 'Install failed: {}'.format(error))
            cmds.confirmDialog(title='Mutant Tools - install failed', icon='critical', button=['OK'], message=(
                'The install did not finish:\n\n{}\n\nCheck your internet connection and try again, or install '
                'Mutant Tools by hand from github.com/{} (INSTALLATION_GUIDE.txt).'.format(error, REPO)))
            return
        finally:
            shutil.rmtree(work, ignore_errors=True)

        cmds.deleteUI(WINDOW)
        if web_to_rig_ready():
            open_web_to_rig()
        else:
            cmds.confirmDialog(title='Mutant Tools', button=['OK'], message=(
                'Mutant Tools is installed, but this release does not include the WebToRig tool yet.\n\n'
                'Drop Drag_into_Maya.py again once a newer release is out.'))

    def download(self, url, path, tag):
        response = request(url)
        total = int(response.headers.get('Content-Length') or 0)
        done = 0
        with open(path, 'wb') as out:
            while True:
                chunk = response.read(CHUNK)
                if not chunk:
                    break
                out.write(chunk)
                done += len(chunk)
                mb = done / 1048576.0
                if total:
                    self.report(2 + 63.0 * done / total, 'Downloading Mutant Tools {}: {:.0f} of {:.0f} MB'.format(
                        tag, mb, total / 1048576.0))
                else:
                    self.report(min(64, 2 + mb / 8.0), 'Downloading Mutant Tools {}: {:.0f} MB'.format(tag, mb))

    def extract(self, archive, target):
        with zipfile.ZipFile(archive) as zf:
            members = zf.infolist()
            for i, member in enumerate(members):
                zf.extract(member, target)
                if i % 40 == 0:
                    self.report(65 + 25.0 * i / len(members), 'Unpacking: {} of {} files'.format(i, len(members)))
        # the package is the folder holding UI/ and Utils/, wherever the zip put it
        for folder, dirs, files in os.walk(target):
            if 'UI' in dirs and 'Utils' in dirs:
                return folder
        raise RuntimeError('the download does not look like Mutant Tools')

    def put_in_place(self, source):
        self.report(91, 'Copying into your scripts folder...')
        target = install_dir()
        if os.path.isdir(target):
            backup = '{}_backup_{}'.format(target, time.strftime('%Y%m%d_%H%M%S'))
            os.rename(target, backup)
            print('Mutant Tools: the old install is kept in {}'.format(backup))
        shutil.copytree(source, target)

    def finish_install(self):
        """What easy_install.py does after copying: the shelf and the menu."""
        self.report(96, 'Adding the shelf and the Mutant-Tools menu...')
        shelf = os.path.join(install_dir(), 'shelf_Bluetape_Rigging.mel')
        shelves = cmds.internalVar(userShelfDir=True)
        if os.path.isfile(shelf) and os.path.isdir(shelves):
            try:
                shutil.copy(shelf, os.path.join(shelves, os.path.basename(shelf)))
            except Exception as error:
                print('Mutant Tools: could not install the shelf ({})'.format(error))
        if scripts_dir() not in sys.path:
            sys.path.append(scripts_dir())
        forget_mutant_tools()
        try:
            from Mutant_Tools.Utils import mt_menu
            mt_menu.create_mutant_menu()
            mt_menu.put_in_userSetup()
        except Exception as error:
            print('Mutant Tools: could not add the menu ({})'.format(error))
