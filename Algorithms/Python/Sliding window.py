# Goal: lowest cost with different color neighbor
# [[12,5,12],[5,12,12],[5,12,12]], 22, 5+12+5
# [[17,2,17],[16,16,5],[14,3,19]], 10, 2+5+3

class Solution(object):
    def minCost(self, costs):

        x = y = z = 0

        for r in costs:
            x,y,z = min(r[0]+y,r[0]+z), min(r[1]+x,r[1]+z), min(r[2]+x,r[2]+y)

        return min(x,y,z)


print(Solution().minCost([[12,5,12],[5,12,12],[5,12,12]]))