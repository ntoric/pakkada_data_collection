
def mask_mobile(value):
    if not value:
        return value
    
    # Keep last 4, mask others
    if len(str(value)) <= 4:
        return value
    
    masked_part = '*' * (len(str(value)) - 4)
    last_four = str(value)[-4:]
    return f"{masked_part}{last_four}"

test_cases = [
    "9876543210",
    9876543210,
    "1234",
    1234,
    "",
    None,
    "9876 543 210",
    " +91 9876543210 ",
]

for tc in test_cases:
    print(f"Input: {tc!r} -> Output: {mask_mobile(tc)!r}")
