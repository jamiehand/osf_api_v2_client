import pprint

from base.utils import response_generator, DotDictify


# TODO get rid of pprint, smart_print()
pp = pprint.PrettyPrinter()
def smart_print(string):
    try:
        print(string)
    except UnicodeEncodeError:
        print(string.encode('utf-8'))

# TODO tests here

# Test returning 4
happy_gen = response_generator("https://staging2.osf.io/api/v2/nodes/xtf45/files/?path=%2F&provider=googledrive", 4)
for item in happy_gen:
    print("{}: {}: {}".format(item.provider, item.name, item.links.self))

# Test returning all available (because when num_requested is not specified, it becomes -1, ie a request to return all)
big_gen = response_generator("https://staging2.osf.io/api/v2/users/se6py/nodes/")
print(next(big_gen))
print(next(big_gen))
print(next(big_gen))
print(next(big_gen))
print(next(big_gen))
print(next(big_gen))
print(next(big_gen))
print(next(big_gen))
print(next(big_gen))
print(next(big_gen))
print(next(big_gen))
print(next(big_gen))
print(next(big_gen))
print(next(big_gen))
print(next(big_gen))
