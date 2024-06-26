MODIS_VARIABLES = {
        "EV_250_Aggr1km_RefSB": [1,2],
        "EV_500_Aggr1km_RefSB":[3,4,5,6,7],
        "EV_1KM_RefSB": [8,9,10,11,12,"13lo","13hi","14lo","14hi",15,16,17,18,19,26],
        "EV_1KM_Emissive": [20,21,22,23,24,25,27,28,29,30,31,32,33,34,35,36],
}



def get_modis_channel_numbers():
    channels = [str(i) for i in range(1, 39)]
    channels[12] = '13lo'
    channels[13] = '14lo'
    channels[36] = '13hi'
    channels[37] = '14hi'
    return channels
