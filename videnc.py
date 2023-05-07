#!/usr/bin/python3
from PIL import Image, ImageGrab, ImageTk
from Crypto.Cipher import AES
import random, cv2
import numpy as np
import tkinter as tk
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
def generate(key, nSrc, nDst, res, len):
    vSrc = cv2.VideoCapture(nSrc)
    vDst = cv2.VideoWriter(nDst, cv2.VideoWriter_fourcc(*'XVID'), vSrc.get(cv2.CAP_PROP_FPS), (int(vSrc.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vSrc.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    while vSrc.isOpened():
        ret, mSrc = vSrc.read()
        if ret:
            iSrc = Image.fromarray(cv2.cvtColor(mSrc, cv2.COLOR_BGR2RGB))
            iDst = encrypt(key, iSrc.resize(res), len).resize(iSrc.size, Image.NEAREST)
            vDst.write(cv2.cvtColor(np.array(iDst), cv2.COLOR_RGB2BGR))
        else:
            break
    vSrc.release()
    vDst.release()
class Decrypter(tk.Tk):
    def __init__(self, key, res, len):
        super().__init__()
        self.key = key
        self.res = res
        self.len = len
        self.title('Video Decrypter')
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        self.geometry('-0-0')
        self.bind('<Escape>', lambda e: self.quit())
        self.bind('<Button-1>', self.click)
        self.bind('<B1-Motion>', self.drag)
        self.label = tk.Label(self)
        self.label.pack()
        self.refresh()
    def click(self, e):
        self.x = e.x
        self.y = e.y
    def drag(self, e):
        self.geometry('+%d+%d' % (self.winfo_pointerx() - self.x, self.winfo_pointery() - self.y))
    def refresh(self):
        iSrc = ImageGrab.grab()
        iDst = decrypt(self.key, iSrc.resize(self.res), self.len)
        self.label.imgtk = ImageTk.PhotoImage(iDst)
        self.label.configure(image = self.label.imgtk)
        self.after(1, self.refresh)
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description = 'Video Encrypter/Decrypter')
    parser.add_argument('-k', '--key', type = bytes.fromhex, default = bytes(16), help = '16/24/32-byte key in hex')
    parser.add_argument('-s', '--src', type = str, default = None, help = 'source file')
    parser.add_argument('-d', '--dst', type = str, default = 'out.avi', help = 'destination file (default: out.avi)')
    parser.add_argument('-r', '--res', type = int, nargs = 2, default = (320, 180), metavar = ('WIDTH', 'HEIGHT'), help = 'resolution of the encrypted video (default: 320x180)')
    parser.add_argument('-l', '--len', type = int, default = 1, help = 'side length corresponding to one bit in the nonce marker (default: 1)')
    args = parser.parse_args()
    if args.src:
        generate(args.key, args.src, args.dst, args.res, args.len)
    else:
        Decrypter(args.key, args.res, args.len).mainloop()
if __name__ == '__main__':
    main()
