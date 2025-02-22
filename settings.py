import os

from dotenv import load_dotenv

load_dotenv()

rpcs = {
    'fantom': [
        'https://rpcapi.fantom.network',
        'https://rpc.ankr.com/fantom',
        'https://rpc.ftm.tools',
        'https://1rpc.io/ftm',
    ],
    'polygon': [
        'https://polygon-rpc.com',
        'https://poly-rpc.gateway.pokt.network',
        'https://polygon-mainnet.public.blastapi.io',
    ],
    'arbitrum': [
        'https://arb1.arbitrum.io/rpc',
        'https://rpc.ankr.com/arbitrum',
    ],
    'bsc': [
        'https://bsc-dataseed4.ninicoin.io',
        'https://bsc-dataseed3.defibit.io',
        'https://bsc-dataseed1.binance.org',
    ],
    'mainnet': [
        'https://ethereum.publicnode.com',
        'https://eth-mainnet.public.blastapi.io',
        'https://rpc.builder0x69.io',
    ],
    'metis': [
        'https://andromeda.metis.io/?owner=1088'
    ],
    'kava': [
        'https://evm.kava.io'
    ],
    'avax': [
        'https://api.avax.network/ext/bc/C/rpc'
    ],
    'base': [
        'https://base.publicnode.com'
    ],
    'blast': [
        'https://blast.blockpi.network/v1/rpc/public',
        'https://rpc.blast.io',
        'https://blastl2-mainnet.public.blastapi.io',
    ],
    'xlayer': [
        'https://xlayerrpc.okx.com',
        'https://endpoints.omniatech.io/v1/xlayer/mainnet/public',
    ],
    'mantle': [
        'https://mantle-rpc.publicnode.com',
        'https://mantle-mainnet.public.blastapi.io',
        'https://rpc.mantle.xyz',
    ],
    'sonic': [
        'https://sonic.drpc.org',
        'https://rpc.soniclabs.com',
    ],
}


