# Return the git revision as a string (local git information)
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

from app.config import settings


def git_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH', 'HOME']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out_env = subprocess.check_output(cmd, stderr=subprocess.STDOUT, env=env)
        return out_env

    try:
        git_revision = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        GIT_REVISION = git_revision.strip().decode('ascii')
        git_short_revision = _minimal_ext_cmd(['git', 'rev-parse', '--short', 'HEAD'])
        GIT_SHORT_REVISION = git_short_revision.strip().decode('ascii')
        git_branch = _minimal_ext_cmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        GIT_BRANCH = git_branch.strip().decode('ascii')
    except (subprocess.SubprocessError, OSError):
        GIT_REVISION, GIT_SHORT_REVISION, GIT_BRANCH = "Unknown", "Unknown", "Unknown"

    if not GIT_REVISION or not GIT_BRANCH:
        # this shouldn't happen but apparently can (see gh-8512)
        GIT_REVISION, GIT_SHORT_REVISION, GIT_BRANCH = "Unknown", "Unknown", "Unknown"

    return GIT_REVISION, GIT_SHORT_REVISION, GIT_BRANCH


def get_current_datetime(format: str = '%Y-%m-%d %H:%M:%S'):
    return datetime.now().strftime(format)


def make_version_info():
    # Adding the git rev number needs to be done inside write_version_py(),
    # otherwise the import of numpy.version messes up the build under Python 3.
    work_dir = Path.cwd()
    ISRELEASED = False
    FULLVERSION = settings.MAJOR_VERSION
    if Path(work_dir).joinpath('.git').exists():  # HOME/.git directory
        GIT_REVISION, GIT_SHORT_REVISION, GIT_BRANCH = git_version()
    else:
        GIT_REVISION, GIT_SHORT_REVISION, GIT_BRANCH = "Unknown", "Unknown", "Unknown"

    if not ISRELEASED:
        version_date = get_current_datetime('%y%m.%d')
        FULLVERSION = f'{FULLVERSION}.{version_date}-{settings.STATUS}-{GIT_SHORT_REVISION}'

    BUILD_DATE = get_current_datetime()
    SERVICE = settings.SERVICE_NAME

    return SERVICE, FULLVERSION, GIT_REVISION, GIT_SHORT_REVISION, GIT_BRANCH, BUILD_DATE


def write_version_py(file_name='version_info.py'):
    version_info = """\
service: str = '{service}'
version: str = '{version}'
git_branch: str = '{git_branch}'
git_revision: str = '{git_revision}'
git_short_revision: str = '{git_short_revision}'
build_date: str = '{build_date}'
"""

    SERVICE, FULL_VERSION, GIT_REVISION, GIT_SHORT_REVISION, GIT_BRANCH, BUILD_DATE = make_version_info()
    if GIT_BRANCH.lower() == 'unknown' or GIT_REVISION.lower() == 'unknown' or GIT_SHORT_REVISION.lower() == 'unknown':
        logging.warning("Unable to get git version information. Set to 'Unknown'")
    else:
        logging.info("Complete writing version, git info, build date on 'version_info.py'. Check it.")
    version_info_path = Path(file_name).open(mode='w')
    version_info_path.write(version_info.format(
        service=SERVICE,
        version=FULL_VERSION,
        git_branch=GIT_BRANCH,
        git_revision=GIT_REVISION,
        git_short_revision=GIT_SHORT_REVISION,
        build_date=BUILD_DATE,
    ))


def get_version_info():
    BUILD_DATE = get_current_datetime()
    FULL_VERSION, GIT_REVISION, GIT_SHORT_REVISION, GIT_BRANCH = "Unknown", "Unknown", "Unknown", "Unknown"

    try:
        import version_info  # type: ignore
    except ImportError as ie:
        logging.error(f"{ie}: Check if 'app.version_info' exists.")
        return FULL_VERSION, GIT_REVISION, GIT_SHORT_REVISION, GIT_BRANCH, BUILD_DATE

    if hasattr(version_info, 'version'):
        FULL_VERSION = version_info.version
    if hasattr(version_info, 'git_branch'):
        GIT_BRANCH = version_info.git_branch
    if hasattr(version_info, 'git_revision'):
        GIT_REVISION = version_info.git_revision
    if hasattr(version_info, 'git_short_revision'):
        GIT_SHORT_REVISION = version_info.git_short_revision
    if hasattr(version_info, 'build_date'):
        BUILD_DATE = version_info.build_date

    return FULL_VERSION, GIT_REVISION, GIT_SHORT_REVISION, GIT_BRANCH, BUILD_DATE


VERSION, GIT_REVISION, GIT_SHORT_REVISION, GIT_BRANCH, BUILD_DATE = get_version_info()

if __name__ == "__main__":
    write_version_py(file_name='version_info.py')
