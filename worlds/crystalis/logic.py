import logging

from BaseClasses import MultiWorld, CollectionState, Entrance, ItemClassification, Region
from .options import CrystalisOptions
from .types import CrystalisShuffleData
from .locations import CrystalisLocation
from .items import CrystalisItem
from typing import Callable, List, Optional
from worlds.generic.Rules import set_rule, add_rule

def has_level_1_sword(state: CollectionState, player: int, element: str) -> bool:
    return state.has("Sword of " + element, player)


def has_level_2_sword(state: CollectionState, player: int, element: str) -> bool:
    return state.has("Sword of " + element, player) and \
           state.has_group(element + " Upgrades", player, 1)


def has_level_3_sword(state: CollectionState, player: int, element: str) -> bool:
    return state.has_group_unique(element, player, 3)


def has_any_level_2_sword(state: CollectionState, player: int) -> bool:
    return has_level_2_sword(state, player, "Wind") or \
           has_level_2_sword(state, player, "Fire") or \
           has_level_2_sword(state, player, "Water") or \
           has_level_2_sword(state, player, "Thunder")


def has_any_level_3_sword(state: CollectionState, player: int) -> bool:
    return has_level_3_sword(state, player, "Wind") or \
           has_level_3_sword(state, player, "Fire") or \
           has_level_3_sword(state, player, "Water") or \
           has_level_3_sword(state, player, "Thunder")


def set_two_way_logic(forward_entrance: Entrance) -> None:
    for entrance in forward_entrance.connected_region.exits:
        if entrance.connected_region == forward_entrance.parent_region:
            #set or add for this func? dunno, setting for now
            entrance.access_rule = forward_entrance.access_rule
            return
    logging.warning(f"Could not find reverse entrance for {forward_entrance.name}")


def get_tetrarch_fight_logic(player: int, element: str, options: CrystalisOptions, level: Optional[int] = None) -> \
    Callable[[CollectionState], bool]:
    logic: Callable[[CollectionState], bool]
    if options.tink_mode:
        logic = lambda state: state.has_group("Sword", player, 1)
    else:
        logic = lambda state: state.has("Sword of " + element, player)
    if not options.battle_magic_not_guaranteed:
        old_logic = logic
        if options.sword_charge_glitch == options.sword_charge_glitch.option_in_logic or options.tink_mode:
            if level is not None and level == 2:
                logic = lambda state: old_logic(state) and has_any_level_2_sword(state, player)
            else:
                logic = lambda state: old_logic(state) and has_any_level_3_sword(state, player)
        else:
            if level is not None and level == 2:
                logic = lambda state: old_logic(state) and has_level_2_sword(state, player, element)
            else:
                logic = lambda state: old_logic(state) and has_level_3_sword(state, player, element)
    if options.guarantee_refresh:
        old_logic = logic
        logic = lambda state: old_logic(state) and state.has("Refresh", player)
    return logic