class Network:
    FANTOM = 'fantom'
    POLYGON = 'polygon'
    ARBITRUM = 'arbitrum'
    BSC = 'bsc'
    MAINNET = 'mainnet'
    METIS = 'metis'
    KAVA = 'kava'
    AVAX = 'avax'
    BASE = 'base'
    BLAST = 'blast'
    XLAYER = 'xlayer'
    MANTLE = 'mantle'
    SONIC = 'sonic'

    def __init__(self, name: str):
        if name == Network.FANTOM:
            self.excludes = {
                'leg_dei': [
                    '0x68C102aBA11f5e086C999D99620C78F5Bc30eCD8',  # Scream msig
                    '0xe3b6CC7b76a7f67BBCcb66c010780bE0AF31Ff05',  # Migrator
                    '0xC481571F724Bf3db59485b66702380E8eE342108',  # OHM
                    '0x8eFD36aA4Afa9F4E157bec759F1744A7FeBaEA0e',  # spirit LP
                    '0x622ed824050BEc39e64E19ade462093A763cC5E9',  # DevWallet DEUSDAO
                ],
                'bdei': [
                    '0xe3b6CC7b76a7f67BBCcb66c010780bE0AF31Ff05',  # Migrator
                    '0xA466FCd4c1fd62B1C9a6927148A2f01efAc24465',  # ScreamMerkle
                    '0xC6825153fA426436438F2D2364629e6DAFfAfA2D',  # MasterChef
                ],
                'xdeus': [
                    '0xe3b6CC7b76a7f67BBCcb66c010780bE0AF31Ff05',  # Migrator
                    '0x62ad8dE6740314677F06723a7A07797aE5082Dbb',  # xDEUS masterchef
                    '0x0cD61B1Bf6F8F2B6BA03cc8BCc57C941b7cC47a4',  # Bridge
                    '0x8783fbD927cA247bf0685E2B5B757ed7f85A6A86',  # BridgeWallet (Lafa)
                    '0x5354b4e74642712199Df4Ab524f96c5C0c8fBA69',  # BridgeWallet (Lafa)
                ],
                'deus': [
                    '0x0153Bf855fE4c5Dd5ACaf49C49A4a6625f071d93',  # xDEUS backing
                    '0xe3b6CC7b76a7f67BBCcb66c010780bE0AF31Ff05',  # SymmMigrator
                    '0x8B42c6Cb07c8dD5fE5dB3aC03693867AFd11353d',  # veDEUS
                    '0xf7b38053A4885c99279c4955CB843797e04455f8',  # anyDEUS
                    '0x79EC95B28f8575b1fBcE2d441031B324965B5931',  # masterChefEscrow
                    '0x5354b4e74642712199Df4Ab524f96c5C0c8fBA69',  # BridgeWallet (Lafa)
                    '0xaF918eF5b9f33231764A5557881E6D3e5277d456',  # ADMIN
                    '0x0B58eD5c0858ACd09Af8e4cBFb912c1fec1688B4',  # baseBridgeEscrow
                    '0xC59A3F19bf33D318F4e3eef248ACFE9B37bfc947',  # DEUS bag
                    '0x0092fc463b969347f2F6d18a572BDf99F61B5e8F',  # Manifold
                    '0x6E0098A8c651F7A6A9510B270CD02c858C344D94',  # BuyBacker
                    '0xBB901d8D3fAF0b675e443B2DE743d149bfe68353',  # ClaimDeus contract
                    # '0x6c9E3B6b6C528ffdF0b5248a2B47069fcEc9e835',  # DeusConversion contract V2
                    '0x33257c271cD2414B444a00346dDaE6f2BB757372',  # AxelarGateway
                    '0x7F5Ae1dC8D2B5d599409C57978D21Cf596D37996',  # msig
                    # '0x9f273FF7B9E16FA5A6e08CF7257d6E697F2B3C5A',  # DeusConversion contract V1
                    '0x183Daf1e89763968C1BFbd1C98BC1a44820f0729',  # Escrow
                    '0x5E0ddC17e87077ce74ddf46B82f026E0d260FE3b',  # tiny msig
                ],
            }
        elif name == Network.MAINNET:
            self.excludes = {
                'xdeus': [
                    '0xe3b6CC7b76a7f67BBCcb66c010780bE0AF31Ff05',  # Migrator
                ],
                'deus': [
                    '0xe3b6CC7b76a7f67BBCcb66c010780bE0AF31Ff05',  # Migrator
                    '0x714bCAF508c6e2e405EAA379BA54804EeD401add',  # AxelarGateway
                    '0x19dceFD603ea112CF547Cdddb8D68f61c6F4c73C',  # SolidlyChildProxy
                    '0xe458B32a21320d539941836995D6c059988f40CA',  # Holder
                    '0x34424Fff5E91d7CE07E82d2e9c8A1a02fA4D0cF2',  # veSOLID escrow
                    '0xf3f5E899059728e0c8aADd38779720549cf37a18',  # anyDEUS (bridge)
                    '0x7F5Ae1dC8D2B5d599409C57978D21Cf596D37996',  # msig
                ],
            }
        elif name == Network.ARBITRUM:
            self.excludes = {
                'bdei': [
                    '0xe3b6CC7b76a7f67BBCcb66c010780bE0AF31Ff05',  # Migrator
                ],
                'deus': [
                    '0x7F5Ae1dC8D2B5d599409C57978D21Cf596D37996',  # msig
                    '0xe432150cce91c13a887f7D836923d5597adD8E31',  # AxelarGateway
                    '0xe3b6CC7b76a7f67BBCcb66c010780bE0AF31Ff05',  # Migrator
                    '0xA16C48C4a07CDCd519b4354C2D094eA509124615',  # DEI incident merkle claim
                    '0xAB9b83a7F3416d921464aB018AE273fb4b284E86',  # BridgeWallet (Lafa)
                    '0x1589931E8a0B311Fc37B8DF57131Cbf60754002B',  # DAO_ARBAMOmsig
                    '0xFa78086986cA5A111497A07b4200391721eC1035',  # RamsesBeaconProxy
                    '0x42d05d13F951AA7c35Cc14453D594427928bF898',  # FeeDistributor
                    '0x0cF9Ce01b99A62B1c2AE7A79370aF5f8518dfa9d',  # BribeContract
                    '0x17A4F71319e09b57F3783D1D193E2C2A535A5ca7',  # tiny msig
                ],
            }
        elif name == Network.POLYGON:
            self.excludes = {
                'deus': [
                    '0xD6739b3012Dd4179C0Cb45C57e6eADD063983143',  # DEA_migrator
                    '0x8878Eb7F44f969D0ed72c6010932791397628546',  # AxelarGateway
                    '0xe3b6CC7b76a7f67BBCcb66c010780bE0AF31Ff05',  # Migrator
                    '0x7F5Ae1dC8D2B5d599409C57978D21Cf596D37996',  # msig
                ],
            }
        elif name == Network.BSC:
            self.excludes = {
                'deus': [
                    '0xe3b6CC7b76a7f67BBCcb66c010780bE0AF31Ff05',  # Migrator
                    '0xE5227F141575DcE74721f4A9bE2D7D636F923044',  # BridgeWallet (Lafa)
                    '0x6a524C7328eb652248d1a3786f9DB0e74CA961F0',  # ADMIN
                    '0xd1604f00F0101c87047cf7E892f04998FB1AE437',  # Bribe
                    '0x50437C8AD1fC8c40BF361d531a4f0eD215175eA1',  # ThenaBribeContract
                    '0x95fB54D8B17c8f7e94DA3aCb8D6cd11FAC29a969',  # ThenaBribeContract
                    '0xaB1Ad7FA79508ac913d3C30EA8952a4486a74451',  # ThenaBribeContract
                    '0x38A0b1cf61581f290D14016b2D37807d28CfF57b',  # AxelarGateway
                    '0x7F5Ae1dC8D2B5d599409C57978D21Cf596D37996',  # msig
                    '0x17A4F71319e09b57F3783D1D193E2C2A535A5ca7',  # tiny msig
                ],
            }
        elif name == Network.KAVA:
            self.excludes = {
                'deus': [
                    '0xE5227F141575DcE74721f4A9bE2D7D636F923044',  # * non circulating
                    '0x8c352C7e3559390EB7e9B84b291997a89A5abc93',  # * migrated
                    '0xC8c1073Bb5b83f28778E5844469604BD0c4E293d',  # AxelarGateway
                    '0x7F5Ae1dC8D2B5d599409C57978D21Cf596D37996',  # msig
                ],
            }
        elif name == Network.AVAX:
            self.excludes = {
                'deus': [
                    '0x44Fa47B1787Db408803ED688c5dC7Eb88199050a',  # AxelarGateway
                    '0xe3b6CC7b76a7f67BBCcb66c010780bE0AF31Ff05',  # Migrator
                    '0xc66035844a5E1FBEe3136b548F36211b3Ff8A973',  # Fee Distributor
                    '0xfE5f33b4cA3992af32d3b53BA7dBFA53e4d2c281',  # BribeWallet (Ross)
                    '0x4a0A3902e091cdb3AEc4279a6BFAC50297F0A79e',  # WHALE
                    '0x83B4678A24955A4100bad18f34dE65D03C711f4C',  # ExternalBribe
                    '0x7F5Ae1dC8D2B5d599409C57978D21Cf596D37996',  # msig
                ],
            }
        elif name == Network.BASE:
            self.excludes = {
                'deus': [
                    '0x3FAa9dD2781080a39B1955b16Fd24367A57F6531',  # base msig
                    '0xAB9b83a7F3416d921464aB018AE273fb4b284E86',  # WhiteKnight
                    '0xcf66F70B7d88749C1Fd2c4287Dc637ca24BA3AF2',  # BribeVotingReward
                    '0x0013efdA0FE688894b85707B89d7F0fb1a39f354',  # AxelarGateway
                    '0x07d79841B8bF0e151f95c984D3bB14F9233122EF',  # tiny msig
                ],
            }
        elif name == Network.BLAST:
            self.excludes = {
                'deus': [
                    '0x7B38CBF4250aEA97a80927c09baD72467eaEf5A6',  # AxelarGateway
                    '0x9f665cf27dEf8CcEb051cd7ac778632200885Ca7',  # blast new msig
                ],
            }
        elif name == Network.XLAYER:
            self.excludes = {
                'deus': [
                    '0x5A1De62CFB7AFE38D63ea09AD728C3F5e95BF080',  # X Layer msig
                    '0x07d79841B8bF0e151f95c984D3bB14F9233122EF',  # tiny msig
                ],
            }
        elif name == Network.MANTLE:
            self.excludes = {
                'deus': [
                    '0xA0650CFeF40C9BCCD006D3966Dedd963d7d656D6',  # mantle msig
                ],
            }
        elif name == Network.SONIC:
            self.excludes = {
                'deus': [
                    '0xfAc44Ee29f75F47C0836460EC61Dcd3BefA71877',  # sonic msig
                    '0x8897ef501b65a2C6df85bAF44eC6b64de6e7DD03',  # Escrow
                ],
            }
        else:
            raise NameError('Invalid network name')

    @classmethod
    def deus_chains(cls):
        return (cls.FANTOM, cls.POLYGON, cls.ARBITRUM, cls.BSC, cls.MAINNET,
                cls.AVAX, cls.KAVA, cls.BASE, cls.BLAST, cls.XLAYER, cls.SONIC)

    @classmethod
    def xdeus_chains(cls):
        return cls.FANTOM, cls.MAINNET

    @classmethod
    def bdei_chains(cls):
        return cls.FANTOM, cls.ARBITRUM

    @classmethod
    def leg_dei_chains(cls):
        return cls.FANTOM,


