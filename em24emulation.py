'''
   Copyright 2024 Astirfreak
   
   Licensed under the GNU GENERAL PUBLIC LICENSE, Version 3 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       https://www.gnu.org/licenses/gpl-3.0.html

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

from pyModbusTCP.server import ModbusServer, DataBank
import time

# values you like to publish, need to get filled somehow
phase_voltages = [230.0, 230.0, 230.0]  # Volt 
phase_currents = [0.0, 0.0, 0.0]        # Ampere 
phase_powers = [0.0, 0.0, 0.0]          # Watt
total_power = [0.0]                     # Watt

# converts python-numbers into two 16 bit words for the Modbus-registers
def Words(value):
    value = int(value)
    lower_16 = value & 0xFFFF
    upper_16 = (value >> 16) & 0xFFFF

    if value < 0:        
        lower_16 = lower_16 - 0x10000 if lower_16 > 0x7FFF else lower_16
        upper_16 = upper_16 - 0x10000 if upper_16 > 0x7FFF else upper_16
    return [lower_16,upper_16]

# customized data bank to catch special Carlo Gavazzi identification request
class CustomDataBank(DataBank):
    def get_holding_registers(self, address, number, srv_info):
        if address==0x000B and number==1:
            return [0x0675] # identification as Carlo Gavazzi counter
        return super().get_holding_registers(address, number, srv_info)

# create Modbus TCP server
server = ModbusServer(host="0.0.0.0", port=502, no_block=True, data_bank=CustomDataBank())

try:
    print("starting Modbus-Server...")
    server.start()

    print("Modbus-Server running. Press Ctrl+C to terminate.")
    while True:
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx    
        # xx  get and fill your data here  xx
        # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 
        # and publish them afterwards:
        # see em24 ethernet cp.pdf for further register adresses
        server.data_bank.set_holding_registers(0x00, Words(phase_voltages[0]*10))   # voltage L1
        server.data_bank.set_holding_registers(0x02, Words(phase_voltages[1]*10))   # voltage L2
        server.data_bank.set_holding_registers(0x04, Words(phase_voltages[2]*10))   # voltage L3
        server.data_bank.set_holding_registers(0x0C, Words(phase_currents[0]*1000)) # current L1
        server.data_bank.set_holding_registers(0x0E, Words(phase_currents[1]*1000)) # current L2
        server.data_bank.set_holding_registers(0x10, Words(phase_currents[2]*1000)) # current L3
        server.data_bank.set_holding_registers(0x12, Words(phase_powers[0]*10))     # power L1
        server.data_bank.set_holding_registers(0x14, Words(phase_powers[1]*10))     # power L2
        server.data_bank.set_holding_registers(0x16, Words(phase_powers[2]*10))     # power L3
        server.data_bank.set_holding_registers(0x28, Words(total_power*10))         # totalPower
        
        time.sleep(0.1)
        pass  # server is running until stopped manualy

except KeyboardInterrupt:
    print("terminating Modbus-Server ...")
    server.stop()
    print("Modbus-Server terminated.")
