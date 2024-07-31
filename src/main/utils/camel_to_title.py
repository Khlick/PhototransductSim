def camel_to_title(camel_str):
    words = [[camel_str[0].upper()]]  # Capitalize the first character
    for c in camel_str[1:]:
        if c.isupper():
            words.append([c])
        else:
            words[-1].append(c)
    return ' '.join([''.join(word) for word in words])
