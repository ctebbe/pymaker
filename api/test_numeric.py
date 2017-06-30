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

from api.numeric import Wad, Ray


class TestWad:
    def test_should_compare_wads_with_each_other(self):
        assert Wad(1000) == Wad(1000)
        assert Wad(1000) != Wad(999)
        assert Wad(1000) > Wad(999)
        assert Wad(999) < Wad(1000)
        assert Wad(999) <= Wad(1000)
        assert Wad(1000) <= Wad(1000)
        assert Wad(1000) >= Wad(1000)
        assert Wad(1000) >= Wad(999)

    def test_should_reject_comparison_with_rays(self):
        with pytest.raises(ArithmeticError):
            assert Wad(1000) == Ray(1000)
        with pytest.raises(ArithmeticError):
            assert Wad(1000) != Ray(999)
        with pytest.raises(ArithmeticError):
            assert Wad(1000) > Ray(999)
        with pytest.raises(ArithmeticError):
            assert Wad(999) < Ray(1000)
        with pytest.raises(ArithmeticError):
            assert Wad(999) <= Ray(1000)
        with pytest.raises(ArithmeticError):
            assert Wad(1000) <= Ray(1000)
        with pytest.raises(ArithmeticError):
            assert Wad(1000) >= Ray(1000)
        with pytest.raises(ArithmeticError):
            assert Wad(1000) >= Ray(999)

    def test_should_reject_comparison_with_ints(self):
        with pytest.raises(ArithmeticError):
            assert Wad(1000) == 100
        with pytest.raises(ArithmeticError):
            assert Wad(1000) != 999
        with pytest.raises(ArithmeticError):
            assert Wad(1000) > 999
        with pytest.raises(ArithmeticError):
            assert Wad(999) < 1000
        with pytest.raises(ArithmeticError):
            assert Wad(999) <= 1000
        with pytest.raises(ArithmeticError):
            assert Wad(1000) <= 1000
        with pytest.raises(ArithmeticError):
            assert Wad(1000) >= 1000
        with pytest.raises(ArithmeticError):
            assert Wad(1000) >= 999

    def test_min_value(self):
        assert Wad.min(Wad(10), Wad(20)) == Wad(10)
        assert Wad.min(Wad(25), Wad(15)) == Wad(15)
        assert Wad.min(Wad(25), Wad(15), Wad(5)) == Wad(5)

    def test_min_value_should_reject_comparison_with_rays(self):
        with pytest.raises(ArithmeticError):
            Wad.min(Wad(10), Ray(20))
        with pytest.raises(ArithmeticError):
            Wad.min(Ray(25), Wad(15))

    def test_min_value_should_reject_comparison_with_ints(self):
        with pytest.raises(ArithmeticError):
            Wad.min(Wad(10), 20)
        with pytest.raises(ArithmeticError):
            Wad.min(20, Wad(10))

    def test_max_value(self):
        assert Wad.max(Wad(10), Wad(20)) == Wad(20)
        assert Wad.max(Wad(25), Wad(15)) == Wad(25)
        assert Wad.max(Wad(25), Wad(15), Wad(40)) == Wad(40)

    def test_max_value_should_reject_comparison_with_rays(self):
        with pytest.raises(ArithmeticError):
            Wad.max(Wad(10), Ray(20))
        with pytest.raises(ArithmeticError):
            Wad.max(Wad(25), Ray(15))

    def test_max_value_should_reject_comparison_with_ints(self):
        with pytest.raises(ArithmeticError):
            Wad.max(Wad(10), 20)
        with pytest.raises(ArithmeticError):
            Wad.max(15, Wad(25))