def set_rules(multiworld: MultiWorld, player: int, options: CrystalisOptions, shuffle_data: CrystalisShuffleData) -> None:
    can_break_wall: Callable[[CollectionState, int, str], bool]
    if options.orbs_not_required:
        can_break_wall = has_level_1_sword
    else:
        can_break_wall = has_level_2_sword

    def can_cross_rivers(state: CollectionState) -> bool:
        return state.has("Flight", player) or can_break_wall(state, player, "Water")

    #make some events
    tower_region = multiworld.get_region("Tower", player)
    dyna_defeated_location = CrystalisLocation(player, "Dyna Defeated", None, tower_region)
    dyna_defeated_location.place_locked_item(CrystalisItem("Victory!", ItemClassification.progression, None, player))
    tower_region.locations.append(dyna_defeated_location)
    multiworld.completion_condition[player] = lambda state: state.has("Victory!", player)
    buy_healing_region = multiworld.get_region("Buy Healing", player)
    buy_healing_location = CrystalisLocation(player, "Buy Healing", None, buy_healing_region)
    buy_healing_location.place_locked_item(CrystalisItem("Buy Healing", ItemClassification.progression, None, player))
    buy_healing_region.locations.append(buy_healing_location)
    buy_warp_boots_region = multiworld.get_region("Buy Warp Boots", player)
    buy_warp_boots_location = CrystalisLocation(player, "Buy Warp Boots", None, buy_warp_boots_region)
    buy_warp_boots_location.place_locked_item(CrystalisItem("Buy Warp Boots", ItemClassification.progression, None, \
                                                            player))
    buy_warp_boots_region.locations.append(buy_warp_boots_location)
    mesia_region = multiworld.get_region("Mesia", player)
    mesia_location = CrystalisLocation(player, "Mesia", None, mesia_region)
    mesia_location.place_locked_item(CrystalisItem("Mesia's Message", ItemClassification.progression, None, player))
    mesia_region.locations.append(mesia_location)

    #Need a sword to be guaranteed to be able to buy things
    #put rules on entrances instead of events because more efficient? Maybe? unsure, should benchmark
    for shop, inventory in shuffle_data.shop_inventories.items():
        if shop == "Shyron Item Shop":
            #Shyron shop becomes unavailable after the massacre, so don't rely on it for logic
            continue
        if "Medical Herb" in inventory:
            buy_healing_entrance = multiworld.get_entrance("Buy Healing: " + shop, player)
            set_rule(buy_healing_entrance, lambda state: state.has_group("Sword", player, 1))
        if "Warp Boots" in inventory:
            buy_warp_boots_entrance = multiworld.get_entrance("Buy Warp Boots: " + shop, player)
            set_rule(buy_warp_boots_entrance, lambda state: state.has_group("Sword", player, 1))

    #Story Mode Events
    if options.story_mode:
        #getting to these regions means you've beaten the boss
        kelby_1_region = multiworld.get_region("Mt. Sabre North - Boss Arena", player)
        kelby_1_victory = CrystalisLocation(player, "Kelbesque 1 Defeated", None, kelby_1_region)
        kelby_1_flag = CrystalisItem("Kelbesque 1 Defeated", ItemClassification.progression, None, player)
        kelby_1_victory.place_locked_item(kelby_1_flag)
        kelby_1_region.locations.append(kelby_1_victory)
        sabera_1_region = multiworld.get_region("Sabera's Fortress - Post-Boss", player)
        sabera_1_victory = CrystalisLocation(player, "Sabera 1 Defeated", None, sabera_1_region)
        sabera_1_flag = CrystalisItem("Sabera 1 Defeated", ItemClassification.progression, None, player)
        sabera_1_victory.place_locked_item(sabera_1_flag)
        sabera_1_region.locations.append(sabera_1_victory)
        mado_1_region = multiworld.get_region("Shyron Temple - Post-Boss", player)
        mado_1_victory = CrystalisLocation(player, "Mado 1 Defeated", None, mado_1_region)
        mado_1_flag = CrystalisItem("Mado 1 Defeated", ItemClassification.progression, None, player)
        mado_1_victory.place_locked_item(mado_1_flag)
        mado_1_region.locations.append(mado_1_victory)
        kelby_2_region = multiworld.get_region("Kelbesque's Floor - Boss Arena", player)
        kelby_2_victory = CrystalisLocation(player, "Kelbesque 2 Defeated", None, kelby_2_region)
        kelby_2_flag = CrystalisItem("Kelbesque 2 Defeated", ItemClassification.progression, None, player)
        kelby_2_victory.place_locked_item(kelby_2_flag)
        kelby_2_region.locations.append(kelby_2_victory)
        sabera_2_region = multiworld.get_region("Sabera's Floor - Boss Arena", player)
        sabera_2_victory = CrystalisLocation(player, "Sabera 2 Defeated", None, sabera_2_region)
        sabera_2_flag = CrystalisItem("Sabera 2 Defeated", ItemClassification.progression, None, player)
        sabera_2_victory.place_locked_item(sabera_2_flag)
        sabera_2_region.locations.append(sabera_2_victory)
        mado_2_region = multiworld.get_region("Mado's Floor - Boss Arena", player)
        mado_2_victory = CrystalisLocation(player, "Mado 2 Defeated", None, mado_2_region)
        mado_2_flag = CrystalisItem("Mado 2 Defeated", ItemClassification.progression, None, player)
        mado_2_victory.place_locked_item(mado_2_flag)
        mado_2_region.locations.append(mado_2_victory)
        karmine_region = multiworld.get_region("Karmine's Floor - Post-Boss", player)
        karmine_victory = CrystalisLocation(player, "Karmine Defeated", None, karmine_region)
        karmine_flag = CrystalisItem("Karmine Defeated", ItemClassification.progression, None, player)
        karmine_victory.place_locked_item(karmine_flag)
        karmine_region.locations.append(karmine_victory)
        draygon_1_region = multiworld.get_region("Pyramid - Post-Draygon", player)
        draygon_1_victory = CrystalisLocation(player, "Draygon 1 Defeated", None, draygon_1_region)
        draygon_1_flag = CrystalisItem("Draygon 1 Defeated", ItemClassification.progression, None, player)
        draygon_1_victory.place_locked_item(draygon_1_flag)
        draygon_1_region.locations.append(draygon_1_victory)


    #Leaf/Wind Valley/Windmill Cave
    windmill_region = multiworld.get_region("Windmill", player)
    wind_valley_nw_cave = multiworld.get_entrance("Wind Valley - North West Cave", player)
    set_rule(wind_valley_nw_cave, lambda state: state.has(shuffle_data.key_item_names["Windmill Key"], player) and
                                                 windmill_region.can_reach(state))
    multiworld.register_indirect_condition(windmill_region, wind_valley_nw_cave)
    windmill_reward_location = multiworld.get_location("Zebu At Windmill", player)
    windmill_reward_location.access_rule = wind_valley_nw_cave.access_rule
    windmill_guard_location = multiworld.get_location("Windmill Guard Alarm Flute Tradein", player)
    set_rule(windmill_guard_location, lambda state: state.has(shuffle_data.key_item_names["Alarm Flute"], player) and
                                                    state.can_reach_region("Leaf Elder's House", player) and
                                                    state.can_reach_region("Zebu Student's House", player) and
                                                    state.can_reach_region("Zebu's Cave - Front", player))

    #GBC Cave
    if options.vanilla_maps == options.vanilla_maps.option_GBC_cave:
        gbc_wall_entrance = multiworld.get_entrance("GBC Cave - Main -> GBC Cave - Past Block", player)
        set_rule(gbc_wall_entrance, lambda state: can_break_wall(state, player, shuffle_data.wall_map["GBC Cave"]))
        set_two_way_logic(gbc_wall_entrance)

    #Zebu's Cave
    zebus_wall_entrance = multiworld.get_entrance("Zebu's Cave - Front -> Zebu's Cave - Back", player)
    set_rule(zebus_wall_entrance, lambda state: can_break_wall(state, player, shuffle_data.wall_map["Zebu's Cave"]))
    set_two_way_logic(zebus_wall_entrance)

    #Sealed Cave
    def can_break_sealed_cave_wall(state: CollectionState) -> bool:
        return can_break_wall(state, player, shuffle_data.wall_map["Sealed Cave"])
    sealed_cave_first_wall = multiworld.get_entrance("Sealed Cave - Front -> Sealed Cave - Back", player)
    sealed_cave_first_wall.access_rule = can_break_sealed_cave_wall
    set_two_way_logic(sealed_cave_first_wall)
    sealed_cave_final_wall = multiworld.get_entrance("Sealed Cave - Back -> Sealed Cave - Exit", player)
    sealed_cave_final_wall.access_rule = can_break_sealed_cave_wall
    set_two_way_logic(sealed_cave_final_wall)
    sealed_cave_ne_chest = multiworld.get_location("Sealed Cave Big Room Northeast Chest", player)
    sealed_cave_ne_chest.access_rule = can_break_sealed_cave_wall
    vamp_1_reward = multiworld.get_location("Vampire 1", player)
    set_rule(vamp_1_reward, lambda state: state.has_group("Sword", player, 1))

    #Cordel Plains/Brynmaer/Amazones/Stom Fight
    if not options.shuffle_areas:
        cordel_nw_cave = multiworld.get_entrance("Cordel Plains - North West Cave", player)
        set_rule(cordel_nw_cave, lambda state: state.has(shuffle_data.key_item_names["Windmill Key"], player) and \
                                                 windmill_region.can_reach(state))
        multiworld.register_indirect_condition(windmill_region, cordel_nw_cave)
    cordel_river = multiworld.get_entrance("Cordel Plains - Main -> Cordel Plains - River Blocked", player)
    cordel_river.access_rule = can_cross_rivers
    set_two_way_logic(cordel_river)
    if not options.trigger_skip == options.trigger_skip.option_in_logic:
        cordel_ne_ow = multiworld.get_entrance("Cordel Plains - North East", player)
        set_rule(cordel_ne_ow, lambda state: state.has("Teleport", player))
        if options.mt_sabre_skip == options.mt_sabre_skip.option_in_logic:
            add_rule(cordel_ne_ow, lambda state: state.has("Flight", player), "or")
        if not options.statue_glitch == options.statue_glitch.option_in_logic:
            aryllis_house_ent = multiworld.get_entrance("Amazones - Aryllis's House", player)
            set_rule(aryllis_house_ent, lambda state: state.has("Change", player) or state.has("Paralysis", player))
    akahana_trade_loc = multiworld.get_location("Akahana Statue of Onyx Tradein", player)
    akahana_trade_item = shuffle_data.trade_in_map["Akahana"]
    set_rule(akahana_trade_loc, lambda state: state.has(akahana_trade_item, player))
    aryllis_trade_loc = multiworld.get_location("Aryllis", player)
    aryllis_trade_item = shuffle_data.trade_in_map["Aryllis"]
    set_rule(aryllis_trade_loc, lambda state: state.has(aryllis_trade_item, player) and state.has("Change", player))
    stom_fight_loc = multiworld.get_location("Stom Fight Reward", player)
    set_rule(stom_fight_loc, lambda state: state.has("Buy Warp Boots", player) and
                                           state.can_reach_region("Oak", player) and
                                           (state.can_reach_region("Leaf", player) or
                                           state.can_reach_region("Amazones", player) or
                                           state.can_reach_region("Sahara", player)))
    if not options.charge_shots_only:
        add_rule(stom_fight_loc, lambda state: state.has_group("Sword", player, 1) and
                                               state.can_reach_region("Oak", player), "or")

    #Mt. Sabre West
    def can_break_sabre_west_wall(state: CollectionState) -> bool:
        return can_break_wall(state, player, shuffle_data.wall_map["Mt. Sabre West"])
    if not options.trigger_skip == options.trigger_skip.option_in_logic:
        sabre_w_small_slope = multiworld.get_entrance("Mt. Sabre West - Main -> Mt. Sabre West - Tornado Cave", player)
        set_rule(sabre_w_small_slope, lambda state: state.has("Flight", player) or state.has("Rabbit Boots", player) or \
                                                    state.has("Speed Boots", player))
    sabre_w_big_slope = multiworld.get_entrance("Mt. Sabre West - Main -> Mt. Sabre West - Upper", player)
    set_rule(sabre_w_big_slope, lambda state: state.has("Flight", player))
    sabre_w_right_wall_1 = multiworld.get_entrance("Mt. Sabre West - Main -> Mt. Sabre West - Interior", player)
    sabre_w_right_wall_1.access_rule = can_break_sabre_west_wall
    set_two_way_logic(sabre_w_right_wall_1)
    sabre_w_right_wall_2 = multiworld.get_entrance("Mt. Sabre West - Interior -> Mt. Sabre West - Upper", player)
    sabre_w_right_wall_2.access_rule = can_break_sabre_west_wall
    set_two_way_logic(sabre_w_right_wall_2)
    sabre_w_final_wall = multiworld.get_entrance("Mt. Sabre West - Upper -> Mt. Sabre West - Final", player)
    sabre_w_final_wall.access_rule = can_break_sabre_west_wall
    tornado_chest = multiworld.get_location("Mt Sabre West Tornado Bracelet Chest", player)
    tornado_chest.access_rule = can_break_sabre_west_wall
    ledge_chest = multiworld.get_location("Mt Sabre West Left Chest", player)
    ledge_chest.access_rule = can_break_sabre_west_wall
    tornel_trade = multiworld.get_location("Mt Sabre West Tornel", player)
    set_rule(tornel_trade, lambda state: state.has_group_unique(shuffle_data.trade_in_map["Tornel"] + " Upgrades",
                                                                player, 2))

    #Swamp/Oak
    swamp_pass_1 = multiworld.get_entrance("Swamp - Near Side -> Swamp - Interior", player)
    set_rule(swamp_pass_1, lambda state: state.has("Hazmat Suit", player) or state.has("Gas Mask", player))
    if options.gas_mask_not_guaranteed:
        add_rule(swamp_pass_1, lambda state: state.has("Buy Healing", player) or \
                                             (state.has("Refresh", player) and state.has_group("Sword", player, 1)), \
                 "or")
    swamp_pass_2 = multiworld.get_entrance("Swamp - Far Side -> Swamp - Interior", player)
    swamp_pass_2.access_rule = swamp_pass_1.access_rule
    set_two_way_logic(swamp_pass_1)
    set_two_way_logic(swamp_pass_2)
    swamp_interior = multiworld.get_region("Swamp - Interior", player)
    if not options.statue_glitch == options.statue_glitch.option_in_logic:
        oak_mom_house = multiworld.get_region("Oak Mom House", player)
        oak_item_shop_ent = multiworld.get_entrance("Oak - Item Shop", player)
        set_rule(oak_item_shop_ent, lambda state: state.has("Telepathy", player) and oak_mom_house.can_reach(state) and\
                                                  swamp_interior.can_reach(state))
        oak_inn_ent = multiworld.get_entrance("Oak - Inn", player)
        oak_inn_ent.access_rule = oak_item_shop_ent.access_rule
        multiworld.register_indirect_condition(oak_mom_house, oak_item_shop_ent)
        multiworld.register_indirect_condition(oak_mom_house, oak_inn_ent)
        multiworld.register_indirect_condition(swamp_interior, oak_item_shop_ent)
        multiworld.register_indirect_condition(swamp_interior, oak_inn_ent)
    oak_mom_reward = multiworld.get_location("Oak Mother", player)
    set_rule(oak_mom_reward, lambda state: state.has("Telepathy", player) and swamp_interior.can_reach(state) and \
                                           state.can_reach_region("Oak", player))
    insect_reward = multiworld.get_location("Giant Insect", player)
    elements = ["Wind", "Fire", "Water", "Thunder"]
    insect_weapons: List[str]
    if options.tink_mode:
        insect_weapons = ["Sword of " + x for x in elements]
    else:
        insect_weapons = ["Sword of " + x for x in elements if x != shuffle_data.boss_reqs["Giant Insect"]]
    set_rule(insect_reward, lambda state: state.has(shuffle_data.key_item_names["Insect Flute"], player) and \
                                          (state.has("Gas Mask", player) or state.has("Hazmat Suit", player)) and \
                                          state.has_any(insect_weapons, player))
    oak_elder_reward = multiworld.get_location("Oak Elder", player)
    set_rule(oak_elder_reward, lambda state: state.has("Telepathy", player) and (state.can_reach(insect_reward) or \
                                                                                 state.can_reach(oak_mom_reward)))

    #Mt. Sabre North entrances
    def can_break_sabre_north_wall(state: CollectionState) -> bool:
        return can_break_wall(state, player, shuffle_data.wall_map["Mt. Sabre North"])
    if options.trigger_skip != options.trigger_skip.option_in_logic and \
       options.mt_sabre_skip != options.mt_sabre_skip.option_in_logic:
        rabbit_trigger = multiworld.get_entrance("Mt. Sabre North - Pre-Trigger -> Mt. Sabre North - Main", player)
        #ugh, ugly; maybe better to do more events here? esp. for spoiler log readability
        zebu_front = multiworld.get_region("Zebu's Cave - Front", player)
        zebu_back = multiworld.get_region("Zebu's Cave - Back", player)
        leaf_elder = multiworld.get_region("Leaf Elder's House", player)
        zebu_student = multiworld.get_region("Zebu Student's House", player)
        rabbit_shed = multiworld.get_region("Leaf Shed", player)
        set_rule(rabbit_trigger, lambda state: state.has("Telepathy", player) and zebu_front.can_reach(state) and \
                                               zebu_back.can_reach(state) and leaf_elder.can_reach(state) and \
                                               zebu_student.can_reach(state) and rabbit_shed.can_reach(state))
        multiworld.register_indirect_condition(zebu_front, rabbit_trigger)
        multiworld.register_indirect_condition(zebu_back, rabbit_trigger)
        multiworld.register_indirect_condition(leaf_elder, rabbit_trigger)
        multiworld.register_indirect_condition(zebu_student, rabbit_trigger)
        multiworld.register_indirect_condition(rabbit_shed, rabbit_trigger)
    sabre_n_first_wall = multiworld.get_entrance("Mt. Sabre North - Main -> Mt. Sabre North - Interior", player)
    sabre_n_first_wall.access_rule = can_break_sabre_north_wall
    sabre_n_main_to_up = multiworld.get_entrance("Mt. Sabre North - Main -> Mt. Sabre North - Upper", player)
    set_rule(sabre_n_main_to_up, lambda state: can_break_sabre_north_wall(state) or state.has("Flight", player))
    if options.trigger_skip != options.trigger_skip.option_in_logic:
        sabre_n_up_to_int = multiworld.get_entrance("Mt. Sabre North - Upper -> Mt. Sabre North - Interior", player)
        set_rule(sabre_n_up_to_int, lambda state: can_break_sabre_north_wall(state) \
                                                  or state.has("Flight", player) \
                                                  or state.has("Rabbit Boots", player) \
                                                  or state.has("Speed Boots", player))
        sabre_n_up_to_boss = multiworld.get_entrance("Mt. Sabre North - Upper -> Mt. Sabre North - Pre-Boss", player)
        set_rule(sabre_n_up_to_boss, lambda state: state.has("Flight", player))
    sabre_n_left_jail_door = multiworld.get_entrance("Mt. Sabre North - Upper -> Mt. Sabre North - Left Jail Cell",
                                                     player)
    sabre_n_left_jail_door.access_rule = can_break_sabre_north_wall
    set_two_way_logic(sabre_n_left_jail_door)
    sabre_n_left_jail_back = multiworld.get_entrance("Mt. Sabre North - Left Jail Cell -> Mt. Sabre North - Prison Key",
                                                     player)
    sabre_n_left_jail_back.access_rule = can_break_sabre_north_wall
    set_two_way_logic(sabre_n_left_jail_back)
    sabre_n_right_jail_door = multiworld.get_entrance("Mt. Sabre North - Upper -> Mt. Sabre North - Right Jail Cell",
                                                     player)
    sabre_n_right_jail_door.access_rule = can_break_sabre_north_wall
    set_two_way_logic(sabre_n_right_jail_door)
    sabre_n_right_jail_back = multiworld.get_entrance("Mt. Sabre North - Right Jail Cell -> Mt. Sabre North - Pre-Boss",
                                                     player)
    sabre_n_right_jail_back.access_rule = can_break_sabre_north_wall

    kelbesque_1_logic = get_tetrarch_fight_logic(player, shuffle_data.boss_reqs["Kelbesque 1"], options)
    sabre_n_boss = multiworld.get_entrance("Mt. Sabre North - Pre-Boss -> Mt. Sabre North - Boss Arena", player)
    sabre_n_boss.access_rule = kelbesque_1_logic
    sabre_n_gate = multiworld.get_entrance("Mt. Sabre North - Boss Arena -> Mt. Sabre North - Elder's Cell", player)
    set_rule(sabre_n_gate, lambda state: state.has(shuffle_data.key_item_names["Key to Prison"], player))
    sabre_n_reverse_gate = multiworld.get_entrance("Mt. Sabre North - Elder's Cell -> Mt. Sabre North - Boss Arena",
                                                   player)
    sabre_n_reverse_gate.access_rule = kelbesque_1_logic
    sabre_n_final_wall = multiworld.get_entrance("Mt. Sabre North - Elder's Cell -> Mt. Sabre North - Final", player)
    sabre_n_final_wall.access_rule = can_break_sabre_north_wall
    set_two_way_logic(sabre_n_final_wall)
    sabre_n_elder_trigger = multiworld.get_entrance("Mt. Sabre North - Elder's Cell -> Mt. Sabre North - Rescue Reward",
                                                    player)
    sabre_n_boss_reg = multiworld.get_region("Mt. Sabre North - Boss Arena", player)
    sabre_n_elder_trigger.access_rule = sabre_n_boss_reg.can_reach
    multiworld.register_indirect_condition(sabre_n_boss_reg, sabre_n_elder_trigger)
    sabre_n_back_trigger = multiworld.get_entrance("Mt. Sabre North - Final -> Mt. Sabre North - Rescue Reward", player)
    sabre_n_back_trigger.access_rule = sabre_n_boss_reg.can_reach
    multiworld.register_indirect_condition(sabre_n_boss_reg, sabre_n_back_trigger)

    #Mt. Sabre North Locations
    sabre_n_first_chest = multiworld.get_location("Mt Sabre North Under Bridge Chest", player)
    sabre_n_first_chest.access_rule = can_break_sabre_north_wall
    sabre_n_mid_chest = multiworld.get_location("Mt Sabre North Middle Chest", player)
    sabre_n_mid_chest.access_rule = can_break_sabre_north_wall
    kelbesque_1_loc = multiworld.get_location("Kelbesque 1", player)
    kelbesque_1_loc.access_rule = kelbesque_1_logic

    #Waterfall Valley
    if not options.shuffle_areas:
        waterfall_hilltop_cave = multiworld.get_entrance("Waterfall Hilltop Cave", player)
        set_rule(waterfall_hilltop_cave, lambda state: state.has(shuffle_data.key_item_names["Key to Prison"], player))
    if options.trigger_skip != options.trigger_skip.option_in_logic:
        waterfall_slope = multiworld.get_entrance("Waterfall Valley - Main -> Waterfall Valley - By Prison", player)
        set_rule(waterfall_slope, lambda state: state.has("Flight", player))
    waterfall_n_river = multiworld.get_entrance("Waterfall Valley - Main -> Waterfall Valley - By North River", player)
    waterfall_n_river.access_rule = can_cross_rivers
    set_two_way_logic(waterfall_n_river)
    waterfall_s_river = multiworld.get_entrance("Waterfall Valley - Main -> Waterfall Valley - By South River", player)
    waterfall_s_river.access_rule = can_cross_rivers
    set_two_way_logic(waterfall_s_river)

    #Waterfall Cave
    def can_break_waterfall_cave_walls(state: CollectionState) -> bool:
        return can_break_wall(state, player, shuffle_data.wall_map["Waterfall Cave"])
    water_cave_first_wall = multiworld.get_entrance("Waterfall Cave - Front -> Waterfall Cave - Before Statues", player)
    water_cave_first_wall.access_rule = can_break_waterfall_cave_walls
    set_two_way_logic(water_cave_first_wall)
    if not options.statue_glitch:
        statue_guards = multiworld.get_entrance("Waterfall Cave - Before Statues -> Waterfall Cave - After Statues", \
                                                player)
        set_rule(statue_guards, lambda state: state.has(shuffle_data.key_item_names["Flute of Lime"], player))
    water_cave_back_wall = multiworld.get_entrance("Waterfall Cave - After Statues -> Waterfall Cave - Back", player)
    water_cave_back_wall.access_rule = can_break_waterfall_cave_walls
    set_two_way_logic(water_cave_back_wall)
    waterfall_front_chest = multiworld.get_location("Waterfall Cave Front Mimic", player)
    waterfall_front_chest.access_rule = can_break_waterfall_cave_walls
    rockahana = multiworld.get_location("Akahana Flute of Lime Tradein", player)
    set_rule(rockahana, lambda state: state.has(shuffle_data.key_item_names["Flute of Lime"], player))
    waterfall_blocked_chest = multiworld.get_location("Waterfall Cave Sword of Water Chest", player)
    waterfall_blocked_chest.access_rule = can_break_waterfall_cave_walls

    #Fog Lamp Cave
    def can_break_fog_lamp_cave_walls(state: CollectionState) -> bool:
        return can_break_wall(state, player, shuffle_data.wall_map["Fog Lamp Cave"])
    fog_lamp_walls = multiworld.get_entrance("Fog Lamp Cave - Front -> Fog Lamp Cave - Behind Walls", player)
    fog_lamp_walls.access_rule = can_break_fog_lamp_cave_walls
    set_two_way_logic(fog_lamp_walls)
    fog_lamp_items = multiworld.get_entrance("Fog Lamp Cave - Behind Walls -> Fog Lamp Cave - Items", player)
    fog_lamp_items.access_rule = can_break_fog_lamp_cave_walls

    #Kirisa Plant Cave
    def can_break_kirisa_plant_cave_walls(state: CollectionState) -> bool:
        return can_break_wall(state, player, shuffle_data.wall_map["Kirisa Plant Cave"])
    kirisa_first_wall = multiworld.get_entrance("Kirisa Plant Cave - Front -> Kirisa Plant Cave - Middle", player)
    kirisa_first_wall.access_rule = can_break_kirisa_plant_cave_walls
    set_two_way_logic(kirisa_first_wall)
    kirisa_second_wall = multiworld.get_entrance("Kirisa Plant Cave - Middle -> Kirisa Plant Cave - Back", player)
    kirisa_second_wall.access_rule = can_break_kirisa_plant_cave_walls
    set_two_way_logic(kirisa_second_wall)
    kirisa_middle_chest = multiworld.get_location("Kirisa Plant Cave Chest", player)
    kirisa_middle_chest.access_rule = can_break_kirisa_plant_cave_walls

    #Rage
    rage_river = multiworld.get_entrance("Rage - South -> Rage - North", player)
    rage_river.access_rule = can_cross_rivers
    if options.rage_skip != options.rage_skip.option_in_logic:
        add_rule(rage_river, lambda state: state.has(shuffle_data.trade_in_map["Rage"], player), "and")
    rage_reward = multiworld.get_location("Rage", player)
    set_rule(rage_reward, lambda state: state.has(shuffle_data.trade_in_map["Rage"], player))

    #Portoa Castle
    teller_front = multiworld.get_region("Fortune Teller - Front", player)
    teller_back = multiworld.get_region("Fortune Teller - Back", player)
    gift_trigger = multiworld.get_region("Portoa Palace - Gift Trigger", player)
    first_guard = multiworld.get_entrance("Portoa Palace - Foyer -> Portoa Palace - Throne Room", player)
    second_guard = multiworld.get_entrance("Portoa Palace - Throne Room -> Portoa Palace - Gift Trigger", player)
    queen_gift = multiworld.get_location("Portoa Queen", player)
    set_rule(queen_gift, lambda state: teller_front.can_reach(state) or teller_back.can_reach(state))
    add_rule(queen_gift, lambda state: state.has(shuffle_data.trade_in_map["Rage"], player) or
                                       gift_trigger.can_reach(state), "and")
    add_rule(queen_gift, lambda state: state.has("Mesia's Message", player), "or")
    if options.trigger_skip != options.trigger_skip.option_in_logic and \
       options.statue_glitch != options.trigger_skip.option_in_logic:
        set_rule(first_guard, lambda state: state.has("Paralysis", player) or
                                            teller_front.can_reach(state) or
                                            teller_back.can_reach(state) or
                                            state.has("Mesia's Message", player))
        set_rule(second_guard, lambda state: state.has("Paralysis", player) or state.has("Mesia's Message", player))
        multiworld.register_indirect_condition(teller_front, first_guard)
        multiworld.register_indirect_condition(teller_back, first_guard)

    #Portoa Waterway
    def can_cross_ocean(state: CollectionState) -> bool:
        return state.has("Flight", player) or state.has("Active Shell Flute", player)
    waterway_top_river = multiworld.get_entrance("Portoa Waterway - Main -> Asina's Chambers", player)
    waterway_top_river.access_rule = can_cross_rivers
    waterway_bottom_river = multiworld.get_entrance("Portoa Waterway - Main -> Fortune Teller - Back", player)
    waterway_bottom_river.access_rule = can_cross_rivers
    waterway_shore = multiworld.get_entrance("Portoa Waterway - Main -> Portoa Waterway - Water", player)
    waterway_shore.access_rule = can_cross_ocean
    asina = multiworld.get_location("Asina In Back Room", player)
    set_rule(asina, lambda state: state.has("Mesia's Message", player))
    dolphin = multiworld.get_location("Injured Dolphin", player)
    set_rule(dolphin, lambda state: asina.can_reach(state) and state.has("Buy Healing", player))
    underwater_item = multiworld.get_location("Underground Channel Underwater Chest", player)
    set_rule(underwater_item, lambda state: state.has("Active Shell Flute", player))

    #Fisherman, Beach House, and Shell Flute stuff
    boat = multiworld.get_entrance("Fisherman House Area -> Angry Sea - Beach House Area", player)
    set_rule(boat, lambda state: state.has("Boat Access", player))
    fisherman_house = multiworld.get_region("Fisherman House", player)
    boat_access_location = CrystalisLocation(player, "Fisherman", None, fisherman_house)
    boat_access_location.place_locked_item(CrystalisItem("Boat Access", ItemClassification.progression, None, player))
    set_rule(boat_access_location, lambda state: state.has(shuffle_data.trade_in_map["Fisherman"], player))
    fisherman_house.locations.append(boat_access_location)
    region_for_flute_activation: Region
    shell_flute_rule: Callable[[CollectionState], bool]
    if not options.vanilla_dolphin:
        region_for_flute_activation = multiworld.get_region("Menu", player)
        shell_flute_rule = lambda state: state.has(shuffle_data.key_item_names["Shell Flute"], player)
        beach_kensu_location = multiworld.get_location("Kensu In Cabin", player)
        set_rule(beach_kensu_location, lambda state: state.has("Boat Access", player))
    else:
        region_for_flute_activation = multiworld.get_region("Beach House", player)
        shell_flute_rule = lambda state: state.has(shuffle_data.key_item_names["Shell Flute"], player) and \
                                         state.has("Boat Access", player)
        add_rule(boat_access_location, lambda state: dolphin.can_reach(state), "and")
    activate_shell_flute_location = CrystalisLocation(player, "Activate Shell Flute", None, region_for_flute_activation)
    activate_shell_flute_location.place_locked_item(CrystalisItem("Active Shell Flute", \
                                                                      ItemClassification.progression, None, player))
    activate_shell_flute_location.access_rule = shell_flute_rule
    region_for_flute_activation.locations.append(activate_shell_flute_location)

    #Angry Sea
    beach_house_shore = multiworld.get_entrance("Angry Sea - Beach House Area -> Angry Sea - South Water", player)
    beach_house_shore.access_rule = can_cross_ocean
    right_shore = multiworld.get_entrance("Angry Sea - Cave Area -> Angry Sea - South Water", player)
    right_shore.access_rule = can_cross_ocean
    flooded_shore = multiworld.get_entrance("Angry Sea - Flooded Cave Land -> Angry Sea - Flooded Cave Water", player)
    flooded_shore.access_rule = can_cross_ocean
    north_shore = multiworld.get_entrance("Angry Sea - North Land -> Angry Sea - North Water", player)
    north_shore.access_rule = can_cross_ocean
    if options.trigger_skip != options.trigger_skip.option_in_logic:
        flooded_cave = multiworld.get_entrance("Angry Sea - South Water -> Angry Sea - Flooded Cave Water", player)
        set_rule(flooded_cave, lambda state: state.has("Active Shell Flute", player))
    seafalls = multiworld.get_entrance("Angry Sea - South Water -> Angry Sea - North Water", player)
    set_rule(seafalls, lambda state: state.has(shuffle_data.key_item_names["Statue of Gold"], player) or
                                     state.has("Flight", player))
    if options.fake_flight == options.fake_flight.option_in_logic:
        add_rule(seafalls, lambda state: state.has("Rabbit Boots", player), "or")
    whirlpool_location = multiworld.get_location("Behind Whirlpool", player)
    set_rule(whirlpool_location, lambda state: state.has(shuffle_data.key_item_names["Statue of Gold"], player))
    #I guess Glowing Lamp + Broken Statue should go here
    repaired_statue = multiworld.get_location("Repaired Statue", player)
    set_rule(repaired_statue, lambda state: state.has(shuffle_data.key_item_names["Broken Statue"], player) and
                                            state.has(shuffle_data.key_item_names["Glowing Lamp"], player))

    #Joel/Lighthouse
    shed_secret = multiworld.get_entrance("Joel Shed - Secret Passage", player)
    set_rule(shed_secret, lambda state: state.has("Eye Glasses", player))
    sleepy_kensu = multiworld.get_location("Kensu In Lighthouse", player)
    set_rule(sleepy_kensu, lambda state: state.has(shuffle_data.key_item_names["Alarm Flute"], player))

    #Evil Spirit Island
    def can_break_esi_walls(state: CollectionState) -> bool:
        return can_break_wall(state, player, shuffle_data.wall_map["Evil Spirit Island"])
    esi_river = multiworld.get_entrance("Evil Spirit Island - Front -> Evil Spirit Island - Across River", player)
    esi_river.access_rule = can_cross_rivers
    set_two_way_logic(esi_river)
    esi_stairs = multiworld.get_entrance("Evil Spirit Island - Across River -> Evil Spirit Island - Upstairs", player)
    esi_stairs.access_rule = can_break_esi_walls
    #no reverse logic necessary - can fall down the pit
    esi_side_wall = multiworld.get_entrance("Evil Spirit Island - Upstairs -> Evil Spirit Island - Item Stash", player)
    esi_side_wall.access_rule = can_break_esi_walls
    set_two_way_logic(esi_side_wall)
    esi_downstairs_chest = multiworld.get_location("Evil Spirit Island Lower Chest", player)
    esi_downstairs_chest.access_rule = can_break_esi_walls
    esi_river_chest = multiworld.get_location("Evil Spirit Island River Left Chest", player)
    esi_river_chest.access_rule = can_cross_rivers

    #Sabera's Fortress/Zombie Town
    can_cross_pain: Callable[[CollectionState], bool]
    #we'll be using this a lot later on
    if options.gas_mask_not_guaranteed:
        can_cross_pain = lambda state: state.has_any(["Flight", "Hazmat Suit", "Rabbit Boots",
                                                      "Leather Boots"], player) or \
                                       (state.has_group("Sword", player, 1) and
                                        state.has_any(["Refresh", "Buy Healing"], player))
    else:
        can_cross_pain = lambda state: state.has_any(["Flight", "Hazmat Suit", "Rabbit Boots", "Leather Boots"], player)
    vamp_2_fight = multiworld.get_entrance("Sabera's Fortress - Front -> Sabera's Fortress - Upstairs", player)
    vamp_2_reward = multiworld.get_location("Vampire 2", player)
    vamp_2_weapons: List[str]
    if options.tink_mode:
        vamp_2_weapons = ["Sword of " + x for x in elements]
    else:
        vamp_2_weapons = ["Sword of " + x for x in elements if x != shuffle_data.boss_reqs["Vampire 2"]]
    vamp_2_logic = lambda state: state.has_any(vamp_2_weapons, player)
    vamp_2_fight.access_rule = vamp_2_logic
    vamp_2_reward.access_rule = vamp_2_logic
    sabera_spike_chest = multiworld.get_location("Sabera Upstairs Right Chest", player)
    sabera_spike_chest.access_rule = can_cross_pain
    sabera_1_fight = multiworld.get_entrance("Sabera's Fortress - Upstairs -> Sabera's Fortress - Post-Boss", player)
    sabera_1_fight.access_rule = get_tetrarch_fight_logic(player, shuffle_data.boss_reqs["Sabera 1"], options)
    sabera_1_post_boss = multiworld.get_region("Sabera's Fortress - Post-Boss", player)
    clark = multiworld.get_location("Clark", player)
    clark.access_rule = sabera_1_post_boss.can_reach

    #Swan/Swan Gate
    swan_gate = multiworld.get_entrance("Guard Checkpoint - South -> Guard Checkpoint - North", player)
    set_rule(swan_gate, lambda state: state.has("Change", player))
    set_two_way_logic(swan_gate)
    tag_kensu = multiworld.get_location("Kensu In Swan", player)
    set_rule(tag_kensu, lambda state: state.has("Paralysis", player) and
                                      state.has(shuffle_data.trade_in_map["Tag Kensu"], player) and
                                      state.can_reach_region("Swan Shed", player) and
                                      state.can_reach_region("Swan Pub", player))

    #Mt. Hydra
    def can_break_hydra_walls(state: CollectionState) -> bool:
        return can_break_wall(state, player, shuffle_data.wall_map["Mt. Hydra"])
    hydra_lower_river = multiworld.get_entrance("Mt. Hydra - Lower -> Mt. Hydra - Guarded Palace", player)
    hydra_lower_river.access_rule = can_cross_rivers
    set_two_way_logic(hydra_lower_river)
    shyron_region = multiworld.get_region("Shyron", player)
    massacre_trigger = multiworld.get_region("Goa Entrance - Massacre Trigger", player)
    if options.statue_glitch != options.statue_glitch.option_in_logic:
        shyron_temple = multiworld.get_region("Shyron Temple", player)
        hydra_guardpost = multiworld.get_entrance("Mt. Hydra - Guardpost", player)
        set_rule(hydra_guardpost, lambda state: state.has("Change", player) or shyron_region.can_reach(state) or
                                                (state.has("Sword of Thunder", player) and
                                                 shyron_temple.can_reach(state) and
                                                 massacre_trigger.can_reach(state)))
    hydra_upper_river = multiworld.get_entrance("Mt. Hydra - Lower -> Mt. Hydra - Upper", player)
    hydra_upper_river.access_rule = can_cross_rivers
    set_two_way_logic(hydra_upper_river)
    hydra_first_wall = multiworld.get_entrance("Mt. Hydra - Upper -> Mt. Hydra - Wide Cave", player)
    hydra_first_wall.access_rule = can_break_hydra_walls
    set_two_way_logic(hydra_first_wall)
    hydra_second_wall = multiworld.get_entrance("Mt. Hydra - Wide Cave -> Mt. Hydra - Summit", player)
    hydra_second_wall.access_rule = can_break_hydra_walls
    set_two_way_logic(hydra_second_wall)
    hydra_palace = multiworld.get_entrance("Mt. Hydra - Palace", player)
    set_rule(hydra_palace, lambda state: state.has(shuffle_data.key_item_names["Key to Stxy"], player))
    hydra_ledge = multiworld.get_location("Mt Hydra Left Right Chest", player)
    hydra_ledge.access_rule = can_break_hydra_walls
    hydra_summit = multiworld.get_location("Mt Hydra Summit Chest", player)
    set_rule(hydra_summit, lambda state: state.has("Flight", player))

    #Shyron
    mado_1_fight = multiworld.get_entrance("Shyron Temple -> Shyron Temple - Post-Boss", player)
    mado_1_fight_logic = get_tetrarch_fight_logic(player, shuffle_data.boss_reqs["Mado 1"], options)
    set_rule(mado_1_fight, lambda state: state.has("Sword of Thunder", player) and
                                          massacre_trigger.can_reach(state) and
                                          mado_1_fight_logic(state))

    #Stxy
    can_cross_shooters_south = lambda state: state.has("Barrier", player)
    if options.barrier_not_guaranteed:
        old_func = can_cross_shooters_south
        can_cross_shooters_south = lambda state: old_func(state) or \
                                                 (state.has_group("Sword", player, 1) and
                                                 (state.has("Shield Ring", player) or
                                                  state.has("Buy Healing", player) or
                                                  state.has("Refresh", player)))
    can_cross_shooters_north = can_cross_shooters_south
    if options.statue_gauntlet_skip:
        can_cross_shooters_north = lambda state: state.has("Flight", player) or can_cross_shooters_south(state)
    stxy_gauntlet = multiworld.get_entrance("Stxy - Front -> Stxy - Downstairs", player)
    stxy_gauntlet.access_rule = can_cross_shooters_north
    stxy_reverse = multiworld.get_entrance("Stxy - Downstairs -> Stxy - Front", player)
    stxy_reverse.access_rule = can_cross_shooters_south
    stxy_right_river = multiworld.get_entrance("Stxy - Downstairs -> Stxy - Right", player)
    set_rule(stxy_right_river, lambda state: state.has("Flight", player))
    #no two-way logic - can't get to Stxy - Right any other way
    stxy_left_river = multiworld.get_entrance("Stxy - Downstairs -> Stxy - Upstairs", player)
    stxy_left_river.access_rule = can_cross_rivers
    #no two-way logic - can drop from hole above to reach downstairs
    stxy_spike_chest = multiworld.get_location("Stxy Left Upper Sword of Thunder Chest", player)
    stxy_spike_chest.access_rule = can_cross_pain

    #Goa Town
    if options.statue_glitch != options.statue_glitch.option_in_logic:
        goa_inn_ent = multiworld.get_entrance("Goa - Inn", player)
        goa_item_ent = multiworld.get_entrance("Goa - Item Shop", player)
        goa_inn_ent.access_rule = shyron_region.can_reach
        goa_item_ent.access_rule = shyron_region.can_reach
        multiworld.register_indirect_condition(shyron_region, goa_inn_ent)
        multiworld.register_indirect_condition(shyron_region, goa_item_ent)
    brokahana = multiworld.get_location("Brokahana", player)
    mado_1_region = multiworld.get_region("Shyron Temple - Post-Boss", player)
    set_rule(brokahana, lambda state: state.has("Change", player) and mado_1_region.can_reach(state))

    #Goa Fortress - Entrance
    goa_entrance_shooter_n = multiworld.get_entrance("Goa Entrance - Front -> Goa Entrance - Massacre Trigger", player)
    goa_entrance_shooter_n.access_rule = can_cross_shooters_north
    goa_entrance_shooter_s = multiworld.get_entrance("Goa Entrance - Massacre Trigger -> Goa Entrance - Front", player)
    goa_entrance_shooter_s.access_rule = can_cross_shooters_south
    goa_entrance_wall = multiworld.get_entrance("Goa Entrance - Massacre Trigger -> Goa Entrance - Behind Wall", player)
    set_rule(goa_entrance_wall, lambda state: can_break_wall(state, player, shuffle_data.wall_map["Goa Entrance"]))
    set_two_way_logic(goa_entrance_wall)

    #Goa Fortress - Kelbesque's Floor
    kelbesque_2_logic = get_tetrarch_fight_logic(player, shuffle_data.boss_reqs["Kelbesque 2"], options)
    kelbesque_2_forward = multiworld.get_entrance("Kelbesque's Floor - Front -> Kelbesque's Floor - Boss Arena", player)
    kelbesque_2_forward.access_rule = kelbesque_2_logic
    kelbesque_2_backward = multiworld.get_entrance("Kelbesque's Floor - Back -> Kelbesque's Floor - Boss Arena", player)
    kelbesque_2_backward.access_rule = kelbesque_2_logic

    #Goa Fortress - Sabera's Floor
    sabera_river = multiworld.get_entrance("Sabera's Floor - Front -> Sabera's Floor - Across Rivers", player)
    sabera_river.access_rule = can_cross_rivers
    set_two_way_logic(sabera_river)
    sabera_river_items = multiworld.get_entrance("Sabera's Floor - Front -> Sabera's Floor - River Items", player)
    sabera_river_items.access_rule = can_cross_rivers
    sabera_boss_wall = multiworld.get_entrance("Sabera's Floor - Across Rivers -> Sabera's Floor - Pre-Boss", player)
    set_rule(sabera_boss_wall, lambda state: can_break_wall(state, player, shuffle_data.wall_map["Sabera Boss"]))
    set_two_way_logic(sabera_boss_wall)
    sabera_2_logic = get_tetrarch_fight_logic(player, shuffle_data.boss_reqs["Sabera 2"], options)
    sabera_2_forward = multiworld.get_entrance("Sabera's Floor - Pre-Boss -> Sabera's Floor - Boss Arena", player)
    sabera_2_forward.access_rule = sabera_2_logic
    sabera_2_backward = multiworld.get_entrance("Sabera's Floor - Back -> Sabera's Floor - Boss Arena", player)
    sabera_2_backward.access_rule = sabera_2_logic
    sabera_wall_item = multiworld.get_location("Fortress Sabera Northwest Chest", player)
    set_rule(sabera_wall_item, lambda state: can_break_wall(state, player, shuffle_data.wall_map["Sabera Item"]))

    #Goa Fortress - Mado's Floor
    mado_spike_items = multiworld.get_entrance("Mado's Floor - Front -> Mado's Floor - Spike Items", player)
    mado_spike_items.access_rule = can_cross_pain
    mado_left = multiworld.get_entrance("Mado's Floor - Front -> Mado's Floor - Upstairs Left", player)
    mado_left.access_rule = can_cross_pain
    mado_right = multiworld.get_entrance("Mado's Floor - Front -> Mado's Floor - Upstairs Right", player)
    mado_right.access_rule = can_cross_pain
    mado_2_logic = get_tetrarch_fight_logic(player, shuffle_data.boss_reqs["Mado 2"], options)
    mado_2_forward = multiworld.get_entrance("Mado's Floor - Upstairs Right -> Mado's Floor - Boss Arena", player)
    mado_2_forward.access_rule = mado_2_logic
    mado_2_backward = multiworld.get_entrance("Mado's Floor - Back -> Mado's Floor - Boss Arena", player)
    mado_2_backward.access_rule = mado_2_logic
    mado_wall_item = multiworld.get_location("Fortress Mado Upper Behind Wall Chest", player)
    set_rule(mado_wall_item, lambda state: can_break_wall(state, player, shuffle_data.wall_map["Mado"]))

    #Goa Fortress - Karmine's Floor
    karmine_wall = multiworld.get_entrance("Karmine's Floor - Front -> Karmine's Floor - Back", player)
    set_rule(karmine_wall, lambda state: can_break_wall(state, player, shuffle_data.wall_map["Karmine"]))
    set_two_way_logic(karmine_wall)
    karmine_spikes = multiworld.get_entrance("Karmine's Floor - Back -> Karmine's Floor - Item Stash", player)
    karmine_spikes.access_rule = can_cross_pain
    karmine_boss_door = multiworld.get_entrance("Karmine's Floor - Back -> Karmine's Floor - Pre-Boss Gauntlet", player)
    karmine_boss_door.access_rule = can_cross_pain
    set_two_way_logic(karmine_boss_door)
    karmine_gauntlet = multiworld.get_entrance("Karmine's Floor - Pre-Boss Gauntlet -> Karmine's Floor - Boss Arena",
                                               player)
    karmine_gauntlet.access_rule = can_cross_shooters_north
    karmine_logic = get_tetrarch_fight_logic(player, shuffle_data.boss_reqs["Karmine"], options, level=2)
    karmine_fight = multiworld.get_entrance("Karmine's Floor - Boss Arena -> Karmine's Floor - Post-Boss", player)
    karmine_fight.access_rule = karmine_logic
    slime_kensu = multiworld.get_location("Slimed Kensu", player)
    set_rule(slime_kensu, lambda state: state.has(shuffle_data.trade_in_map["Slime Kensu"], player))

    #Oasis Cave/Power Ring Basement
    oasis_river = multiworld.get_entrance("Oasis Cave - Front -> Oasis Cave - Across the River", player)
    set_rule(oasis_river, lambda state: state.has("Flight", player))
    set_two_way_logic(oasis_river)
    purple_pain = multiworld.get_entrance("Oasis Cave - Across the River -> Oasis Cave - Past Purple Pain", player)
    purple_pain.access_rule = can_cross_pain
    set_two_way_logic(purple_pain)
    oasis_river_maze = multiworld.get_entrance("Oasis Cave - Front -> Oasis Cave - By Deep Entrance", player)
    oasis_river_maze.access_rule = can_cross_rivers
    set_two_way_logic(oasis_river_maze)
    power_ring_loc = multiworld.get_location("Oasis Cave Fortress Basement Chest", player)
    set_rule(power_ring_loc, lambda state: can_break_wall(state, player, shuffle_data.wall_map["Power Ring Basement"]))
    battle_armor_loc = multiworld.get_location("Battle Armor Chest", player)
    set_rule(battle_armor_loc, lambda state: state.has("Flight", player))
    oasis_river_maze_loc = multiworld.get_location("Oasis Cave Near Entrance Chest", player)
    oasis_river_maze_loc.access_rule = can_cross_rivers

    #Desert 1/2, Deo Valley
    desert_1_whirlpool = multiworld.get_entrance("Desert 1 -> Desert 1 - Past Whirlpool", player)
    set_rule(desert_1_whirlpool, lambda state: state.has("Flight", player))
    set_two_way_logic(desert_1_whirlpool)
    pyramid_whirlpool = multiworld.get_entrance("Desert 2 -> Desert 2 - Past Pyramid Whirlpools", player)
    set_rule(pyramid_whirlpool, lambda state: state.has("Flight", player))
    set_two_way_logic(pyramid_whirlpool)
    crypt_whirlpool = multiworld.get_entrance("Desert 2 -> Desert 2 - Past Crypt Whirlpools", player)
    set_rule(crypt_whirlpool, lambda state: state.has("Flight", player))
    set_two_way_logic(crypt_whirlpool)
    deo = multiworld.get_location("Deo", player)
    set_rule(deo, lambda state: state.has("Change", player) and state.has("Telepathy", player))

    #Pyramid
    draygon_1_fight = multiworld.get_entrance("Pyramid -> Pyramid - Post-Draygon", player)
    if options.battle_magic_not_guaranteed:
        set_rule(draygon_1_fight, lambda state: state.has_group("Sword", player, 1))
    else:
        set_rule(draygon_1_fight, lambda state: has_any_level_2_sword(state, player))
    if options.guarantee_refresh:
        add_rule(draygon_1_fight, lambda state: state.has("Refresh", player), "and")

    #Bow Passage/Crypt
    bow_statues = multiworld.get_entrance("Bow Passage - Front -> Bow Passage - Back", player)
    set_rule(bow_statues, lambda state: state.has(shuffle_data.key_item_names["Bow of Sun"], player) and
                                        state.has(shuffle_data.key_item_names["Bow of Moon"], player))
    set_two_way_logic(bow_statues)
    crypt_spike_pit_a = multiworld.get_entrance("Crypt - Front -> Crypt - Middle", player)
    crypt_spike_pit_a.access_rule = can_cross_pain
    set_two_way_logic(crypt_spike_pit_a)
    crypt_spike_pit_b = multiworld.get_entrance("Crypt - Front -> Crypt - Left", player)
    crypt_spike_pit_b.access_rule = can_cross_pain
    set_two_way_logic(crypt_spike_pit_b)
    crypt_spike_pit_c = multiworld.get_entrance("Crypt - Middle -> Crypt - Back", player)
    crypt_spike_pit_c.access_rule = can_cross_pain
    set_two_way_logic(crypt_spike_pit_c)
    crypt_right_chest = multiworld.get_location("Crypt Right Chest", player)
    crypt_right_chest.access_rule = can_cross_pain

    #Draygon 2 Logic
    draygon_2_fight = multiworld.get_entrance("Crypt - Pre-Draygon -> Tower", player)
    if options.battle_magic_not_guaranteed:
        set_rule(draygon_2_fight, lambda state: state.has_group("Sword", player, 1))
    else:
        set_rule(draygon_2_fight, lambda state: has_any_level_3_sword(state, player))
    if not options.no_bow_mode:
        add_rule(draygon_2_fight, lambda state: state.has(shuffle_data.key_item_names["Bow of Truth"], player), "and")
    if options.guarantee_refresh:
        add_rule(draygon_2_fight, lambda state: state.has("Refresh", player), "and")
    if options.story_mode:
        spawn_reqs: List[str] = ["Sword of Wind", "Sword of Fire", "Sword of Water", "Sword of Thunder",
                                 "Kelbesque 1 Defeated", "Sabera 1 Defeated", "Mado 1 Defeated",
                                 "Kelbesque 2 Defeated", "Sabera 2 Defeated", "Mado 2 Defeated",
                                 "Karmine Defeated", "Draygon 1 Defeated"]
        add_rule(draygon_2_fight, lambda state: state.has_all(spawn_reqs, player), "and")
