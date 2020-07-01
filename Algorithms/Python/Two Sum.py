def solution(nums,target):

    hash = {}

    for i, x in enumerate(nums):
        if hash.get(target - x) is not None:
            return hash.get(target - x),i
        hash[x] = i

nums = [3,2,4]
target = 6
print(solution(nums,target))
