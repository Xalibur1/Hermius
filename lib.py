def caesar_encrypt(text, shift=3):
    result = ""
    for char in text:
        if char.isalpha():
            base = ord("a") if char.islower() else ord("A")
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result

def caesar_decrypt(encrypted_text):
    return caesar_encrypt(encrypted_text, -3)