# Copyright 2017  Lars Wirzenius
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# =*= License: GPL-3+ =*=



import os

import cliapp

import vmdb


class AptPlugin(cliapp.Plugin):

    def enable(self):
        self.app.step_runners.add(AptStepRunner())


class AptStepRunner(vmdb.StepRunnerInterface):

    def get_required_keys(self):
        return ['apt', 'fs-tag', 'packages']

    def run(self, step, settings, state):
        operation = step['apt']
        if operation != 'install':
            raise Exception('"apt" must always have value "install"')

        packages = step['packages']
        fstag = step['fs-tag']
        mount_point = state.mounts[fstag]
        opts = step.get('options', '').split()

        if not self.got_eatmydata(state):
            self.install_packages(mount_point, [], [], ['eatmydata'])
            state.got_eatmydata = True
        self.install_packages(mount_point, ['eatmydata'], opts, packages)

    def got_eatmydata(self, state):
        return hasattr(state, 'got_eatmydata') and getattr(state, 'got_eatmydata')

    def install_packages(self, mount_point, argv_prefix, opts, packages):
        env = os.environ.copy()
        env['DEBIAN_FRONTEND'] = 'noninteractive'

        vmdb.runcmd_chroot(
            mount_point,
            argv_prefix +
            ['apt-get', '-y', '--no-show-progress'] + opts + ['install'] + packages,
            env=env)
