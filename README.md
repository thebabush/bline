# bline

Collection of things you might find useful when doing security assessment of
[Naver LINE](https://line.me).
This is mostly related to the App's voice call stack, which was based on a
modified version of [PJSIP](https://www.pjsip.org/) at the time.
It has since been rewritten (thank God), so YMMV.

This was created in 2018 as you can see from
[this page :)](https://bugbounty.linecorp.com/en/halloffame/2018/)
(even though I ended up not using the content of this repo).

In my tests, the SIP data exchanged between my phone and LINE's servers wasn't
encrypted, but just used a modified ZLIB version with custom dictionary.
There was support for encryption in the voice call library (`libamp.so`), but
I didn't reverse enough of it to understand how it is used.

## List of goodies

- `bline/`: a library for compressing/decompressing the custom ZLIB that LINE
  uses
- `data/heartbeat.ksy`: Kaitai Struct definition of LINE's heartbeat protocol
- `scripts/bline`: pipe binary data in and compresses/decompresses it

I also have more scripts but I can't shared them at the moment since they have
personal information copy-pasted in them.
For example, I have a script that does MITM of voice calls and can dump the
packets in a `tshark`-like fashion (even though I didn't have time to understand
the payload format for audio data).

Ping [@pmontesel](https://twitter.com/pmontesel) on twitter if you want to have
a chat about what I know.

## Author

[babush](https://thebabush.github.io/).

## License

See [LICENSE](./LICENSE).

