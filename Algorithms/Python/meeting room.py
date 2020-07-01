# Goal: calculate room need for meeting
# [[0,30],[5,10],[15,20]], 2
# [[0,10],[15,20]],1

import heapq

input1 = [[0,30],[5,10],[15,20]]
input2 = [[0,30],[5,10],[9,20]]
input3 = [[0,10],[15,20]]
input4 = []

class Solution():
    def minMeetingRooms(self,intervals):
        if len(intervals) == 0:
            return 0

        intervals.sort(key= lambda x:x[0]) 

        stack = []
        heapq.heappush(stack,intervals[0][1])

        for i in intervals[1:]:
            if stack[0] <= i[0]:
                heapq.heappop(stack)

            heapq.heappush(stack,i[1])
        
        return len(stack)


print(Solution().minMeetingRooms(input1))
print(Solution().minMeetingRooms(input2))
print(Solution().minMeetingRooms(input3))
print(Solution().minMeetingRooms(input4))

