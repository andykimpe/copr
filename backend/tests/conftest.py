"""
Fixtures for Copr Backend
"""

import os
from pytest import fixture
import shutil
import tarfile
import tempfile
import subprocess

class CoprTestFixtureContext():
    pass

@fixture
def f_temp_directory():
    "create and return temporary directory"
    directory = tempfile.mkdtemp(prefix="copr-backend-test-")
    ctx = CoprTestFixtureContext()
    ctx.workdir = directory
    yield ctx
    shutil.rmtree(directory)

@fixture
def f_testresults(f_temp_directory):
    "extract testresults.tar.gz into temporary directory"
    ctx = f_temp_directory
    src_path = os.path.join(os.path.dirname(__file__),
                            "_resources", "testresults.tar.gz")

    with tarfile.open(src_path, "r:gz") as tfile:
        tfile.extractall(ctx.workdir)
    ctx.testresults = os.path.join(ctx.workdir, 'testresults')
    yield ctx

@fixture
def f_empty_repos(f_testresults):
    """
    create empty john/empty/<chroots> directories, and run
    createrepo_c there
    """
    ctx = f_testresults
    ctx.empty_dir = os.path.join(ctx.workdir, 'john', 'empty')
    ctx.chroots = ['fedora-rawhide-x86_64', 'epel-7-x86_64']
    for chroot in ctx.chroots:
        chdir = os.path.join(ctx.empty_dir, chroot)
        os.makedirs(chdir)
        subprocess.check_output(['createrepo_c', chdir])
    yield ctx

@fixture
def f_first_build(f_empty_repos):
    """
    Simulate that first build finished, but no craterepo was run, yet.
    """
    ctx = f_empty_repos

    source = os.path.join(
        ctx.testresults,
        '@copr', 'prunerepo', 'fedora-23-x86_64', '00000041-prunerepo',
        'prunerepo-1.1-1.fc23.noarch.rpm',
    )

    build = '00000001-prunerepo'
    ctx.builds = [build]
    ctx.first_build = build

    for chroot in ctx.chroots:
        chdir = os.path.join(ctx.empty_dir, chroot, build)
        os.makedirs(chdir)
        shutil.copy(source, chdir)

    yield ctx

@fixture
def f_acr_on_and_first_build(f_first_build):
    """
    Simulate that we have ACR=1 and that first build finished, while
    no createrepo run after the build, yet.
    """
    ctx = f_first_build
    for chroot in ctx.chroots:
        chdir = os.path.join(ctx.empty_dir, chroot, 'devel')
        os.mkdir(chdir)
        subprocess.check_output(['createrepo_c', chdir])
    yield ctx

@fixture
def f_second_build(f_first_build):
    """
    Simulate that second build finished right after the first one,
    and no create repo was run yet.
    """
    ctx = f_first_build
    source = os.path.join(ctx.workdir, '@copr', 'prunerepo', 'fedora-23-x86_64',
                          '00000049-example', 'example-1.0.4-1.fc23.x86_64.rpm')
    source = os.path.join(ctx.testresults, '@copr', 'prunerepo',
                          'fedora-23-x86_64', '00000049-example',
                          'example-1.0.4-1.fc23.x86_64.rpm')
    ctx.build = '00000002-example'
    ctx.builds.append(ctx.build)
    for chroot in ctx.chroots:
        chdir = os.path.join(ctx.empty_dir, chroot, ctx.build)
        os.mkdir(chdir)
        shutil.copy(source, chdir)

    yield ctx
