from server import MasterP

if __name__ == '__main__':
    from config import Config
    config = Config('127.0.0.1:8000', nworker=3)
    serv = MasterP(config)
    serv.run()
