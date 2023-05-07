from PIL import Image, ImageGrab
from Crypto.Cipher import AES
import random, cv2
import numpy as np
def encrypt(key, iSrc, len):
    iSrc = iSrc.convert('RGB')
    bSrc = iSrc.tobytes()
    nonce = random.randbytes(8)
    cipher = AES.new(key, AES.MODE_CTR, nonce = nonce)
    bDst = cipher.encrypt(bSrc)
    iDst = Image.frombytes('RGB', iSrc.size, bDst)
    for i in range(8):
        for j in range(8):
            bit = (nonce[i] >> j & 1) * 255
            for x in range(len):
                for y in range(len):
                    iDst.putpixel((i * len + x, j * len + y), bit)
    return iDst
def decrypt(key, iSrc, len):
    iSrc = iSrc.convert('RGB')
    bSrc = iSrc.tobytes()
    nonce = bytearray(8)
    for i in range(8):
        for j in range(8):
            nonce[i] |= iSrc.getpixel((i * len + len // 2, j * len + len // 2))[0] >> 7 << j
    cipher = AES.new(key, AES.MODE_CTR, nonce = nonce)
    bDst = cipher.decrypt(bSrc)
    iDst = Image.frombytes('RGB', iSrc.size, bDst)
    return iDst
def generate(key, nSrc, nDst, size, len):
    vSrc = cv2.VideoCapture(nSrc)
    vDst = cv2.VideoWriter(nDst, cv2.VideoWriter_fourcc(*'XVID'), vSrc.get(cv2.CAP_PROP_FPS), (int(vSrc.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vSrc.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    while vSrc.isOpened():
        ret, iSrc = vSrc.read()
        if ret:
            iSrc = Image.fromarray(cv2.cvtColor(iSrc, cv2.COLOR_BGR2RGB))
            iDst = encrypt(key, iSrc.resize(size), len).resize(iSrc.size, Image.NEAREST)
            vDst.write(cv2.cvtColor(np.array(iDst), cv2.COLOR_RGB2BGR))
        else:
            break
    vSrc.release()
    vDst.release()
def screen(key, size, len):
    while True:
        iSrc = ImageGrab.grab()
        iDst = decrypt(key, iSrc.resize(size), len)
        cv2.imshow('Decrypter', cv2.cvtColor(np.array(iDst), cv2.COLOR_RGB2BGR))
        cv2.setWindowProperty('Decrypter', cv2.WND_PROP_TOPMOST, 1)
        cv2.waitKey(1)
        if cv2.getWindowProperty('Decrypter', cv2.WND_PROP_VISIBLE) < 1:
            break
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description = 'Video Encrypter/Decrypter')
    parser.add_argument('-k', '--key', type = bytes.fromhex, default = bytes(16), help = '16/24/32-byte key in hex')
    parser.add_argument('-s', '--src', type = str, default = None, help = 'source file')
    parser.add_argument('-d', '--dst', type = str, default = 'out.avi', help = 'destination file (default: out.avi)')
    parser.add_argument('-S', '--size', type = int, nargs = 2, default = (320, 180), metavar = ('WIDTH', 'HEIGHT'), help = 'size of encrypted video in pixels (default: 320x180)')
    parser.add_argument('-l', '--len', type = int, default = 1, help = 'side length corresponding to one bit in the nonce marker (in pixels in the encrypted video)')
    args = parser.parse_args()
    if args.src:
        generate(args.key, args.src, args.dst, args.size, args.len)
    else:
        screen(args.key, args.size, args.len)
if __name__ == '__main__':
    main()