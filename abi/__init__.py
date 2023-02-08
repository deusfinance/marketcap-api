import json

with open('abi/erc20.json') as fp:
    ERC20_ABI = json.load(fp)

with open('abi/masterchef_xdeus.json') as fp:
    MASTERCHEF_XDEUS_ABI = json.load(fp)

with open('abi/masterchef.json') as fp:
    MASTERCHEF_ABI = json.load(fp)

with open('abi/pair.json') as fp:
    PAIR_ABI = json.load(fp)

with open('abi/swap_flashloan.json') as fp:
    SWAP_FLASHLOAN_ABI = json.load(fp)

with open('abi/masterchef_helper.json') as fp:
    MASTERCHEF_HELPER_ABI = json.load(fp)
