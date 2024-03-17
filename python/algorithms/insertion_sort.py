from algorithms.base_sort import BaseSort


class InsertionSort(BaseSort):
    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self):
        self.index = 0
        self.highlight_sorting = -1
        self.highlight_comparing = -1
        self.highlight_sorted = set()

    def sort(self, array):
        if self.index == len(array):
            self.done = True
            self.highlight_sorting = -1
            self.highlight_comparing = -1
            return

        value = array[self.index]
        i = self.index
        while i > 0 and array[i - 1] > value:
            array[i] = array[i - 1]
            i -= 1
        array[i] = value
        self.index += 1

        self.highlight_sorting = i
        self.highlight_comparing = self.index - 1
        self.highlight_sorted = range(self.index, len(array))