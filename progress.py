class progress():
    def __init__(self, maxim, bar_width = 80, chars = '[# ]', supply_endings = True):
        self.maxim = maxim
        self.bar_width = bar_width
        self.left_end = chars[0]
        self.right_end = chars[3]
        self.full = chars[1]
        self.empty = chars[2]
        self.supply_endings = supply_endings
    
    def makeBar(self, count):
        if self.supply_endings:
            if count == self.maxim:
                end = '\n'
            else:
                end = '\r'
        else:
            end = ''
        onePercent = self.maxim / 100
        percentage = count / onePercent
        fraction = percentage / 100
        chars = int(self.bar_width * fraction)
        bar = '{}{}{}{}{}{}'.format(self.left_end, self.full * chars,
                                    self.empty * (self.bar_width - chars),
                                    self.right_end, '{:6}%'.format(percentage), end)
        return bar

    
    def __call__(self, count):
        if self.supply_endings:
            end = ''
        else:
            if count == self.maxim:
                end = '\n'
            else:
                end = '\r'
        print(self.makeBar(count), end=end, flush=True)

if __name__ == '__main__':
    import time
    p = progress(10);
    p(0)
    for i in range(1, 11):
        time.sleep(1)
        p(i)
