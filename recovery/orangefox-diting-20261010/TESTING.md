# Recovery candidate test checklist

The first candidate must pass actual phone tests before being advertised as an installation
method. It targets the project's Android 16 AviumUI ROM, with matching boot/vendor_boot.
Keep the original Recovery from the exact installed ROM available as a fallback.

Connect only the intended diting / ditingp phone. From bootloader FASTBOOT, verify the
candidate image hash against its delivery manifest, then use:

```text
fastboot flash recovery recovery.img
fastboot reboot recovery
```

This image has no standalone kernel; use the recovery partition rather than `fastboot boot`.
Do not change boot, vendor_boot or vbmeta for this first Recovery-only test.

Record separately for Xiaomi 12T Pro and Redmi K50 Ultra:

1. Does the main menu appear and stay open without a repeating Fox logo?
2. Do touch, buttons, brightness and battery display work?
3. Does the correct lockscreen credential unlock storage, with readable filenames?
4. Are ADB and file transfer available?
5. Can it reboot back to the installed system?
6. After the above pass, does installation of the full matching ROM ZIP succeed with
   signature verification enabled? Save the exact result and Recovery log.
7. Does fastbootd work, and can the device return to Recovery and the system?

If storage decryption fails, report the message before considering a data format.
The candidate's compilation and static checks do not prove decryption works.
Installing a full ROM OTA may restore that ROM's bundled Avium Recovery.

If the Fox logo repeats, capture `/tmp/recovery.log`, logcat and dmesg while ADB is available.
Redact identifiers and personal data before posting logs. Return to FASTBOOT using the
power and volume-down buttons and restore the matching original Recovery:

```text
fastboot flash recovery Avium-recovery-fallback.img
fastboot reboot
```

Root configuration, cellular data and roaming do not need to change for these tests.
