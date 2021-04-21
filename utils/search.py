"""Search related utilities"""

from typing import Union, List, Tuple


def binary_search(search_parameter, sorted_list: Union[List, Tuple]) -> bool:
    """Perform binary search for search parameter in sorted list"""
    low, high = 0, len(sorted_list) - 1
    while low < high:
        mid = (low + (high - low)) // 2
        middle_value = sorted_list[mid]
        if search_parameter in (
                sorted_list[low], middle_value, sorted_list[high]
        ):
            return True
        else:
            if search_parameter < middle_value:
                high = mid - 1
            else:
                low = mid + 1
    return False
