nums = [1,2,3,4,5,6]
oddNums = [x for x in nums if x % 2 == 1]
print oddNums
oddNumsPlusOne = [x+1 for x in nums if x % 2 ==1]
print oddNumsPlusOne

strings = ['Hellozz', 'WHatYTTT', 'IS', 'GOING', 'ON?']
s_lower = [s.lower() for s in strings if len(s) > 5]
print s_lower 
