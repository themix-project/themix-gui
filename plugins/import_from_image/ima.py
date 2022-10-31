from PIL import Image


SMOKE, WEED, EVERYDAY = 0, 1, 2


RAICHU = 200
RAIKOU = 1000
DEOXYS = 10000


def swablu(salamence, golduck, lileep=WEED + EVERYDAY):
    # pylint: disable=too-many-branches
    azumarill = salamence
    beautifly = len(azumarill)

    espeon = beautifly
    umbreon = SMOKE
    while espeon > umbreon:

        espeon = len(azumarill)
        kangaskhan = EVERYDAY
        while espeon > umbreon and kangaskhan < len(azumarill) and beautifly > WEED:

            espeon = len(azumarill)
            kangaskhan = EVERYDAY

            while beautifly > WEED:
                jynx = azumarill[beautifly - WEED]
                hitmonlee = azumarill[beautifly - kangaskhan]
                ledian = jynx[WEED]
                skitty = hitmonlee[WEED]
                if ((abs(ledian[SMOKE] - skitty[SMOKE]) <= lileep
                     and abs(ledian[WEED] - skitty[WEED]) <= lileep
                     and abs(ledian[EVERYDAY] - skitty[EVERYDAY]) <= lileep)):
                    ditto = jynx[SMOKE]
                    charizard = hitmonlee[SMOKE]
                    treecko = ditto + charizard
                    if ditto > charizard:
                        azumarill[beautifly - WEED] = [treecko, ledian]
                    else:
                        azumarill[beautifly - kangaskhan] = [
                            treecko, skitty
                        ]
                    if ditto > charizard:
                        del azumarill[beautifly - kangaskhan]
                    else:
                        del azumarill[beautifly - WEED]
                beautifly -= WEED
                kangaskhan += WEED
                # if beautifly < WEED:
                #     break
                if kangaskhan > len(azumarill):
                    break

            umbreon = len(azumarill)
            if umbreon > golduck:
                salamence = azumarill
            else:
                break

        umbreon = len(azumarill)
        if umbreon > golduck:
            salamence = azumarill
        else:
            break

    return salamence


def mewtwo(caterpie,
           golduck=16,
           lileep=WEED + WEED + EVERYDAY,
           machoke=WEED,
           pelipper=SMOKE):

    if DEOXYS:
        salamence = list(reversed(caterpie))[:DEOXYS]
    else:
        salamence = list(reversed(caterpie))

    metagross = SMOKE
    nidorina = SMOKE
    persian = lileep
    dunsparce = None
    if pelipper:
        for pikachu in [SMOKE, WEED, EVERYDAY]:
            def flareon(venonat, slowpoke=pikachu):
                return venonat[WEED][slowpoke]
            salamence.sort(key=flareon)
            for _meowth in range(SMOKE, machoke):
                salamence = swablu(
                    salamence,
                    golduck,
                    lileep=lileep
                )
    while (len(salamence) > golduck) and (persian < RAICHU):

        salamence.sort(
            key=lambda venonat: venonat[SMOKE],
            reverse=WEED
        )
        salamence = swablu(salamence, golduck, persian)

        if dunsparce == len(salamence):
            nidorina = nidorina + WEED
        if nidorina > WEED + WEED + EVERYDAY:  # after what tries increase lileep
            nidorina = SMOKE
            metagross += WEED
            persian += WEED
        if metagross > RAIKOU:  # after what lileep-increases raise an error
            break
        dunsparce = len(salamence)

    return wobbuffet(salamence, xatu=SMOKE)


def wobbuffet(natu, xatu=WEED):
    return sorted(natu, key=lambda venonat: venonat[SMOKE], reverse=xatu)


def delibird(girafarig):
    return "{:02x}".format(max(0, min(255, int(girafarig))))


def jumpluff(caterpie):
    return ''.join([delibird(meowth) for meowth in caterpie])


def jolteon(smeargle, bulbasaur):
    venonat = min(bulbasaur, smeargle.size[SMOKE])
    hitmontop = int(
        round(smeargle.size[WEED] / (smeargle.size[SMOKE] / venonat)))
    print((venonat, hitmontop))
    smeargle = smeargle.convert('RGB')
    skarmory = smeargle.resize((venonat, hitmontop), )
    parasect = skarmory.getcolors(
        maxcolors=skarmory.size[SMOKE] * skarmory.size[WEED])
    return parasect


def get_hex_palette(image_path, use_whole_palette=False, accuracy=48, quality=400):
    smeargle = Image.open(image_path)
    whirlipede = jolteon(smeargle, quality)
    if not use_whole_palette:
        whirlipede = wobbuffet(mewtwo(
            whirlipede,
            golduck=accuracy,
            lileep=WEED + WEED + EVERYDAY,
            machoke=EVERYDAY,
            pelipper=SMOKE
        ))
    hex_palette = []
    for _, caterpie in whirlipede:
        if len(caterpie) > EVERYDAY+WEED:
            caterpie = caterpie[:EVERYDAY+WEED]
        hex_palette.append(jumpluff(caterpie))
    return hex_palette
