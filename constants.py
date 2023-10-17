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
            self.xdeus_bridge_pool = '0x0cD61B1Bf6F8F2B6BA03cc8BCc57C941b7cC47a4'
        elif name == Network.POLYGON:
            self.deus_non_circulating = {
                'Migrator': '0xD6739b3012Dd4179C0Cb45C57e6eADD063983143',
            }
            self.xdeus_non_circulating = None
            self.dues_bridge_pool = '0x1e323B29DeBdd06e5Fa498D380952ae41F46E6E8'
            self.xdeus_bridge_pool = None
        elif name == Network.ARBITRUM:
            self.deus_non_circulating = None
            self.xdeus_non_circulating = None
            self.dues_bridge_pool = '0x6fF0609046A38D76Bd40C5863b4D1a2dCe687f73'
            self.xdeus_bridge_pool = None
        elif name == Network.BSC:
            self.deus_non_circulating = None
            self.xdeus_non_circulating = None
            self.dues_bridge_pool = '0xc0DD739C4A190a45C91ED3EC587B1F3fc4d31BA6'
            self.xdeus_bridge_pool = None
        elif name == Network.MAINNET:
            self.deus_non_circulating = None
            self.xdeus_non_circulating = None
            self.dues_bridge_pool = '0x5fd564518A71AAB9B1D0Ac6D5825bbBC46a5845e'
            self.xdeus_bridge_pool = '0x6Ed2b2ac055bd755c3A30Fb9c039922859CaA0ba'
        elif name == Network.METIS:
            self.deus_non_circulating = None
            self.xdeus_non_circulating = None
            self.dues_bridge_pool = None
            self.xdeus_bridge_pool = None
        elif name == Network.KAVA:
            self.deus_non_circulating = None
            self.xdeus_non_circulating = None
            self.dues_bridge_pool = None
            self.xdeus_bridge_pool = None
        elif name == Network.AVAX:
            self.deus_non_circulating = None
            self.xdeus_non_circulating = None
            self.dues_bridge_pool = None
            self.xdeus_bridge_pool = None
        else:
            raise NameError('Invalid network name')

    @classmethod
    def deus_chains(cls):
        return cls.FANTOM, cls.POLYGON, cls.ARBITRUM, cls.BSC, cls.MAINNET, cls.AVAX, cls.KAVA

    @classmethod
    def xdeus_chains(cls):
        return cls.FANTOM,


dei_reserve_token_symbols = ['USDC', 'DAI', 'USDT', 'USDD']

DEUS_ADDRESS = '0xDE5ed76E7c05eC5e4572CfC88d1ACEA165109E44'
XDEUS_ADDRESS = '0x953Cd009a490176FcEB3a26b9753e6F01645ff28'

XDEUS_DEUS_POOL = '0x54a5039C403fff8538fC582e0e3f07387B707381'
veDEUS_ADDRESS = '0x8B42c6Cb07c8dD5fE5dB3aC03693867AFd11353d'
MASTERCHEF_XDEUS = '0x62ad8dE6740314677F06723a7A07797aE5082Dbb'
MASTERCHEF_HELPER = '0x852D150abF696B34676fEf634e0Ee974D170416B'
