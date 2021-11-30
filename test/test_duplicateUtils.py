###############################################################################################################
#    test_duplicateUtils.py   Copyright (C) <2020-2021>  <Kevin Scott>                                        #                                                                                                             #                                                                                                             #
#    test for helper and utility functions in duplicateUtils.py                                               #
#                                                                                                             #
###############################################################################################################
#    Copyright (C) <2020-2021>  <Kevin Scott>                                                                 #
#                                                                                                             #
#    This program is free software: you can redistribute it and/or modify it under the terms of the           #
#    GNU General Public License as published by the Free Software Foundation, either Version 3 of the         #
#    License, or (at your option) any later Version.                                                          #
#                                                                                                             #
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without        #
#    even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
#    GNU General Public License for more details.                                                             #
#                                                                                                             #
#    You should have received a copy of the GNU General Public License along with this program.               #
#    If not, see <http://www.gnu.org/licenses/>.                                                              #
#                                                                                                             #
###############################################################################################################

import pytest
import src.utils.duplicateUtils as duplicateUtils


@pytest.mark.parametrize("test_input, expected_output", [ ("The Shadows", "Shadows"), ("Shadows", "Shadows"), ("", "") ] )
def test_removeThe(test_input, expected_output):
    assert duplicateUtils.removeThe(test_input) == expected_output

@pytest.mark.parametrize("test_input, expected_output", [ ("Shadows, the", True), ("Shadows, The", True), ("The Shadows", False), ("Ken Boothe", False), ("", "") ] )
def test_trailingThe(test_input, expected_output):
    assert duplicateUtils.trailingThe(test_input) == expected_output
