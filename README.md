# StreamEnc

StreamEnc is an encryption tool for streaming media that allows users to encrypt a video on the server side into another secret video that can be streamed, and decrypt the original video directly on the client side.

## Usage

- Server Side

  ```
  python3 streamenc.py -s your/video/to/encrypt.mp4 -d enc.mp4 -k 12345678abcdef12345678abcdef
  ```

  Encrypt your/video/to/encrypt.mp4 to out.avi using AES-128 CTR mode with `12345678abcdef12345678abcdef` as the key.

  ```
  Optional arguments
  
  -S WIDTH HEIGHT  size of encrypted video in pixels (320x180 as default, which
                   in my experiments worked the best result in bilibili's live
                   stream (since the live screen will be compressed, a higher
                   resolution may instead result in a more illegible decrypted
                   screen))
  
  -l LEN           side length corresponding to one bit in the nonce marker (in
                   pixels in the encrypted video) (1 as default, but I recommend
                   setting this to an upward rounding of HEIGHT/200, e.g. with
                   -S as the default value, this should be set to 2)
  ```

  Also, note that in order to be able to decrypt the video correctly on the client side, the input video should be in the same scale as the client's monitor and preferably at the same resolution.

  Once you're done, just use out.avi as the video source for your stream.

- Client Side

  Open the stream and play it full screen (at the top of the main monitor), then run the following command: (the -k, -S, -l arguments need to be the same as on the server side)

  ```
  python3 streamenc.py -k 12345678abcdef12345678abcdef
  ```

  The decrypted video will be displayed in the small pop-up window.

![example](https://user-images.githubusercontent.com/83796250/236632203-cb979b2d-0e96-4c14-9792-2769010e97cc.png)

## FAQ

- Why use AES-128?

  Because it's fast (due to the AES instruction set).
  
- Why use CTR Mode?

  Video is compressed during transmission. The CTR mode turns the block cipher into a stream cipher, which directly XORs the plaintext with the key stream generated by the user key to obtain the ciphertext, so that each bit is independent in the encryption and decryption process, the bit that changes due to being compressed will not affect the decryption of other bits; and if other encryption modes such as ECB, CBC, CFB, etc. are used, then any small change will make the decryption of the entire block where it is located wrong, This greatly reduces the robustness. In addition, the ECB mode also has the problem of not resisting statistical analysis.

- What is the Nonce marker in the upper left corner for?

  The Nonce in CTR mode cannot be reused, otherwise the plaintext will be leaked. Therefore, the program randomly generates a different Nonce for each frame of image during encryption, and marks this in the upper left corner of the encrypted image. When decrypting, first analyze the marker to get the Nonce, and then decrypt according to it and the user key.

- Why not just encrypt each pixel at the resolution of the input video, but reduce the video resolution first?
  
  This is also because the video is compressed when it is transferred (and saved). If I directly encrypt the 4k video you input, every pixel of the encrypted video will be very blurry after streaming, and the effect after decryption will be terrible, and reducing the resolution to 320x180 is equivalent to increasing The amount of redundant information is reduced, so as to avoid losing too much effective information during transmission.
  
- What if the decrypted image is in chaos?

  If the decrypted image is not clear enough, try different -S argument (the aspect ratio should be consistent with the client's screen ratio and the original video ratio). If the decrypted image cannot identify anything at all, first check whether the -S, -l and -k arguments selected by the server and the client are the same, and then make sure that the client video is full screen (no black border), and the Nonce marker in the upper left corner is not blocked by other windows.
