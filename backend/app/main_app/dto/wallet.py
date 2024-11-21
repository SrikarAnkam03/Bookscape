from flask_restx import Namespace

class walletDto:
    walletapi= Namespace('wallet',description = 'api to get wallet details')
