class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        hSet = set(nums)
        return len(hSet) != len(nums)