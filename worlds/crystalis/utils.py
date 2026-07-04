# Python Imports
from typing import TYPE_CHECKING

# Archipelago Imports
from BaseClasses import CollectionState

if TYPE_CHECKING:
    from . import CrystalisWorld


ITEMS_TO_TEST: list[str] = [
]


def visualize_regions(world: "CrystalisWorld", out_filepath: str):
    test_state: CollectionState = CollectionState(world.multiworld)
    for item in world.multiworld.itempool:
        if item.player == world.player and item.name in ITEMS_TO_TEST:
            test_state.collect(item, True)
    # test_state.sweep_for_advancements()
    from Utils import visualize_regions
    visualize_regions(world.get_region("Menu"), out_filepath)#, regions_to_highlight=test_state.reachable_regions[1])
