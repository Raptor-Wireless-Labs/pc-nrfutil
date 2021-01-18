## Instructions for this tool specific to Raptor/Midland project use


**Note** this tool seems to work best with Python 3.6, and has issue with python 3.8 

### Package for 832 devices

To create a zip file usable for 832 device, (earbud and repeater-832)

`./nordicsemi/__main__.py pkg generate --hw-version {hw version}
--sd-req 0x00 --application-version {sw version} --application {path to app hex} --key-file
../../assets/midland_fw.key {output zip file}`


Where:

{hw version} (integer): the hardware revision that this build is intended for. 

{sw version} {integer}: the software version of this build. 

{path to app hex}: the relative path to the hex file output from the compiler.

{output zip file}: the path where the dfu package should be saved.
### Package for 840 devices

[TBD]

### Programming an 832 device via pc

For development, you can program the device over USB serial with the command

`./nordicsemi/__main__.py dfu serial -pkg {path to packge zip} --port {pc serial port name}`


Where:

{path to packge zip}: The zip file created by the package process

{pc serial port name}: the name of the port on the pc. For example:

`./nordicsemi/__main__.py dfu serial -pkg ./erbd_v25.zip --port com6`

on Windows

