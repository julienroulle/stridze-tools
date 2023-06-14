import numpy as np


def smooth_fn(x, window_len, window='blackman'):
    """smooth function

    :param x: parameter of the function
    :type x: array
    :param window_len: window length
    :type window_len: int
    :param window: boundary to calculate
    :type window: array
    :raises ValueError: if numbers are outside of expected boundary
    :raises ValueError: if numbers are outside of expected boundary
    :return: result
    :rtype: array
    """
    x = np.asanyarray(x)

    if x.ndim != 1:
        raise ValueError

    if x.size < window_len:
        return x

    if window_len < 3:
        return x

    if window not in ["flat", "hanning", "hamming", "bartlett", "blackman"]:
        raise ValueError

    s = np.r_[x[window_len - 1 : 0 : -1], x, x[-2 : -window_len - 1 : -1]]
    if window == "flat":
        w = np.ones(window_len, "d")
    else:
        w = eval("np." + window + "(window_len)")

    y = np.convolve(w / w.sum(), s, mode="valid")

    return y[(window_len//2-1):-(window_len//2)]

def str_time_to_num_time(time):
    """Convert a string time (e.g. 1:36:50) to seconds."""
    
    # If time is --, then no time found
    if time == '--':
        return -1
    
    # Split time into hours, minutes, seconds
    time_parts = str(time).split(':')
    
    # Store each time part as a float number
    hours = float(time_parts[-3]) if len(time_parts) > 2 else 0
    mins = float(time_parts[-2]) if len(time_parts) > 1 else 0
    secs = float(time_parts[-1])
    
    # Calculate seconds and return
    return (3600*hours) + (60*mins) + secs

def num_time_to_str_time(time, dp=2):
    time = round(time)
    """Convert a number of seconds to a string time (e.g. 1:36:50)."""
    str_time = ''
    str_hour = ''
    str_mins = ''
    str_secs = ''
    
    # Get number of whole hours
    hours = int(time // 3600)
    # Add to string time
    if hours > 0:
        str_time += str(hours)
        str_hour = str(hours)
    # Remove hours from time, for minutes calculation
    time -= hours * 3600
    
    # Get number of whole minutes
    mins = int(time // 60)
    # Add to string time
    if (mins > 0) or (len(str_time) > 0):
        if len(str_time) > 0:
            str_time += ':'
            if mins < 10:
                str_time += '0'
                str_mins += '0'
        str_time += str(mins)
        str_mins += str(mins)
    # Remove minutes from time, for seconds calculation
    time -= mins * 60
    # Deal with 60 edge case
    if str_mins == '60':
        str_hour = str(int(str_hour) + 1)
        str_mins = '00'
    
    # Get number of seconds to 2 dp (or input dp)
    secs = round(time, dp)
    # Add to string time
    if (secs > 0) or (len(str_time) > 0):
        if len(str_time) > 0:
            str_time += ':'
            if secs < 10:
                str_time += '0'
                str_secs += '0'
        str_time += str(secs) if str(secs)[-2:] != '.0' else str(secs)[:-2]
        str_secs += str(secs) if str(secs)[-2:] != '.0' else str(secs)[:-2]
    # Deal with 60 edge case
    if str_secs == '60':
        str_mins = ('0' if (mins < 9) and (hours > 0) else '') + str(mins+1)
        str_secs = '00'
        
    # Return string time
    return str_hour + (':' if hours>1 else '') + str_mins + (':' if mins>1 else '') + str_secs