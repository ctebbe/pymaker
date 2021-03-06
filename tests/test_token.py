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

import pytest
from pymaker import Address
from pymaker.numeric import Wad
from pymaker.util import synchronize
from web3 import EthereumTesterProvider
from web3 import Web3

from pymaker.token import DSToken, DSEthToken, ERC20Token


class TestERC20Token:
    def setup_method(self):
        self.web3 = Web3(EthereumTesterProvider())
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        self.our_address = Address(self.web3.eth.defaultAccount)
        self.second_address = Address(self.web3.eth.accounts[1])
        self.token = DSToken.deploy(self.web3, 'ABC')
        self.token.mint(Wad(1000000)).transact()

    def test_fail_when_no_token_with_that_address(self):
        with pytest.raises(Exception):
            ERC20Token(web3=self.web3, address=Address('0x0123456789012345678901234567890123456789'))

    def test_total_supply(self):
        assert self.token.total_supply() == Wad(1000000)

    def test_balance_of(self):
        assert self.token.balance_of(self.our_address) == Wad(1000000)
        assert self.token.balance_of(self.second_address) == Wad(0)

    def test_transfer(self):
        # when
        receipt = self.token.transfer(self.second_address, Wad(500)).transact()

        # then
        assert receipt is not None
        assert self.token.balance_of(self.our_address) == Wad(999500)
        assert self.token.balance_of(self.second_address) == Wad(500)

    def test_transfer_async(self):
        # when
        receipt = synchronize([self.token.transfer(self.second_address, Wad(750)).transact_async()])

        # then
        assert receipt is not None
        assert self.token.balance_of(self.our_address) == Wad(999250)
        assert self.token.balance_of(self.second_address) == Wad(750)

    def test_transfer_failed(self):
        # when
        receipt = self.token.transfer(self.second_address, Wad(5000000)).transact()

        # then
        assert receipt is None
        assert self.token.balance_of(self.our_address) == Wad(1000000)
        assert self.token.balance_of(self.second_address) == Wad(0)

    def test_transfer_failed_async(self):
        # when
        receipt = synchronize([self.token.transfer(self.second_address, Wad(5000000)).transact_async()])[0]

        # then
        assert receipt is None
        assert self.token.balance_of(self.our_address) == Wad(1000000)
        assert self.token.balance_of(self.second_address) == Wad(0)

    def test_transfer_out_of_gas(self):
        # when
        with pytest.raises(Exception):
            self.token.transfer(self.second_address, Wad(500)).transact(gas=26000)

        # then
        assert self.token.balance_of(self.our_address) == Wad(1000000)
        assert self.token.balance_of(self.second_address) == Wad(0)

    def test_transfer_out_of_gas_async(self):
        # when
        with pytest.raises(Exception):
            synchronize([self.token.transfer(self.second_address, Wad(500)).transact_async(gas=26000)])[0]

        # then
        assert self.token.balance_of(self.our_address) == Wad(1000000)
        assert self.token.balance_of(self.second_address) == Wad(0)

    def test_allowance_of(self):
        assert self.token.allowance_of(self.our_address, self.second_address) == Wad(0)

    def test_approve(self):
        # when
        self.token.approve(self.second_address, Wad(2000)).transact()

        # then
        assert self.token.allowance_of(self.our_address, self.second_address) == Wad(2000)

    def test_equals(self):
        # given
        token1 = DSToken.deploy(self.web3, 'ABC')
        token2 = DSToken.deploy(self.web3, 'DEF')
        token2b = ERC20Token(web3=self.web3, address=token2.address)

        # expect
        assert token1 == token1
        assert token2 == token2b
        assert not token1 == token2
        assert not token1 == token2b

    def test_should_have_printable_representation(self):
        erc20token = ERC20Token(web3=self.web3, address=self.token.address)
        assert repr(erc20token) == f"ERC20Token('{erc20token.address}')"


class TestDSToken:
    def setup_method(self):
        self.web3 = Web3(EthereumTesterProvider())
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        self.our_address = Address(self.web3.eth.defaultAccount)
        self.dstoken = DSToken.deploy(self.web3, 'ABC')

    def test_fail_when_no_contract_under_that_address(self):
        # expect
        with pytest.raises(Exception):
            DSToken(web3=self.web3, address=Address('0xdeadadd1e5500000000000000000000000000000'))

    def test_authority(self):
        # given
        some_address = Address('0x4545454545676767676789898989890101010101')

        # when
        self.dstoken.set_authority(some_address).transact()

        # then
        assert self.dstoken.authority() == some_address

    def test_mint(self):
        # when
        self.dstoken.mint(Wad(100000)).transact()

        # then
        assert self.dstoken.balance_of(self.our_address) == Wad(100000)

    def test_burn(self):
        # given
        self.dstoken.mint(Wad(100000)).transact()

        # when
        self.dstoken.burn(Wad(40000)).transact()

        # then
        assert self.dstoken.balance_of(self.our_address) == Wad(60000)

    def test_should_have_printable_representation(self):
        assert repr(self.dstoken) == f"DSToken('{self.dstoken.address}')"


class TestDSEthToken:
    def setup_method(self):
        self.web3 = Web3(EthereumTesterProvider())
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        self.our_address = Address(self.web3.eth.defaultAccount)
        self.dsethtoken = DSEthToken.deploy(self.web3)

    def test_fail_when_no_contract_under_that_address(self):
        # expect
        with pytest.raises(Exception):
            DSEthToken(web3=self.web3, address=Address('0xdeadadd1e5500000000000000000000000000000'))

    def test_deposit(self):
        # when
        self.dsethtoken.deposit(Wad(100000)).transact()

        # then
        assert self.dsethtoken.balance_of(self.our_address) == Wad(100000)

    def test_withdraw(self):
        # given
        self.dsethtoken.deposit(Wad(100000)).transact()

        # when
        self.dsethtoken.withdraw(Wad(40000)).transact()

        # then
        assert self.dsethtoken.balance_of(self.our_address) == Wad(60000)

    def test_should_have_printable_representation(self):
        assert repr(self.dsethtoken) == f"DSEthToken('{self.dsethtoken.address}')"
