#coding=utf-8

import memcache

class Memcached(object):
	"""docstring for Memcached"""
	mc = memcache.Client(['127.0.0.1:12333'], debug = False)

	@classmethod
	def get(cls, key, default = None):
		return cls.mc.get(key) or default

	@classmethod
	def set(cls, key, value, timeout = 0):
		return cls.mc.set(key, value, timeout)

	@classmethod
	def clear(cls):
		return cls.mc.flush_all()



if __name__ == '__main__':
	Memcached.set('a', 'fjlajfl')
	print (Memcached.get('a'))
	Memcached.set('a','')
	print (Memcached.get('a', 'b'))