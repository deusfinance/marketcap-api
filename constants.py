class Network:
    FANTOM = 'fantom'
    POLYGON = 'polygon'
    ARBITRUM = 'arbitrum'
    BSC = 'bsc'
    MAINNET = 'mainnet'
    METIS = 'metis'
    KAVA = 'kava'
    AVAX = 'avax'

    def __init__(self, name: str):
        if name == Network.FANTOM:
            self.deus_non_circulating = {
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
                'solidlyLabsEscrow': '0xa3C325B6BB922A773924D608ECf8100A1C60F5dB',
                'masterChefEscrow': '0x79EC95B28f8575b1fBcE2d441031B324965B5931',
                'HedgerInvestmentEscrow': '0x4d601646cE6F359F93673087CdAF415470c61ecC',
                'xDeusBackingEscrow': '0x0153Bf855fE4c5Dd5ACaf49C49A4a6625f071d93',
                'GnosisSafeProxy': '0x0BAC771371F25DF85CDbF45C48a11F11332185C2',
            }
            self.xdeus_non_circulating = {
                'MasterChefV2': '0x62ad8dE6740314677F06723a7A07797aE5082Dbb',
                'DEUS mSig': '0xEf6b0872CfDF881Cf9Fe0918D3FA979c616AF983',
            }
            self.dues_bridge_pool = '0xf7b38053A4885c99279c4955CB843797e04455f8'
            self.dei_bridge_pool = '0xbB8B2F05A88108F7e9227b954358110c20e97E26'
            self.dei_bridge_sig = '0x7F5Ae1dC8D2B5d599409C57978D21Cf596D37996'
            self.xdeus_bridge_pool = '0x0cD61B1Bf6F8F2B6BA03cc8BCc57C941b7cC47a4'
            self.usdc = '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75'
            self.amos = []
        elif name == Network.POLYGON:
            self.deus_non_circulating = {
                'Migrator': '0xD6739b3012Dd4179C0Cb45C57e6eADD063983143',
            }
            self.xdeus_non_circulating = None
            self.dues_bridge_pool = '0x1e323B29DeBdd06e5Fa498D380952ae41F46E6E8'
            self.dei_bridge_pool = '0x0dB2e82660812b56BAde5B03059f2b0133Bcd136'
            self.dei_bridge_sig = '0x7F5Ae1dC8D2B5d599409C57978D21Cf596D37996'
            self.xdeus_bridge_pool = None
            self.usdc = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
            self.amos = []
        elif name == Network.ARBITRUM:
            self.deus_non_circulating = None
            self.xdeus_non_circulating = None
            self.dues_bridge_pool = '0x6fF0609046A38D76Bd40C5863b4D1a2dCe687f73'
            self.dei_bridge_pool = '0xDf00960e0Adfea78EE29dA7FcCA17CFdDDc0A4cA'
            self.dei_bridge_sig = '0x7F5Ae1dC8D2B5d599409C57978D21Cf596D37996'
            self.xdeus_bridge_pool = None
            self.usdc = '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8'
            self.amos = ['0x1589931E8a0B311Fc37B8DF57131Cbf60754002B', '0x79E0C399816162f00E53D0996Ce4ed2108994316']  # [RAMSES, CHRONOS]
        elif name == Network.BSC:
            self.deus_non_circulating = None
            self.xdeus_non_circulating = None
            self.dues_bridge_pool = '0xc0DD739C4A190a45C91ED3EC587B1F3fc4d31BA6'
            self.dei_bridge_pool = '0x0116a8fC7500Af82c528F5Fb069a84080117482e'
            self.dei_bridge_sig = '0x7F5Ae1dC8D2B5d599409C57978D21Cf596D37996'
            self.xdeus_bridge_pool = None
            self.usdc = '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d'
            self.amos = ['0x09a8c72BeA36035c4c18DA6c13B4E56F6834Fd0A']  # [THENA]
        elif name == Network.MAINNET:
            self.deus_non_circulating = None
            self.xdeus_non_circulating = None
            self.dues_bridge_pool = '0x5fd564518A71AAB9B1D0Ac6D5825bbBC46a5845e'
            self.dei_bridge_pool = '0x4D67A556f6FB7d84A857f363518501c831e1348B'
            self.dei_bridge_sig = '0x7F5Ae1dC8D2B5d599409C57978D21Cf596D37996'
            self.xdeus_bridge_pool = '0x6Ed2b2ac055bd755c3A30Fb9c039922859CaA0ba'
            self.usdc = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
            self.amos = ['0x0D5e44ddA87a6Bc0E3adA25014fdceee545e1a05']  # [SOLIDLY]
        elif name == Network.METIS:
            self.deus_non_circulating = None
            self.xdeus_non_circulating = None
            self.dues_bridge_pool = None
            self.dei_bridge_pool = None
            self.dei_bridge_sig = None
            self.xdeus_bridge_pool = None
            self.usdc = '0xEA32A96608495e54156Ae48931A7c20f0dcc1a21'
            self.amos = []
        elif name == Network.KAVA:
            self.deus_non_circulating = None
            self.xdeus_non_circulating = None
            self.dues_bridge_pool = None
            self.dei_bridge_pool = '0xAAb1688899A833d0b6e0226afCD9a4C1128a5a77'
            self.dei_bridge_sig = '0x7F5Ae1dC8D2B5d599409C57978D21Cf596D37996'
            self.xdeus_bridge_pool = None
            self.usdc = '0xEB466342C4d449BC9f53A865D5Cb90586f405215'  # Axelar Wrapped USDC
            self.amos = []
        elif name == Network.AVAX:
            self.deus_non_circulating = None
            self.xdeus_non_circulating = None
            self.dues_bridge_pool = None
            self.dei_bridge_pool = '0x890fca365e1438B5Adb58a53413c4bf6Cbb1BDE8'
            self.dei_bridge_sig = '0x7F5Ae1dC8D2B5d599409C57978D21Cf596D37996'
            self.xdeus_bridge_pool = None
            self.usdc = '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E'
            self.amos = []
        else:
            raise NameError('Invalid network name')

    @classmethod
    def deus_chains(cls):
        return cls.FANTOM, cls.POLYGON, cls.ARBITRUM, cls.BSC, cls.MAINNET, cls.METIS

    @classmethod
    def xdeus_chains(cls):
        return cls.FANTOM,

    @classmethod
    def dei_chains(cls):
        return cls.FANTOM, cls.POLYGON, cls.ARBITRUM, cls.BSC, cls.MAINNET, cls.KAVA, cls.AVAX


