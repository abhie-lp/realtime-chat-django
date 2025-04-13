"""Search related utilities"""

import bisect
from collections.abc import Sequence


def binary_search(search_parameter, sorted_list: Sequence) -> bool:
    """Perform binary search for search parameter in sorted list"""
    idx = bisect.bisect_left(sorted_list, search_parameter)
    return idx < len(sorted_list) and sorted_list[idx] == search_parameter