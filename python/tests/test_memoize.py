from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from ..memoize import JsonCache, memoize


# Test the memoize() function
class TestMemoize:
    def test_cache_calls(self, mocker: MockerFixture, tmp_path: Path):
        """
        Verify that the JsonCache methods are called
        """

        loadSpy = mocker.spy(JsonCache, 'load')
        dumpSpy = mocker.spy(JsonCache, 'dump')
        cache_file = tmp_path / 'cache.json'

        # Call memoized function
        def fn(self, a, b=None):
            return [a,b]
        wrapped = memoize(cache_file)(fn)
        wrapped(self, 1, b=2)
        
        # Check cache
        loadSpy.assert_called_once()

        key = str([1] + [('b', 2)])
        value = [1,2]
        dumpSpy.assert_called_once_with(mocker.ANY, {key:value})

    def test_cache(self, mocker: MockerFixture, tmp_path: Path):
        loadSpy = mocker.spy(JsonCache, 'load')
        dumpSpy = mocker.spy(JsonCache, 'dump')
        cache_file = tmp_path / 'cache.json'

        fn = mocker.Mock(return_value=0)
        wrapped = memoize(cache_file)(fn)

        # Call multiple times
        wrapped(self, 1)
        wrapped(self, 2)
        wrapped(self, 1)
        
        # Check that one of the calls was cached
        assert fn.call_count == 2
        assert loadSpy.call_count == 3
        assert dumpSpy.call_count == 2

    def test_return_value(self, tmp_path: Path):
        cache_file = tmp_path / 'cache.json'

        # Create memoized function
        def fn(self, b, a=1, c=None):
            return [a,b,c]
        wrapped = memoize(cache_file)(fn)

        # Call it
        result = wrapped(self, 2, c=3)

        assert result == [1,2,3]

    def test_kwargs_sort(self, mocker: MockerFixture, tmp_path: Path):
        dumpSpy = mocker.spy(JsonCache, 'dump')
        cache_file = tmp_path / 'cache.json'

        # Call memoized function
        def fn(self, b=0, c=0, a=0):
            return [a, b, c]
        wrapped = memoize(cache_file)(fn)
        wrapped(self, c=3, a=1, b=2)

        # Check that kwargs were sorted
        key = str([
            ('a', 1),
            ('b', 2),
            ('c', 3)
        ])
        dumpSpy.assert_called_once_with(mocker.ANY, {key: mocker.ANY})

