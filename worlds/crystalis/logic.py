import logging

from BaseClasses import MultiWorld, CollectionState, Entrance
from .options import CrystalisOptions
from .types import CrystalisShuffleData
from typing import Callable
from worlds.generic.Rules import set_rule, add_rule

def has_level_1_sword(state: CollectionState, player: int, element: str) -> bool:
    return state.has("Sword of " + element, player, 1)


def has_level_2_sword(state: CollectionState, player: int, element: str) -> bool:
    return state.has("Sword of " + element, player, 1) and \
           state.has_group(element + " Upgrades", player, 1)


def has_level_3_sword(state: CollectionState, player: int, element: str) -> bool:
    return state.has_group(element, player, 3)


def set_two_way_logic(forward_entrance: Entrance) -> None:
    for entrance in forward_entrance.connected_region.exits:
        if entrance.connected_region == forward_entrance.parent_region:
            #set or add for this func? dunno, setting for now
            entrance.access_rule = forward_entrance.access_rule
            return
    logging.warning(f"Could not find reverse entrance for {forward_entrance.name}")


def set_rules(world, multiworld: MultiWorld, player: int, options: CrystalisOptions, shuffle_data: CrystalisShuffleData) -> None:
    can_break_wall: Callable[[CollectionState, int, str], bool]
    if options.orbs_not_required:
        can_break_wall = has_level_1_sword
    else:
        can_break_wall = has_level_2_sword


