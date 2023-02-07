import json

with open('erc20.json') as fp:
    ERC20_ABI = json.load(fp)

with open('masterchef_xdeus.json') as fp:
    MASTERCHEF_XDEUS_ABI = json.load(fp)

with open('masterchef.json') as fp:
    MASTERCHEF_ABI = json.load(fp)

with open('pair.json') as fp:
    PAIR_ABI = json.load(fp)

with open('swap_flashloan.json') as fp:
    SWAP_FLASHLOAN_ABI = json.load(fp)

with open('masterchef_helper.json') as fp:
    MASTERCHEF_HELPER_ABI = json.load(fp)
