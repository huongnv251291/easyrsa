import os
from os.path import exists

if __name__ == "__main__":
    listIp = {}
    # listStreamCountry = {}
    listValueIspCountryForCheck = {}
    listValueIspCountryForWrite = {}
    ispInfor = {}
    logFile = open('E://huong//logTest//ipError.log', 'r', encoding="utf-8")
    for line in logFile:
        values = line.split(',')
        if len(values) == 8:

            # streamCountry = None
            listIsp = None
            country = str(values[1]).strip()
            if country in listValueIspCountryForCheck:
                # streamCountry = listStreamCountry[values[1]]
                listIsp = listValueIspCountryForCheck[country]
            else:
                # streamCountry = open('E://huong//logTest//' + values[1], 'w', buffering=1, encoding="utf-8")
                listIsp = []
            isp = values[6].strip()
            listIsp.append(isp)
            listValueIspCountryForCheck[country] = listIsp
            count = listIsp.count(isp)
            ispInfor[isp + country] = values[6] + ',' + values[5] + ',' + values[4] + ', ' + str(count)
            listRealIsp = None
            if country in listValueIspCountryForWrite:
                listRealIsp = listValueIspCountryForWrite[country]
            else:
                listRealIsp = []
            if listRealIsp.count(isp) <= 0:
                listRealIsp.append(isp)
            listValueIspCountryForWrite[country] = listRealIsp
    keys = listValueIspCountryForWrite.keys()
    hashMapStream = {}
    file_exists = exists('E://huong//logTest//country')
    if file_exists:
        os.remove('F//logTest//country')
    os.mkdir('E://huong//logTest//country')
    for country in keys:
        stream = None
        extnetion = None
        listIsp = listValueIspCountryForWrite[country]
        if len(listValueIspCountryForCheck[country]) <= 80:
            continue
        if country in hashMapStream:
            stream = hashMapStream[country]
        else:
            stream = open('E://huong//logTest//country//' + country + '.csv', 'w', buffering=1, encoding="utf-8")
            stream.write('COUNTRY,TOTAL_CONNECT_FAIL,TOTAL_ISP')
            stream.write(
                '\n' + country + ', ' + str(len(listValueIspCountryForCheck[country])) + ', ' + str(len(listIsp)))
            # ispInfor[isp] = values[6] + ',' + values[5] + ',' + values[4] + ', ' + str(count)
            stream.write('\n---------------------------------------------------------------------------------------')
            stream.write('\nISP,AS,ORG,COUNT')
            stream.flush()
            hashMapStream[country] = stream
        for isp in listIsp:
            stream.write('\n' + ispInfor[isp + country].strip())
            stream.flush()
