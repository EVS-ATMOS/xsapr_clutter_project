import gc
import numpy as np
import pyart


def xsapr_clutter(files, out_file, clutter_threshold=0.0002,
                  radius=1):
    """
    X-SAPR Wind Farm Clutter Calculation
    
    Parameters
    ----------
    files : list
        List of radar files used for X-SAPR clutter calculation.
    out_file : string
        File path and name for where new radar object will be
        written to.

    Other Parameters
    ----------------
    clutter_threshold : float
        Threshold value for which, values obtained from
        the radars reflectivity standard deviations divided by the
        means, if any of these values are below the threshold,
        they will be considered clutter.
    radius : int
        Radius of the area surrounding the clutter gate that will
        be also flagged as clutter.

    Returns
    -------
    clutter_radar : Radar
        Radar object with the clutter field that was calculated.
        This radar only has the clutter field, but maintains all
        other radar specifications.

    """

    run_stats = RunningStats()
    for file in files:
        radar = pyart.io.read(file)
        if radar.fields[
            'reflectivity']['data'].shape == (9200, 501):
            reflect_array = (radar.fields['reflectivity']['data'])
        else:
            print(str(file), ' skipped',
                radar.fields['reflectivity']['data'].shape)
        del radar
        gc.collect()
        run_stats.push(reflect_array)
    mean = run_stats.mean()
    stdev = run_stats.standard_deviation()
    #new_means = expit(mean / 1000)
    clutter_values = stdev / mean
    clutter_array = _clutter_calculation(clutter_values,
                                         clutter_threshold,
                                         radius)
    clutter_radar = pyart.io.read(files[0])
    clutter_radar.fields.clear()
    clutter_dict = _clutter_to_dict(clutter_array)
    clutter_radar.add_field('xsapr_clutter', clutter_dict,
                            replace_existing=True)
    pyart.io.write_cfradial(out_file, clutter_radar)
    return clutter_radar


def _clutter_calculation(clutter_values, clutter_threshold,
                         radius):
    """ Takes clutter_values(stdev/mean)and the clutter_threshold
    and calculates where X-SAPR wind farm clutter is occurring at
    the SGP ARM site. """
    is_clutters = np.argwhere(clutter_values > clutter_threshold)
    shape = clutter_values.shape
    mask = np.ma.getmask(clutter_values)
    temp_array = np.zeros(shape)
    temp_array = np.pad(temp_array, radius,
                        mode='constant', constant_values=-999)
    is_clutters = is_clutters + radius
    x_val, y_val = np.ogrid[-radius:(radius + 1),
                            -radius:(radius + 1)]
    circle = (x_val * x_val) + (y_val * y_val) <= (radius * radius)
    for is_clutter in is_clutters:
        ray, gate = is_clutter[0], is_clutter[1]
        frame = temp_array[ray - radius:ray + radius + 1,
                           gate - radius:gate + radius + 1]
        temp_array[ray - radius:ray + radius + 1,
                   gate - radius:gate + radius + 1] = np.logical_or(
            frame, circle)
    temp_array = temp_array[radius:shape[0] + radius,
                            radius:shape[1] + radius]
    clutter_array = np.ma.array(temp_array, mask=mask)
    return clutter_array


def _clutter_to_dict(clutter_array):
    """ Function that takes the clutter array
    and turn it into a dictionary to be used and added
    to the pyart radar object. """
    clutter_dict = {}
    clutter_dict['units'] = 'unitless'
    clutter_dict['data'] = clutter_array
    clutter_dict['standard_name'] = 'xsapr_clutter'
    clutter_dict['long_name'] = 'X-SAPR Clutter'
    clutter_dict['notes'] = '0: No Clutter, 1: Clutter'
    return clutter_dict


class RunningStats:
    """ Calculated Mean, Variance and Standard Deviation, but
    uses the Welford algorithm to save memory. """
    def __init__(self):
        self.n = 0
        self.old_m = 0
        self.new_m = 0
        self.old_s = 0
        self.new_s = 0

    def clear(self):
        self.n = 0

    def push(self, x):
        self.n += 1

        if self.n == 1:
            self.old_m = self.new_m = x
            self.old_s = 0
        else:
            self.new_m = self.old_m + (x - self.old_m) / self.n
            self.new_s = self.old_s + (x - self.old_m) * (x - self.new_m)

            self.old_m = self.new_m
            self.old_s = self.new_s

    def mean(self):
        return self.new_m if self.n else 0.0

    def variance(self):
        return self.new_s / (self.n - 1) if self.n > 1 else 0.0

    def standard_deviation(self):
        return np.sqrt(self.variance())
