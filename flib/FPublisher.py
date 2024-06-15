# -*- coding: utf-8 -*-

class IPublisher(object):
    def __init__(self):
        pass
    def register(self):
        pass
    def unregister(self):
        pass
    def notifyAll(self):
        pass
    def on_notify(self, *args, **kwargs):
        pass

class ISubscriber(object):
    def __init__(self):
        pass
    def on_notify(self, *args, **kwargs):
        pass
    def notify(self):
        pass

class Publisher(IPublisher):
    def __init__(self):
        self._listOfUsers = []
    def register(self, user):
        if user not in self._listOfUsers:
            self._listOfUsers.append(user)
    def unregister(self, user):
        self._listOfUsers.remove(user)
    def notifyAll(self, *args, **kwargs):
        for user in self._listOfUsers:
            user.on_notify(*args, **kwargs)
    def on_notify(self, *args, **kwargs):
        print (args, kwargs)

class Subscriber(ISubscriber):
    def __init__(self, publisher = None):
        self._publisher = publisher
    def on_notify(self, *args, **kwargs):
        print (args, kwargs)
    def notify(self, *args, **kwargs):
        self._publisher.on_notify(*args, **kwargs)
        
    
def main():
    w = Publisher()
    a = Subscriber(w)
    b = Subscriber(w)
    w.register(a)
    w.register(b)
    w.notifyAll(1,b=1)

    b.notify(b)

if __name__ == "__main__":
    main()