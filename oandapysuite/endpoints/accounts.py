

class Account:

    def __init__(self, data):
        for key, val in zip(data.keys(), data.values()):
            setattr(self, key, val)

    
    