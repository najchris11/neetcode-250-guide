"""
Definition of Interval:
class Interval(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
"""

#10 mins, did not watch soln
class Solution:
    def canAttendMeetings(self, intervals: List[Interval]) -> bool:
        sched = sorted(intervals, key = lambda interval: interval.start)
        for i in range(len(sched) - 1):
            if sched[i].end > sched[i+1].start:
                return False
        return True