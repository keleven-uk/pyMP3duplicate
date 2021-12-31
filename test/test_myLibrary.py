###############################################################################################################
#    test_myLibrary.py.py   Copyright (C) <2020-2021>  <Kevin Scott>                                          #                                                                                                             #                                                                                                             #
#    test for functions in myLibrary.pys.py                                                                   #
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
import src.Library as Library
import src.Exceptions as Exceptions


@pytest.fixture
def db_library(tmp_path):
    """  Set up the pickle database.  """
    db = tmp_path / "testLibrary.pickle"
    return Library.Library(db, "pickle")

@pytest.fixture
def ja_library(tmp_path):
    """  Set up the jason database.  """
    db = tmp_path / "testLibrary.jason"
    return Library.Library(db, "jason")

#-----------------------------------------------------------------  test add to library ------------------------
def test_library_pickle_add(db_library):
    db_library.addItem("one", "data1", "data2", "date3")
    assert db_library.noOfItems == 1

def test_library_jason_add(ja_library):
    ja_library.addItem("one", "data1", "data2", "date3")
    assert ja_library.noOfItems == 1

#---------------------------------------------------------------  test library get --------------------------
def test_library_pickle_get(db_library):
    db_library.addItem("one", "data1", "data2", "data3")
    r1, r2, r3 = db_library.getItem("one")
    assert r1 == "data1"
    assert r2 == "data2"
    assert r3 == "data3"

def test_library_pickle_get_fail(db_library):
    db_library.addItem("one", "data1", "data2", "data3")
    with pytest.raises(Exceptions.LibraryError) as execInfo:
        r1, r2, r3 = db_library.getItem("two")
    assert str(execInfo.value) == "LibraryError has been raised"

def test_library_jason_get(ja_library):
    ja_library.addItem("one", "data1", "data2", "data3")
    r1, r2, r3 = ja_library.getItem("one")
    assert r1 == "data1"
    assert r2 == "data2"
    assert r3 == "data3"

def test_library_jason_get_fail(ja_library):
    ja_library.addItem("one", "data1", "data2", "data3")
    with pytest.raises(Exceptions.LibraryError) as execInfo:
        r1, r2, r3 = ja_library.getItem("two")
    assert str(execInfo.value) == "LibraryError has been raised"

#-----------------------------------------------------------------  test library has --------------------------
def test_library_pickle_has(db_library):
    db_library.addItem("one", "data1", "data2", "data3")
    assert db_library.hasKey("one") == True

def test_library_pickle_has_fail(db_library):
    db_library.addItem("one", "data1", "data2", "data3")
    assert db_library.hasKey("two") == False

def test_library_jason_has(db_library):
    db_library.addItem("one", "data1", "data2", "data3")
    assert db_library.hasKey("one") == True

def test_library_jason_has_fail(db_library):
    db_library.addItem("one", "data1", "data2", "data3")
    assert db_library.hasKey("two") == False

#-----------------------------------------------------------------  test delete from library -------------------

def test_library_pickle_del(db_library):
    db_library.addItem("one", "data1", "data2", "data3")
    db_library.addItem("two", "data1", "data2", "data3")
    assert db_library.noOfItems == 2
    db_library.delItem("one")
    assert db_library.noOfItems == 1

def test_library_pickle_del_fail(db_library):
    db_library.addItem("one", "data1", "data2", "data3")
    with pytest.raises(Exceptions.LibraryError) as execInfo:
        db_library.delItem("two")
    assert str(execInfo.value) == "LibraryError has been raised"

def test_library_jason_del(db_library):
    db_library.addItem("one", "data1", "data2", "data3")
    db_library.addItem("two", "data1", "data2", "data3")
    assert db_library.noOfItems == 2
    db_library.delItem("one")
    assert db_library.noOfItems == 1

def test_library_jason_del_fail(db_library):
    db_library.addItem("one", "data1", "data2", "data3")
    with pytest.raises(Exceptions.LibraryError) as execInfo:
        db_library.delItem("two")
    assert str(execInfo.value) == "LibraryError has been raised"

#-----------------------------------------------------------------  test save/load of a pickle library ---------
def test_library_pickle(db_library):
    db_library.addItem("one", "data1", "data2", "data3")
    db_library.addItem("two", "data1", "data2", "data3")
    db_library.addItem("three", "data1", "data2", "data3")
    db_library.addItem("four", "data1", "data2", "data3")
    db_library.addItem("five", "data1", "data2", "data3")

    db_library.save()
    db_library.clear()
    db_library.load()

    assert db_library.noOfItems == 5

    r1, r2, r3 = db_library.getItem("one")
    assert r1 == "data1"
    assert r2 == "data2"
    assert r3 == "data3"


#-----------------------------------------------------------------  test save/load of a jason library ---------
def test_library_jason(ja_library):
    ja_library.addItem("one", "data1", "data2", "data3")
    ja_library.addItem("two", "data1", "data2", "data3")
    ja_library.addItem("three", "data1", "data2", "data3")
    ja_library.addItem("four", "data1", "data2", "data3")
    ja_library.addItem("five", "data1", "data2", "data3")

    ja_library.save()
    ja_library.clear()
    ja_library.load()

    assert ja_library.noOfItems == 5

    r1, r2, r3 = ja_library.getItem("one")
    assert r1 == "data1"
    assert r2 == "data2"
    assert r3 == "data3"
