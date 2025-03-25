from BaseClasses import CollectionState
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .__init__ import CrystalisWorld


ITEMS_TO_TEST: list[str] = [
    "Sword of Wind",
    "Sword of Fire",
    "Sword of Water",
    "Sword of Thunder",
    "Bow of Sun",
    "Bow of Moon",
    "Bow of Truth",
    "Flight"
]


def visualize_regions(world: "CrystalisWorld", out_filepath: str):
    test_state: CollectionState = CollectionState(world.multiworld)
    for item in world.multiworld.itempool:
        if item.player == world.player and item.name in ITEMS_TO_TEST:
            test_state.collect(item, True)
    test_state.sweep_for_advancements()
    from Utils import visualize_regions
    visualize_regions(world.get_region("Menu"), out_filepath, regions_to_highlight=test_state.reachable_regions[1])
