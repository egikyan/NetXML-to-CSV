#!/usr/bin/python
from lxml import etree
import os
import sys

def run():


    if len(sys.argv) != 3:
        print "[*] Usage: %s input output" % sys.argv[0]
    else:
        output_file_name = sys.argv[2]
        input_file_name = sys.argv[1]
        if input_file_name != output_file_name:
            try:
                output = file(output_file_name, 'w')
            except:
                print "[-] Unable to create output file '%s' for writing." % output_file_name
                exit()

            try:
                doc = etree.parse(input_file_name)
            except:
                print "[-] Unable to open input file: '%s'." % input_file_name
                exit()

            print "[+] Parsing '%s'." % input_file_name
            sys.stdout.write("[+] Outputting to '%s' " % output_file_name)
            output.write("BSSID,Channel,Encryptionfull,WPAversion,Auth,Power,ESSID,Lat,Lon,Type,MaxRate,IsHidden,WPS,manuf_short, wps_manuf, dev_name, model_name, model_num, last_signal_dbm, min_signal_dbm, max_signal_dbm\n")
            # result, clients = parse_net_xml(doc)
            result = parse_net_xml(doc)
            output.write(result)
            sys.stdout.write(" Complete.\r\n")

def parse_net_xml(doc):
    result = ""

    # Show progress
    total = len(list(doc.getiterator("wireless-network")))
    tenth = total/10
    count = 0   

    for network in doc.getiterator("wireless-network"):
        count += 1
        if (count % tenth) == 0:
            sys.stdout.write(".")
        type = network.attrib["type"]
        channel = network.find('channel').text
        bssid = network.find('BSSID').text

        encryption = network.getiterator('encryption')

        auth = ""
        if encryption is not None:
            for item in encryption:
                if item.text.startswith("WEP"):
                    auth = ""
                    break
                elif item.text.startswith("WPA"):
                    if item.text.endswith("PSK"):
                        auth = "PSK"


        power = network.find('snr-info')
        dbm = ""
        if power is not None:
            dbm = power.find('max_signal_dbm').text

        if int(dbm) > 1:
            dbm = power.find('last_signal_dbm').text

        if int(dbm) > 1:
            dbm = power.find('min_signal_dbm').text

        ssid = network.find('SSID')

        essid_text = ""
        maxrate = ""
        wps = ""
        wpaversion = ""
        stationtype = ""
        encodings = ""
        encodings_temp = " "
        network_hidden = ""

        wps_status = ""
        wps_manuf = ""
        model_name = ""
        model_num = "" 
        dev_name = ""

        manuf_short = ""

        manuf_short = network.find('manuf').text
 

        if ssid is not None:
            essid_text = ssid.find('essid').text
            maxrate = ssid.find('max-rate').text
            wps = ssid.find('wps').text
            stationtype = ssid.find('type').text

            if network.find('SSID').findtext('wps-manuf') is not None:
                wps_manuf = network.find('SSID').findtext('wps-manuf')
                wps_manuf = wps_manuf.replace(',', '')
                # print wps_manuf
            if ssid.findtext('model-name')  is not None:
                model_name = ssid.findtext('model-name')
                # print model_name
            if ssid.findtext('wps')  is not None:
                wps_status= ssid.findtext('wps')
                # print model_name
            if ssid.findtext('model-num')  is not None:
                model_num = ssid.findtext('model-num')
                # print model_num
            if ssid.findtext('dev-name')  is not None:
                dev_name = ssid.findtext('dev-name')       
                # print dev_name

            wpaversion = ssid.findtext('wpa-version')

            if wpaversion is None:
                wpaversion = ""

            # Find all supported encodings

            num_of_encodings_found = len(ssid.findall('encryption'))

            i = 0

            while i < num_of_encodings_found :
                num_of_encodings_found -= 1
                encodings_temp = ssid.findall('encryption')[num_of_encodings_found].text
                encodings = encodings + encodings_temp
                # add space if needed
                if num_of_encodings_found >= 1:
                    encodings = encodings + " "

            # Find if network SSID is hidden
            for cloaked in network.iter('SSID'):
                for cloaked in network.iter('essid'):
                    network_hidden = cloaked.attrib['cloaked']


        # Find information on signal strentght
        last_signal_dbm = ""
        min_signal_dbm = ""
        max_signal_dbm = ""

        signals = ['last_signal_dbm', 'min_signal_dbm', 'max_signal_dbm']


        for signal in signals:
            if signal is not None:
                value = power.find(signal).text
                # print "Start        " + essid_text
                # # print signal
                # print value + "\n END _------------"

                if signal is 'last_signal_dbm':
                    last_signal_dbm = value
                if signal is 'min_signal_dbm':
                    min_signal_dbm = value
                if signal is 'max_signal_dbm':
                    max_signal_dbm = value

        gps = network.find('gps-info')
        lat, lon = '', ''
        if gps is not None:
            lat = network.find('gps-info').find('avg-lat').text
            lon = network.find('gps-info').find('avg-lon').text

        result += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\n" % (bssid, channel, encodings, wpaversion, auth, dbm, essid_text, lat, lon, type, maxrate,network_hidden,wps, manuf_short, wps_manuf, dev_name, model_name, model_num, last_signal_dbm, min_signal_dbm, max_signal_dbm)

        # c_list = associatedClients(network, bssid, essid_text)
        # if c_list is not None:
        #     clients.append(c_list)
    print count
    return result 
        
        

    #, clients

# def associatedClients(network, bssid, essid_text):
#     clients = network.getiterator('wireless-client')

#     if clients is not None:
#         client_info = list()
#         for client in clients:
#             mac = client.find('client-mac')
#             if mac is not None:
#                 client_mac = mac.text
#                 snr = client.find('snr-info')
#                 if snr is not None:
#                     power = client.find('snr-info').find('max_signal_dbm')
#                     if power is not None:
#                         client_power = power.text
#                         c = client_mac, client_power, bssid, essid_text
#                         client_info.append(c)

#         return client_info

if __name__ == "__main__":
      run()
