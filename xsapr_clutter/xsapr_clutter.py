import numpy as np
import pyart


def xsapr_clutter(files, clutter_thres_min=0.0002,
                  clutter_thres_max=1.5, radius=1,
                  write_radar=False, out_file=None):
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
    clutter_thres_min : float
        Threshold value for which, any clutter values above the
        clutter_thres_min will be considered clutter, as long as they
        are also below the clutter_thres_max.
    clutter_thres_max : float
        Threshold value for which, any clutter values below the
        clutter_thres_max will be considered clutter, as long as they
        are also above the clutter_thres_min.
    radius : int
        Radius of the area surrounding the clutter gate that will
        be also flagged as clutter.
    write_radar : bool
        Whether to or not, to write the clutter radar as a netCDF file.
        Default is False.
    out_file : string
        String of location and filename to write the radar object too,
        if write_radar is True.

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
        run_stats.push(reflect_array)
    mean = run_stats.mean()
    stdev = run_stats.standard_deviation()
    # new_means = expit(mean / 1000)
    clutter_values = stdev / mean
    clutter_array = _clutter_calculation(clutter_values,
                                         clutter_thres_min,
                                         clutter_thres_max,
                                         radius)
    clutter_radar = pyart.io.read(files[0])
    clutter_radar.fields.clear()
    clutter_dict = _clutter_to_dict(clutter_array)
    clutter_radar.add_field('xsapr_clutter', clutter_dict,
                            replace_existing=True)
    if write_radar is True:
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


# Adapted from http://stackoverflow.com/a/17637351/6392167
class RunningStats():

    def __init__(self):
        self.n = 0
        self.old_m = 0
        self.new_m = 0
        self.old_s = 0
        self.new_s = 0

    def clear(self):
        self.n = 0

    def push(self, x):
        shape = x.shape
        ones_arr = np.ones(shape)
        mask = np.ma.getmask(x)
        mask_ones = np.ma.array(ones_arr, mask=mask)
        add_arr = np.ma.filled(mask_ones, fill_value=0.0)
        self.n += add_arr
        mask_n = np.ma.array(self.n, mask=mask)
        fill_n = np.ma.filled(mask_n, fill_value=1.0)

        if self.n.max() == 1.0:
            self.old_m = self.new_m = np.ma.filled(x, 0.0)
            self.old_s = np.zeros(shape)
        else:
            self.new_m = np.nansum(np.dstack(
                (self.old_m, (x-self.old_m) / fill_n)), 2)
            self.new_s = np.nansum(np.dstack(
                (self.old_s, (x-self.old_m) * (x-self.new_m))), 2)

            self.old_m = self.new_m
            self.old_s = self.new_s

    def mean(self):
        return self.new_m if np.any(self.n) else 0.0

    def variance(self):
        return self.new_s / (self.n-1) if (self.n.max() > 1.0) else 0.0

    def standard_deviation(self):
        return np.sqrt(self.variance())
