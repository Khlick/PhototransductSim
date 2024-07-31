from collections import deque

class StateBuffer:
    def __init__(self, maxlen=20):
        self.max_len = maxlen
        self.buffer = deque(maxlen=maxlen)
        self.current_index = 0

    def append(self, item):
        # if current index is not at the left extreme, rotate the array then append
        if self.current_index:
            for _ in range(self.current_index):
                self.buffer.popleft()
            
        # Prepend the new item and adjust the current index
        self.buffer.appendleft(item)
        self.current_index = 0

    def previous(self):
        if self.current_index < (len(self.buffer) - 1):
            self.current_index += 1
            return self.buffer[self.current_index]
        
        # If index doesn't increment, return tuple of None based on current buffer slot
        if len(self.buffer):
            num_items = len(self.buffer[self.current_index])
            return tuple(None for _ in range(num_items))
        return None

    def next(self):
        if self.current_index > 0:
            self.current_index -= 1
            return self.buffer[self.current_index]
        
        # If index doesn't decrement, return tuple of None based on current buffer slot
        if len(self.buffer):
            num_items = len(self.buffer[self.current_index])
            return tuple(None for _ in range(num_items))
        return None

    def __repr__(self):
        return f"Buffer: {list(self.buffer)}, Current index: {self.current_index}"
    
    def __iter__(self):
        return iter(self.buffer)
    
    def __len__(self):
        return len(self.buffer)
