

"""  Obtain terrain squares setups (including attacker and defender points).

Valid values are from 0 to 6 (seven valid values).
The terrain info is packed two terrain squares per byte.
First add higher nybble in byte to setup list, then add lower 4 bits

Vanilla rom contains 41 battle map setups (41 provinces)

Each battle map:
12 rows and 13 columns of terrain squares. 156 terrain squares total per battle map.


The scenarios all share the same battle map terrain setups and available starting points (Xs and Os).

"""





def obtain_collection_of_setups(setups_binary):


    provinces_arrays_of_battle_setups = [None] * 41
    for p in range(41):

        # Every province requires 78 bytes, with 2 terrain squares per byte. 156 terrain squares total.
        battle_setup = [0] * 156
        for j in range(78):

            current_byte = setups_binary[j + p * 78]

            first_half = (current_byte & 0b11110000) >> 4
            second_half = current_byte & 0b00001111

            battle_setup[j * 2] = first_half
            battle_setup[j * 2 + 1] = second_half

        provinces_arrays_of_battle_setups[p] = battle_setup

    return provinces_arrays_of_battle_setups





if __name__ == '__main__':

    import os



    from copier_header import smc_header


    # adjusted_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'R2.smc')  # maybe double check this
    adjusted_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rotk2.sfc')
    rom_path = adjusted_path


    SMC_header = smc_header(rom_path)


    with open(rom_path, "rb") as f_rom:

        ## the SFC start location is 0x32994.
        ## the SMC start read location is 0x32B94. The amount to read is 0xc7e, i.e. smc: (0x33812 - 0x32B94).
        f_rom.seek(0x32994 + SMC_header, 0)
        province_terrain_setups_binary = f_rom.read(0xc7e)

        ## attacker and defender starting points
        ## SMC: (start + 1) minus end (length in bytes): (0x32B93 + 1) - 0x31F16
        f_rom.seek(0x31D16 + SMC_header, 0)
        battle_maps_starting_points_binary = f_rom.read(0xc7e)



    # this is currently implemented as 2d list:
    terrain_setups = obtain_collection_of_setups(province_terrain_setups_binary)

    battle_setups_starting_points = obtain_collection_of_setups(battle_maps_starting_points_binary)



    # debugging / examination stuff

    assert not [y for L in terrain_setups for y in L if y > 6]  # 0 to 6 inclusive

    assert max([y for L in battle_setups_starting_points for y in L]) <= 7 # 0 to 7 inclusive
    temp_set = {y for L in battle_setups_starting_points for y in L}


    # more debugging / examination stuff
    print()
    # a_setup = list(range(12*13))
    a_setup = terrain_setups[33]  # province thirty-four
    for r in range(12):
        for c in range(13):
            tile = a_setup[r * 13 + c]
            print(tile, end='  ')
        print('\n')


    print()
    print()


    print("starting points for a province:")
    # a_setup = list(range(12*13))
    a_setup = battle_setups_starting_points[33]  # province thirty-four
    for r in range(12):
        for c in range(13):
            tile = a_setup[r * 13 + c]
            print(tile, end='  ')
        print('\n')

    print('Done.')


