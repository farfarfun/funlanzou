"""funlanzou.api.models 容器类测试：正常路径 + 空列表/未命中的边界。"""

from collections import namedtuple

from funlanzou.api.models import FileList, FolderList

Item = namedtuple("Item", ["name", "id"])


def make_list(*items):
    lst = FileList()
    for item in items:
        lst.append(item)
    return lst


def test_append_and_len():
    lst = make_list(Item("a.txt", 1), Item("b.txt", 2))
    assert len(lst) == 2
    assert lst[0].name == "a.txt"


def test_iteration_order_preserved():
    lst = make_list(Item("a", 1), Item("b", 2), Item("c", 3))
    assert [it.name for it in lst] == ["a", "b", "c"]


def test_name_id_property():
    lst = make_list(Item("a", 1), Item("b", 2))
    assert lst.name_id == {"a": 1, "b": 2}


def test_all_name_property():
    lst = make_list(Item("a", 1), Item("b", 2))
    assert lst.all_name == ["a", "b"]


def test_find_by_name_hit_and_miss():
    lst = make_list(Item("a", 1))
    assert lst.find_by_name("a").id == 1
    assert lst.find_by_name("missing") is None


def test_find_by_id_hit_and_miss():
    lst = make_list(Item("a", 1))
    assert lst.find_by_id(1).name == "a"
    assert lst.find_by_id(999) is None


def test_pop_by_id_removes_item_and_returns_it():
    lst = make_list(Item("a", 1), Item("b", 2))
    popped = lst.pop_by_id(1)
    assert popped.name == "a"
    assert len(lst) == 1
    assert lst.find_by_id(1) is None


def test_pop_by_id_miss_returns_none_and_keeps_list():
    lst = make_list(Item("a", 1))
    assert lst.pop_by_id(999) is None
    assert len(lst) == 1


def test_update_by_id_replaces_namedtuple_fields():
    lst = make_list(Item("a", 1))
    lst.update_by_id(1, name="renamed")
    assert lst.find_by_id(1).name == "renamed"


def test_filter_returns_matching_items_as_plain_list():
    lst = make_list(Item("a", 1), Item("b", 2), Item("c", 3))
    result = lst.filter(lambda it: it.id > 1)
    assert isinstance(result, list)
    assert [it.name for it in result] == ["b", "c"]


def test_empty_list_operations():
    lst = FolderList()
    assert len(lst) == 0
    assert list(lst) == []
    assert lst.find_by_id(1) is None
    assert lst.find_by_name("x") is None
    assert lst.pop_by_id(1) is None
    assert lst.all_name == []
    assert lst.name_id == {}


def test_clear_empties_list():
    lst = make_list(Item("a", 1), Item("b", 2))
    lst.clear()
    assert len(lst) == 0


def test_lt_compares_by_joined_name_path():
    a = make_list(Item("a", 1))
    b = make_list(Item("b", 1))
    assert a < b


def test_repr_contains_item_reprs():
    lst = make_list(Item("a", 1))
    assert "List" in repr(lst)