global_excludes = {
    'deus': [
        '0x77eeaf07C050a690f9B3C2E8e7642Cc3CBEcEEb4',  # RossBribingWallet
        '0x04063BE551982933c2F512A0f116D6ECc445F8eC',  # DeusOps
        '0x83B285E802D76055169B1C5e3bF21702B85b89Cb',  # Lafa
        '0x9995271aE39F8684F680E521862a9a8341219F66',  # Ross new ops wallet
    ],
}
NEW_DEUS_ADDRESS = '0xDE55B113A27Cc0c5893CAa6Ee1C020b6B46650C0'
DEUS_ADDRESS = '0xDE5ed76E7c05eC5e4572CfC88d1ACEA165109E44'
XDEUS_ADDRESS = '0x953Cd009a490176FcEB3a26b9753e6F01645ff28'
bDEI_ON_FTM = '0x05f6ea7F80BDC07f6E0728BbBBAbebEA4E142eE8'
bDEI_ON_ARB = '0x4a142eb454A1144c85D23e138A4571C697Ed2483'
legacyDEI = '0xDE12c7959E1a72bbe8a5f7A1dc8f8EeF9Ab011B3'

XDEUS_DEUS_POOL = '0x54a5039C403fff8538fC582e0e3f07387B707381'
MASTERCHEF_XDEUS = '0x62ad8dE6740314677F06723a7A07797aE5082Dbb'
MASTERCHEF_HELPER = '0x852D150abF696B34676fEf634e0Ee974D170416B'

DEUS_FIXED_TOTAL_SUPPLY = 250_000 * 10 ** 18

# .env settings
symm_api_url = os.environ.get('SYMM_API_URL') or 'https://info.deus.finance/symm'
REDIS_MARKETCAP_DB = int(os.environ.get('MARKETCAP_REDIS_N') or 0)
REDIS_PRICE_DB = int(os.environ.get('PRICE_REDIS_N') or 1)
update_timeout = int(os.environ.get('UPDATE_TIMEOUT') or 60)
proxies = None
if os.environ.get('REQUESTS_PROXY_ENABLE') in ('true', 'True', '1'):
    port = int(os.environ['SOCKS5_PORT'])
    proxies = {'http': f'socks5h://127.0.0.1:{port}', 'https': f'socks5h://127.0.0.1:{port}'}
