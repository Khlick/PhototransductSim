import os
import sys
# Ensure the src directory is in the Python path
# Adjust this as it was expected to be in src/main/test
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.main.utils import StateBuffer

def main():
    # Create a StateBuffer with a maximum length of 5
    buffer = StateBuffer(maxlen=5)

    # Append some states
    buffer.append('a')
    buffer.append('b')
    buffer.append('c')
    buffer.append('d')
    buffer.append('e')

    print(buffer)  # Buffer: ['e', 'd', 'c', 'b', 'a'], Current index: 0
    
    # Undo operations
    print(buffer.previous())  # 'd'
    print(buffer.previous())  # 'c'

    # Redo operations
    print(buffer.next()) # 'd'

    print(buffer)  # Buffer: ['e', 'd', 'c', 'b', 'a'], Current index: 1

    # Append a new state
    buffer.append('f')
    print(buffer)  # Buffer: ['f', 'd', 'c', 'b', 'a'], Current index: 0

    # Redo operation reports None for nothing to redo from state 0
    print(buffer.next())  # None
    print(buffer)  # Buffer: ['f', 'd', 'c', 'b', 'a'], Current index: 0

    # Iterate over buffer
    print(f"Buffer Length: {len(buffer)}") # "Buffer Length: 5"
    for state in buffer:
        print(state)
    # Output:
    # f
    # d
    # c
    # b
    # a
    print("Final Buffer state:")
    print(buffer)
    
    print('Append beyond maxlen:')
    buffer.append('g')
    print(buffer)
    
    
    # Create a new buffer with tuple
    buffer_2 = StateBuffer(maxlen=5)
    buffer_2.append(('a','1'))
    buffer_2.append(('b','2'))
    buffer_2.append(('c','3'))
    buffer_2.append(('d','4'))
    buffer_2.append(('e','5'))
    
    print('New buffer with tuples:')
    print(buffer_2) #Buffer: [('e', '5'), ('d', '4'), ('c', '3'), ('b', '2'), ('a', '1')], Current index: 0
    
    label,index = buffer_2.previous()
    print(f'label: {label}, index: {index}.')
    print(f"Buffer Index: {buffer_2.current_index}")

if __name__ == '__main__':
    main()