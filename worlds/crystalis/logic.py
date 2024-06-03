import logging

from BaseClasses import MultiWorld, CollectionState, Entrance, ItemClassification
from .options import CrystalisOptions
from .types import CrystalisShuffleData
from .locations import CrystalisLocation
from .items import CrystalisItem
from typing import Callable
from worlds.generic.Rules import set_rule, add_rule

def has_level_1_sword(state: CollectionState, player: int, element: str) -> bool:
    return state.has("Sword of " + element, player)


def has_level_2_sword(state: CollectionState, player: int, element: str) -> bool:
    return state.has("Sword of " + element, player) and \
           state.has_group(element + " Upgrades", player, 1)


def has_level_3_sword(state: CollectionState, player: int, element: str) -> bool:
    return state.has_group(element, player, 3)


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
    menu_region = multiworld.get_region("Menu", player)
    if not options.vanilla_dolphin:
        activate_shell_flute_location = CrystalisLocation(player, "Activate Shell Flute", None, menu_region)
        activate_shell_flute_location.place_locked_item(CrystalisItem("Active Shell Flute", \
                                                                      ItemClassification.progression, None, player))
        set_rule(activate_shell_flute_location, lambda state: state.has(shuffle_data.key_item_names["Shell Flute"], \
                                                                        player))
        menu_region.locations.append(activate_shell_flute_location)
        #TODO friggin' vanilla dolphin, blech

    #Need a sword to be guaranteed to be able to buy things
    #put rules on entrances instead of events because more efficient? Maybe? unsure, should benchmark
    for shop, inventory in shuffle_data.shop_inventories.items():
        if "Medical Herb" in inventory:
            buy_healing_entrance = multiworld.get_entrance("Buy Healing: " + shop, player)
            set_rule(buy_healing_entrance, lambda state: state.has_group("Sword", player, 1))
        if "Warp Boots" in inventory:
            buy_warp_boots_entrance = multiworld.get_entrance("Buy Warp Boots: " + shop, player)
            set_rule(buy_warp_boots_entrance, lambda state: state.has_group("Sword", player, 1))

    #Leaf/Wind Valley/Windmill Cave
    windmill_region = multiworld.get_region("Windmill", player)
    wind_valley_nw_cave = multiworld.get_entrance("Wind Valley - North West Cave", player)
    set_rule(wind_valley_nw_cave, lambda state: state.has(shuffle_data.key_item_names["Windmill Key"], player) and
                                                 state.can_reach(windmill_region))
    multiworld.register_indirect_condition(windmill_region, wind_valley_nw_cave)
    windmill_reward_location = multiworld.get_location("Zebu At Windmill", player)
    windmill_reward_location.access_rule = wind_valley_nw_cave.access_rule
    windmill_guard_location = multiworld.get_location("Windmill Guard Alarm Flute Tradein", player)
    set_rule(windmill_guard_location, lambda state: state.has(shuffle_data.key_item_names["Alarm Flute"], player) and
                                                    state.can_reach("Leaf Elder's House", player=player) and
                                                    state.can_reach("Zebu Student's House", player=player) and
                                                    state.can_reach("Zebu's Cave - Front", player=player))

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
                                                 state.can_reach(windmill_region))
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
                                           state.can_reach("Oak", player=player) and
                                           (state.can_reach("Leaf", player=player) or
                                           state.can_reach("Amazones", player=player) or
                                           state.can_reach("Sahara", player=player)))
    if not options.charge_shots_only:
        add_rule(stom_fight_loc, lambda state: state.has_group("Sword", player, 1) and
                                               state.can_reach("Oak", player=player), "or")

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
    set_rule(tornel_trade, lambda state: state.has_group(shuffle_data.trade_in_map["Tornel"] + " Upgrades", player, 2))

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
        set_rule(oak_item_shop_ent, lambda state: state.has("Telepathy", player) and state.can_reach(oak_mom_house) and\
                                                  state.can_reach(swamp_interior))
        oak_inn_ent = multiworld.get_entrance("Oak - Inn", player)
        oak_inn_ent.access_rule = oak_item_shop_ent.access_rule
        multiworld.register_indirect_condition(oak_mom_house, oak_item_shop_ent)
        multiworld.register_indirect_condition(oak_mom_house, oak_inn_ent)
        multiworld.register_indirect_condition(swamp_interior, oak_item_shop_ent)
        multiworld.register_indirect_condition(swamp_interior, oak_inn_ent)
    oak_mom_reward = multiworld.get_location("Oak Mother", player)
    set_rule(oak_mom_reward, lambda state: state.has("Telepathy", player) and state.can_reach(swamp_interior) and \
                                           state.can_reach("Oak", player=player))
    insect_reward = multiworld.get_location("Giant Insect", player)
    elements = ["Wind", "Fire", "Water", "Thunder"]
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
        set_rule(rabbit_trigger, lambda state: state.has("Telepathy", player) and state.can_reach(zebu_front) and \
                                               state.can_reach(zebu_back) and state.can_reach(leaf_elder) and \
                                               state.can_reach(zebu_student) and state.can_reach(rabbit_shed))
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
        sabre_n_up_to_boss = multiworld.get_entrance("Mt. Sabre North - Upper -> Mt. Sabre North - Boss", player)
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
    sabre_n_right_jail_back = multiworld.get_entrance("Mt. Sabre North - Right Jail Cell -> Mt. Sabre North - Boss",
                                                     player)
    sabre_n_right_jail_back.access_rule = can_break_sabre_north_wall
    sabre_n_gate = multiworld.get_entrance("Mt. Sabre North - Boss -> Mt. Sabre North - Elder's Cell", player)
    sabre_n_reverse_gate = multiworld.get_entrance("Mt. Sabre North - Elder's Cell -> Mt. Sabre North - Boss", player)
    set_rule(sabre_n_reverse_gate, lambda state: state.has("Sword of " + shuffle_data.boss_reqs["Kelbesque 1"], player))
    if not options.battle_magic_not_guaranteed:
        if options.sword_charge_glitch == options.sword_charge_glitch.option_in_logic:
            add_rule(sabre_n_reverse_gate, lambda state: has_any_level_3_sword(state, player), "and")
        else:
            add_rule(sabre_n_reverse_gate,
                     lambda state: has_level_3_sword(state, player, shuffle_data.boss_reqs["Kelbesque 1"]), "and")
    if options.guarantee_refresh:
        add_rule(sabre_n_reverse_gate, lambda state: state.has("Refresh", player), "and")
    sabre_n_gate.access_rule = sabre_n_reverse_gate.access_rule
    add_rule(sabre_n_gate, lambda state: state.has(shuffle_data.key_item_names["Key to Prison"], player), "and")
    sabre_n_final_wall = multiworld.get_entrance("Mt. Sabre North - Elder's Cell -> Mt. Sabre North - Final", player)
    sabre_n_final_wall.access_rule = can_break_sabre_north_wall
    set_two_way_logic(sabre_n_final_wall)
    sabre_n_elder_trigger = multiworld.get_entrance("Mt. Sabre North - Elder's Cell -> Mt. Sabre North - Rescue Reward",
                                                    player)
    sabre_n_boss_reg = multiworld.get_region("Mt. Sabre North - Boss", player)
    set_rule(sabre_n_elder_trigger, lambda state: sabre_n_reverse_gate.access_rule(state) and
                                                  state.can_reach(sabre_n_boss_reg))
    multiworld.register_indirect_condition(sabre_n_boss_reg, sabre_n_elder_trigger)
    sabre_n_back_trigger = multiworld.get_entrance("Mt. Sabre North - Final -> Mt. Sabre North - Rescue Reward", player)
    sabre_n_back_trigger.access_rule = sabre_n_elder_trigger.access_rule
    multiworld.register_indirect_condition(sabre_n_boss_reg, sabre_n_back_trigger)

    #Mt. Sabre North Locations
    sabre_n_first_chest = multiworld.get_location("Mt Sabre North Under Bridge Chest", player)
    sabre_n_first_chest.access_rule = can_break_sabre_north_wall
    sabre_n_mid_chest = multiworld.get_location("Mt Sabre North Middle Chest", player)
    sabre_n_mid_chest.access_rule = can_break_sabre_north_wall
    kelbesque1_loc = multiworld.get_location("Kelbesque 1", player)
    kelbesque1_loc.access_rule = sabre_n_reverse_gate.access_rule

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
        set_two_way_logic(statue_guards)
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
        add_rule(rage_river, lambda state: state.has(shuffle_data.trade_in_map["Rage"], player))
    rage_reward = multiworld.get_location("Rage", player)
    set_rule(rage_reward, lambda state: state.has(shuffle_data.trade_in_map["Rage"], player))
