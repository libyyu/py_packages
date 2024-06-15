# -*- coding: utf-8 -*-
import multiprocessing
from flib.FPublisher import ISubscriber, IPublisher

class FTask(multiprocessing.Process, ISubscriber):
    """
    单个任务操作
    """
    def __init__(self, publisher = None):
        super(FTask, self).__init__()
        self._multi_process = False
        self._publisher = publisher
        self._lock = None
    def __work__(self):
        pass
    def getResult(self):
        pass
    def run(self):
        self._multi_process = True
        if self._lock: self._lock.acquire()
        success = self.__work__()
        if self._lock: self._lock.release()
        self.notify(success, self)
        if not success: exit(1)
        else: exit(0)
    def work(self):
        self._multi_process = False
        success = self.__work__()
        self.notify(success, self)
    def notify(self, *args, **kwargs):
        if self._publisher is None:
            print ("publisher is none")
            return
        self._publisher.on_notify(*args, **kwargs)
    def on_notify(self, *args, **kwargs):
        pass
    def update_lock(self, lock):
        self._lock = lock


class FTaskCenter(IPublisher):
    """
    多任务管理器
    """
    def __init__(self):
        super(FTaskCenter, self).__init__()
        self._lock = multiprocessing.Lock()
        self._tasks = []
        self._multi_process = False

    def Lock(self):
        self._lock.acquire()

    def Unlock(self):
        self._lock.release()

    def notifyAll(self,*args, **kwargs):
        self.Lock()
        for task in self._tasks:
            task.on_notify(*args, **kwargs)
        self.Unlock()

    def on_notify(self, *args, **kwargs):
        print (args, kwargs)
        task = args[1]
        print (task.getResult())

    def addTask(self, task):
        """
        添加一个任务
        task: FTask
        """
        if not isinstance(task, FTask): 
            raise Exception("argument #1 type {0} expected got {1}".format(FTask, type(task)))
        self.Lock()
        self._tasks.append(task)
        self.Unlock()

    def removeTask(self, task):
        self.Lock()
        self._tasks.remove(task)
        self.Unlock()

    @property
    def TaskCount(self):
        nCount = 0
        self.Lock()
        nCount = len(self._tasks)
        self.Unlock()
        return nCount

    def run(self, multi_process = False):
        self._multi_process = multi_process
        if not multi_process:
            self.Lock()
            for task in self._tasks:
                task.work()
            self.Unlock()
        else:
            self.Lock()
            for task in self._tasks:
                task.update_lock(multiprocessing.Lock())
            for task in self._tasks:
                task.start()
            for task in self._tasks:
                task.join()
            self.Unlock()
            for task in self._tasks:
                self.removeTask(task)

def main():
    mgr = FTaskCenter()
    mgr.addTask(FTask(mgr))
    mgr.addTask(FTask(mgr))
    mgr.run(True)


if __name__ == "__main__":
    main()
