def split_by_len(string, length):
  result = []
  for i in range(0, len(string), length):
    result.append(string[i:i + length])
  return result
