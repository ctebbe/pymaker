# This file is part of Maker Keeper Framework.
#
# Copyright (C) 2017 reverendus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time

import pytest
from mock import MagicMock
from web3 import EthereumTesterProvider, Web3

import pymaker
from pymaker import Address
from pymaker.lifecycle import Web3Lifecycle


class TestLifecycle:
    def setup_method(self):
        self.web3 = Web3(EthereumTesterProvider())
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        self.our_address = Address(self.web3.eth.defaultAccount)

        # `test_etherdelta.py` executes before this test file and creates some event filters,
        # so we need to clear the list of filter threads as otherwise `Web3Lifecycle` will
        # be waiting forever for them to terminate and the test harness will never finish
        pymaker.filter_threads = []

    def test_should_always_exit(self):
        with pytest.raises(SystemExit):
            with Web3Lifecycle(self.web3):
                pass

    def test_should_start_instantly_if_no_initial_delay(self):
        # given
        start_time = int(time.time())

        # when
        with pytest.raises(SystemExit):
            with Web3Lifecycle(self.web3) as lifecycle:
                pass

        # then
        end_time = int(time.time())
        assert end_time - start_time <= 2

    def test_should_obey_initial_delay(self):
        # given
        start_time = int(time.time())

        # when
        with pytest.raises(SystemExit):
            with Web3Lifecycle(self.web3) as lifecycle:
                lifecycle.initial_delay(5)

        # then
        end_time = int(time.time())
        assert end_time - start_time >= 4

    def test_should_call_startup_callback(self):
        # given
        startup_mock = MagicMock()

        # when
        with pytest.raises(SystemExit):
            with Web3Lifecycle(self.web3) as lifecycle:
                lifecycle.on_startup(startup_mock)

        # then
        startup_mock.assert_called()

    def test_should_fail_to_register_two_startup_callbacks(self):
        # expect
        with pytest.raises(BaseException):
            with Web3Lifecycle(self.web3) as lifecycle:
                lifecycle.on_startup(lambda: 1)
                lifecycle.on_startup(lambda: 2)

    def test_should_call_shutdown_callback(self):
        # given
        ordering = []
        startup_mock = MagicMock(side_effect=lambda: ordering.append('STARTUP'))
        shutdown_mock = MagicMock(side_effect=lambda: ordering.append('SHUTDOWN'))

        # when
        with pytest.raises(SystemExit):
            with Web3Lifecycle(self.web3) as lifecycle:
                lifecycle.on_startup(startup_mock)
                lifecycle.on_shutdown(shutdown_mock)

        # then
        assert ordering == ['STARTUP', 'SHUTDOWN']

    def test_should_fail_to_register_two_shutdown_callbacks(self):
        # expect
        with pytest.raises(BaseException):
            with Web3Lifecycle(self.web3) as lifecycle:
                lifecycle.on_shutdown(lambda: 1)
                lifecycle.on_shutdown(lambda: 2)

    def test_should_fail_to_register_two_block_callbacks(self):
        # expect
        with pytest.raises(BaseException):
            with Web3Lifecycle(self.web3) as lifecycle:
                lifecycle.on_block(lambda: 1)
                lifecycle.on_block(lambda: 2)

    def test_every(self):
        self.counter = 0

        def callback():
            self.counter = self.counter + 1
            if self.counter >= 2:
                lifecycle.terminate("Unit test is over")

        # given
        mock = MagicMock(side_effect=callback)

        # when
        with pytest.raises(SystemExit):
            with Web3Lifecycle(self.web3) as lifecycle:
                lifecycle.every(1, mock)

        # then
        assert mock.call_count >= 2
        assert lifecycle.terminated_internally

    def test_every_does_not_start_operating_until_startup_callback_is_finished(self):
        # given
        self.every_triggered = False

        def startup_callback():
            time.sleep(3)
            assert not self.every_triggered

        def every_callback():
            self.every_triggered = True
            lifecycle.terminate("Unit test is over")

        # when
        with pytest.raises(SystemExit):
            with Web3Lifecycle(self.web3) as lifecycle:
                lifecycle.on_startup(startup_callback)
                lifecycle.every(1, every_callback)

        # then
        assert self.every_triggered

    def test_every_should_not_fire_when_keeper_is_already_terminating(self):
        # given
        self.every_counter = 0

        def shutdown_callback():
            time.sleep(5)

        def every_callback():
            self.every_counter = self.every_counter + 1
            lifecycle.terminate("Unit test is over")

        # when
        with pytest.raises(SystemExit):
            with Web3Lifecycle(self.web3) as lifecycle:
                lifecycle.every(1, every_callback)
                lifecycle.on_shutdown(shutdown_callback)

        # then
        assert self.every_counter <= 2

    def test_should_not_call_shutdown_until_every_timer_has_finished(self):
        # given
        self.every1_finished = False
        self.every2_finished = False

        def shutdown_callback():
            assert self.every1_finished
            assert self.every2_finished

        def every_callback_1():
            time.sleep(1)
            lifecycle.terminate("Unit test is over")
            time.sleep(4)
            self.every1_finished = True

        def every_callback_2():
            time.sleep(2)
            self.every2_finished = True

        # expect
        with pytest.raises(SystemExit):
            with Web3Lifecycle(self.web3) as lifecycle:
                lifecycle.every(1, every_callback_1)
                lifecycle.every(1, every_callback_2)
                lifecycle.on_shutdown(shutdown_callback)  # assertions are in `shutdown_callback`