USDC_ON_FTM = '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75'
USDC_ON_ETH = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
DAI_ON_ETH = '0x6B175474E89094C44Da98b954EedeAC495271d0F'
USDT_ON_ETH = '0xdAC17F958D2ee523a2206206994597C13D831ec7'
USDD_ON_ETH = '0x0C10bF8FcB7Bf5412187A595ab97a3609160b5c6'

dei_reserve_addresses = {
    Network.MAINNET: {
        '0x5B598261c2A8a9B2fb564Ff26BE93B79A87e554D': [USDC_ON_ETH,
                                                       DAI_ON_ETH,
                                                       USDT_ON_ETH,
                                                       USDD_ON_ETH],
    },
    Network.FANTOM: {
        '0x6E0098A8c651F7A6A9510B270CD02c858C344D94': [USDC_ON_FTM],
        '0x0092fc463b969347f2F6d18a572BDf99F61B5e8F': [USDC_ON_FTM],
    }
}

dei_reserve_token_symbols = ['USDC', 'DAI', 'USDT', 'USDD']

DEUS_ADDRESS = '0xDE5ed76E7c05eC5e4572CfC88d1ACEA165109E44'
XDEUS_ADDRESS = '0x953Cd009a490176FcEB3a26b9753e6F01645ff28'
DEI_ADDRESS = '0xDE1E704dae0B4051e80DAbB26ab6ad6c12262DA0'

SPOOKY_USDC_FTM = '0x2b4C76d0dc16BE1C31D4C1DC53bF9B45987Fc75c'
SPOOKY_FTM_DEUS = '0xaF918eF5b9f33231764A5557881E6D3e5277d456'
XDEUS_DEUS_POOL = '0x54a5039C403fff8538fC582e0e3f07387B707381'
veDEUS_ADDRESS = '0x8B42c6Cb07c8dD5fE5dB3aC03693867AFd11353d'
MASTERCHEF_XDEUS = '0x62ad8dE6740314677F06723a7A07797aE5082Dbb'
MASTERCHEF_HELPER = '0x852D150abF696B34676fEf634e0Ee974D170416B'
DEI_STRATEGY_ADDRESS = '0x02ee9b45a72DA0Ebb5F23984c161D1ce14490f14'

SOLIDLY_XDEUS_DEUS = '0x4EF3fF9dadBa30cff48133f5Dc780A28fc48693F'
SOLIDLY_WETH_DEUS = '0x0dF99E55FD9F829A2a57097dA4469925e90aB8c3'
SOLIDLY_WETH_DEI = '0xed82dE5C52b2CdeB3FeEd2a4a7f87d60300E19b5'
SOLIDLY_USDC_DEI = '0xc7ed724499946C8d12F57330c0d2D25Af219AdF8'
