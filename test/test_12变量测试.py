a = 1,2,3

def test(*args):
    one, two, three = args
    print(one)
    print(two)
    print(three)

test(*a)
