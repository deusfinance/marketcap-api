non_circulating_contracts = {
    'fantom': {
        'DEUS mSig': '0xEf6b0872CfDF881Cf9Fe0918D3FA979c616AF983',
        'MasterChefV2 old': '0x120FF9821817eA2bbB700e1131e5c856ccC20d1b',
        'Minter Pool': '0x6E0098A8c651F7A6A9510B270CD02c858C344D94',
        'DUES BAG': '0xC59A3F19bf33D318F4e3eef248ACFE9B37bfc947',
        'gnosisSafe': '0x467694A3c9afFfDEB66e2E31F141148287D3Ad1E',
        'TimeBasedMasterChefRewarder': '0x90177BF4f4a5aaF5812508dbC1EBA8752C5cd605',
        'ComplexRewarder': '0xDdB816c59200aF55b1Ca20735Ef086626a2C6a8D',
        'StrategyRewarder': '0x90De614815C1e550213974C2f004C5e56C4a4be0',
        'MasterChefV2': '0x67932809213AFd6bac5ECD2e4e214Fe18209c419',
        'MultiRewarderAccess': '0x9909E6046A9Ca950Cd2a28071338BdcB7d33f9Cb',
        'TimeBasedMasterChefRewarder1': '0xA81E2bA1035f973c734f1eD23a0c0D6d197dd229',
        'TimeBasedMasterChefRewarder2': '0x58b86B32F560d025594ADFF02073Ae18976C4700',
        'Admin Wallet': '0xE5227F141575DcE74721f4A9bE2D7D636F923044',
        'veDIST': '0x09cE8C8E2704E84750E9c1a4F54A30eF60aF0073',
    },
    'polygon': {
        'Migrator': '0xD6739b3012Dd4179C0Cb45C57e6eADD063983143',
    },
    'arbitrum': {
    },
    'bsc': {
    },
    'mainnet': {
    },
    'metis': {
    }
}

bridge_pools = {
    'fantom': '0xf7b38053A4885c99279c4955CB843797e04455f8',
    'polygon': '0x1e323B29DeBdd06e5Fa498D380952ae41F46E6E8',
    'arbitrum': '0x6fF0609046A38D76Bd40C5863b4D1a2dCe687f73',
    'bsc': '0xc0DD739C4A190a45C91ED3EC587B1F3fc4d31BA6',
    'mainnet': '0x5fd564518A71AAB9B1D0Ac6D5825bbBC46a5845e',
}

xdeus_non_circulating_contracts = {
    'fantom': {
        'MasterChefV2': '0x62ad8dE6740314677F06723a7A07797aE5082Dbb',
        'DEUS mSig': '0xEf6b0872CfDF881Cf9Fe0918D3FA979c616AF983',
    }
}

xdeus_bridge_pools = {
    'fantom': '0x0cD61B1Bf6F8F2B6BA03cc8BCc57C941b7cC47a4',
    'mainnet': '0x6Ed2b2ac055bd755c3A30Fb9c039922859CaA0ba',
}

PAIR_ABI = '[{"constant":true,"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"}]'
XDEUS_POOL_ABI = '[{"inputs":[{"internalType":"uint8","name":"tokenIndexFrom","type":"uint8"},{"internalType":"uint8","name":"tokenIndexTo","type":"uint8"},{"internalType":"uint256","name":"dx","type":"uint256"}],"name":"calculateSwap","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
MASTERCHEF_ABI = '[{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"totalDepositedAmount","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
SPOOKY_USDC_FTM = '0x2b4C76d0dc16BE1C31D4C1DC53bF9B45987Fc75c'
SPOOKY_FTM_DEUS = '0xaF918eF5b9f33231764A5557881E6D3e5277d456'
DEUS_ADDRESS = '0xDE5ed76E7c05eC5e4572CfC88d1ACEA165109E44'
XDEUS_ADDRESS = '0x953Cd009a490176FcEB3a26b9753e6F01645ff28'
XDEUS_DEUS_POOL = '0x54a5039C403fff8538fC582e0e3f07387B707381'
veDEUS_ADDRESS = '0x8B42c6Cb07c8dD5fE5dB3aC03693867AFd11353d'
MASTERCHEF_XDEUS = '0x62ad8dE6740314677F06723a7A07797aE5082Dbb'
XDEUS_DEUS_SOLIDLY = '0x4EF3fF9dadBa30cff48133f5Dc780A28fc48693F'
