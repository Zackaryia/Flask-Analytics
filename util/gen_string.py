from random import choice


def gen_string(length):
	return ''.join(choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-') for _ in range(length))

if __name__ == "__main__":
	print(gen_string(20))