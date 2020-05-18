from decimal import *
import numpy as np
import math
class data_reduction:
    def __init__(self,sn,copc):
        self.data_reduction_version = 1.3
        self.data = []
        self.segments = []
        self.tolerance = Decimal('.1')
        self.site_name = sn
        self.copc = copc
        #noise per Mart Oostrom and Ryan Nell
        self.noise = Decimal('.000000000001')
        self.jump = Decimal('.25')
        self.min_step = Decimal(0)
        self.max_step = Decimal(365250)
        self.day_unit = False
        self.time = []
        self.flux = []
#    def insert_data(self,rec):
#        self.data.append(rec)
    def set_min_step(self, ms, day_unit):
        self.min_step = Decimal(ms)
        self.day_unit = day_unit
    def set_max_step(self, ms, day_unit):
        self.max_step = Decimal(ms)
        self.day_unit = day_unit
    def set_logger(self,log):
        self.logger = log
    #---------------------------------------------------------------------------
    #
    def build_numpy_arrs(self):
        x = []
        y = []
        for rec in self.data:
            x.append(rec[0])
            y.append(rec[1])
        self.time  = np.array(x)
        self.flux = np.array(y)
    #---------------------------------------------------------------------------
    # consolidate concurrent zero fluxes
    def consolidate_zero_flux(self,b_ind,e_ind):
        end = b_ind
        for i in range(b_ind,e_ind):
            if self.data[i+1][1] > 0 or i + 1 == e_ind:
                end = i
                break

        return end
    #---------------------------------------------------------------------------
    # Average groups of fluxes that are considered noise
    def avg_noise(self,b_ind, e_ind):
        end = b_ind +1
        seg_flux = self.data[end][1]
        tot_cum = Decimal(0.0)
        for i in range(b_ind+1, e_ind):

            p_data = self.data[i - 1]
            c_data = self.data[i]
            n_data = self.data[i + 1]
            #while flux is < noise add to total cumulative
            if c_data[1] < self.noise:
                tot_cum += c_data[1] * (c_data[0] - p_data[0])
                end = i
            #if next flux is > noise or == 0 then this is the last flux
            #  to be filtered.
            if n_data[1] > self.noise or n_data[1] <= 0:
                break


        if end > b_ind+1:
            seg_flux = tot_cum / (self.data[end][0] - self.data[b_ind][0])
        return seg_flux,end
    #---------------------------------------------------------------------------
    #broken
    def find_flat_line(self, b_ind, e_ind):

        t_cum = 0
        end = b_ind+1
        segs = self.data[b_ind+1]
        tol = Decimal(".01")
        for i in range (b_ind+2, e_ind):

            t_cum += self.data[i][1] * (self.data[i][0] - self.data[i-1][0])
            seg_flux = t_cum / (self.data[i][0] - self.data[b_ind][0])
            seg_cum = self.data[i][1] * (self.data[i][0] - self.data[b_ind][0])
            segs = [self.data[i][0], seg_flux]
            end = i
            if self.check_tolerance(seg_cum,t_cum, tol):
                #check if the flux is thin 1.5X the tolerance
                if self.check_tolerance(seg_flux,self.data[i][1], tol*Decimal(1.5)):
                    break
            #if next record exceeds 2% difference in flux the exit loop
            if abs(self.diff_arr[i+1][3] * self.data[i][1]) > .01:
                #self.logger.debug("End of flat line:  {0}   {1}"
                #           .format(self.data[i][0],self.data[i][1]))
                break
            else:
                prev = self.data[self.point_arr[-1]]
                cur = self.data[i]
                time_d = cur[0] - prev[0]
                flux_d = cur[1] - prev[1]
                diff = flux_d / time_d
                perc_d = abs(diff * cur[1])
                #if the difference between the first record and cur exceeds
                # 10% then break the loop.
                if perc_d > .1:
                    #self.logger.debug("Flat line exceeded 10% total differance :  {0}   {1}"
                    #           .format(self.data[i][0],self.data[i][1]))
                    break
        return segs, end
    #---------------------------------------------------------------------------
    #
    def check_tolerance(self,new,old, tol):
        diff = old * tol
        u_limit = old + diff
        l_limit = old - diff

        if u_limit >= new >= l_limit:
            return True
        else:
            return False
    #---------------------------------------------------------------------------
    #
    def reduce_segment(self,b_ind, e_ind):
        getcontext().prec = 28
        segs = self.data[b_ind+1]
        start = b_ind
        reason = 'Single step exceeds tolerance for flux or Cumulative.'
        end = start +1
        t_cum = Decimal(0.0)
        # setup tolerance reduction reduce the tolerance the closer you are to an end point
        tol = self.tolerance
        override = False
        #if e_ind - b_ind > 12:
        #    tol_step_1 = seg_time / 4
        #    tol_step_2 = seg_time / 6
        #    tol_step_3 = seg_time / 8
        for i in range(b_ind+1, e_ind):

            # total cumuluative is flux * (cur date - prev date)
            t_cum += self.data[i][1] * (self.data[i][0] - self.data[i-1][0])

            # so long as seg_flux does not exceep tolerance replace previous value
            #if self.check_tolerance(seg_flux,self.data[i][1]):
            # new total cumulative = cur concentration * (cur_data - first date of segment)

            time = self.data[i][0] - self.data[b_ind][0]
            #if self.check_tolerance(self.data[i][1] * time,t_cum, tol):
                # segment_flux = t_cum / (cur_date - first date of seg)
            seg_flux = t_cum / time
            #if this is the last flux before a zero flux or flux dips into noise then
            #record it.
            if self.data[i+1][1] <= 0 or self.data[i+1][1] < self.noise:
                reason = 'Last step before 0 or noise for flux.'
                end = i
                override = True
                break
            elif self.check_for_jumps(i+1,i):
                reason = 'Next step is a spike in the flux.'
                end = i
                override = True
                break
            #check if the flux is thin 10% the tolerance
            #if self.check_tolerance(seg_flux,self.data[i][1], tol*Decimal(1)):
            elif self.check_tolerance(seg_flux,self.data[i][1], tol) == False:
                reason = 'Next step flux will exceed 10% tolerance.'
                end = i-1
                break
            elif self.check_tolerance(self.data[i][1] * time,t_cum, tol) == False:
                reason = 'Next step Cumulative flux will exceed 10% tolerance.'
                end = i-1
                break
            elif self.data[i][1] < self.noise:
                end = i
                break

        if (self.data[end][0] - self.data[b_ind][0]) < self.min_step and override == False:
            end = b_ind + int(self.min_step / Decimal('365.25'))
        elif (self.data[end][0] - self.data[b_ind][0]) > self.max_step:
            end = b_ind + int(self.max_step / Decimal('365.25'))
        if end > e_ind:
            end = e_ind

        t_cum = 0

        for i in range(b_ind+1, end+1):
            t_cum += Decimal(self.data[i][1] * (self.data[i][0] - self.data[i-1][0]))
        seg_flux = t_cum / (self.data[end][0] - self.data[b_ind][0])
        segs = [self.data[end][0],seg_flux]
        #self.logger.info("year {0} to {1}, original flux: {2};  new: {3} / {4} = {5}; reason: {6}"
        #           .format(self.data[b_ind][0], self.data[end][0],
        #                   self.data[end][1], t_cum, (self.data[end][0] - self.data[b_ind][0]),seg_flux, reason))
        return segs,end
    #---------------------------------------------------------------------------
    #  check if difference between 2 values is greater than 25 %
    def check_for_jumps(self,cur, prev):
        #if this record is more than 25% greater than previous return true
        max = (self.data[prev][1] + (self.data[prev][1] * self.jump))
        min = (self.data[prev][1] - (self.data[prev][1] * self.jump))
        if   self.data[cur][1] > max:
        #    self.logger.debug("    year: {0};  Flux changed by more than {1}: val{2} > {3}({4}+({4}*{1}))"
        #               .format(self.data[cur][0],self.jump,self.data[cur][1],max,self.data[prev][1]))
            return True
        #if this record is more than 25% less than previos return True
        elif self.data[cur][1] < min:
        #    self.logger.debug("    year: {0};  Flux changed by more than {1}: val{2} < {3}({4}-({4}*{1}))"
        #               .format(self.data[cur][0],self.jump,self.data[cur][1],max,self.data[prev][1]))
            return True
        else:
            return False
    #---------------------------------------------------------------------------
    #
    def refine_seg(self, b_ind, e_ind):
        segs = []
        #b_ind has already been inserted it is used to calculate the time from
        # as flux is applied to the previous years
        start = b_ind
        seg_flux = 0
        seg_smear = int(math.ceil((e_ind-b_ind)*.1))
        if seg_smear > 50:
            seg_smear = 50
        #self.logger.info("peak/valley smear = {0}".format(seg_smear))
        #self.logger.info("processing full segment {0} - {1}".format(self.data[b_ind][0],self.data[e_ind][0]))
        for i in range(b_ind,e_ind):
            if start >= e_ind:
                break
            # capture the first and last 10% of points in a segments
            # This chould help define peaks and valley better.

            elif i > start:
        #        self.logger.debug("ind: {2};  processing partial segment {0} - {1}"
        #                   .format(self.data[start][0],self.data[e_ind][0], start))
                #process flux of 0

                if self.data[i][1] <= 0:
                    if self.data[i][1] < 0:
                        #handler = self.logger.handlers[0]
                        #filename = handler.baseFilename
                        print("ALERT: negative concentration found! converting to zero.  check Logs:{0}".format(filename))
        #                self.logger.critical("ALERT: negative concentration found! converting to zero starting at; year: {0}; concentration: {1}"
        #                            .format(self.data[i][0],self.data[i][1]))
                    t_end = self.consolidate_zero_flux(i,e_ind)
        #            self.logger.info("consolidating zero flux {0} - {1}"
        #                       .format(self.data[start][0],self.data[t_end][0]))

                    segs.append(self.data[t_end])
                    start = t_end
                #process flux in the noise range
                elif self.data[i][1] < self.noise:
                    seg_flux, t_end = self.avg_noise(start, e_ind-seg_smear)
        #            self.logger.info("  consolidating flux < {0}: {1} - {2}, new flux={3}"
        #                       .format(self.noise,self.data[start][0],self.data[t_end][0],seg_flux))
                    if t_end > start and seg_flux > 0:
        #                self.logger.info("   --new flux: {0}".format(seg_flux))
                        segs.append([self.data[t_end][0],seg_flux])
                        start = t_end
                elif i < (b_ind + seg_smear):
        #            self.logger.info("    year: {0};  flushing out peak/valleys by {0} years"
        #                       .format(seg_smear/365.25))
                    segs.append(self.data[i])
                    start = i
                elif i > (e_ind - seg_smear):
        #            self.logger.info("    year: {0};  flushing out peak/valleys by {0} years"
        #                       .format(seg_smear/365.25))
                    segs.append(self.data[i])
                    start = i
                #if this is first record after the last zero flux.
                # this recod is 25% greater or less than previous record
                # then record it.
                elif self.data[i-1][1] == 0:
        #            self.logger.debug("    year: {0};  First > 0 flux"
        #                       .format(self.data[i][0]))
                    segs.append(self.data[i])
                    start = i
                # this recod is 25% greater or less than previous record
                # then record it.
                elif self.check_for_jumps(i,i-1):
        #            self.logger.debug("    year: {0};  Flux changed by more than {1}"
        #                       .format(self.data[i][0],self.jump))

                    segs.append(self.data[i])
                    start = i
                #if data is effectively a flat line (diff between this and prev is less than 1%)
                # capture start and end points of it.
                #elif abs(self.diff_arr[i][3] * self.data[i][1]) < .01:
                #    t_segs, t_end = self.find_flat_line(start,e_ind)
                #    self.logger.info("    Flat line found: {0} - {1}"
                #               .format(self.data[start][0],t_segs[0]))
                #    segs.append(t_segs)
                #    start = t_end
                #reduce the segment to smaller segments that are within a given
                # tolerance
                else:
                    t_segs,t_end = self.reduce_segment(start, e_ind-seg_smear)
                    #if len(t_segs) > 0:
        #            self.logger.info("  segment within tolerance found: {0} - {1}"
        #                       .format(self.data[start][0],self.data[t_end][0]))
                    segs.append(t_segs)
                    #else:
                    #    t_end = start + 1
                    #    self.logger.info("single step as could not meet tolerance:  {0} - {1}".format(self.data[start][0],self.data[t_end][0]))
                    #    segs.append(self.data[t_end])
                    start = t_end
        segs.append(self.data[e_ind])
        return segs

    #---------------------------------------------------------------------------
    # find_difs for each time step:
    def find_difs(self):
        self.point_arr = []
        self.diff_arr = []
        d_len = len(self.data)

        for i in range (d_len):
            if i == 0:
                self.diff_arr.append([i,0,0,0])
            else:
                cur_data = self.data[i]
                prev_data = self.data[i-1]
                delta_t = cur_data[0] - prev_data[0]
                if delta_t != 0:
                    delta_f = cur_data[1] - prev_data[1]
                    dif = delta_f / delta_t
                    self.diff_arr.append([i,delta_t, delta_f, dif])
                else:
        #            self.logger.critical("no time passed between 2 points: {0}(index: {1}) and {2}(index: {3})"
        #                                .format(prev_data, i-1,cur_data,i))
                    self.diff_arr.append([i,delta_t,delta_f, 0])
        self.find_p_v_ind()
    #---------------------------------------------------------------------------
    # find single dif between two points
    def find_dif(self,cur_data,prev_data):
        delta_t = cur_data[0] - prev_data[0]
        delta_f = cur_data[1] - prev_data[1]
        dif = delta_f / delta_t
        return dif
    #---------------------------------------------------------------------------
    #
    def is_min_max_within_min_step(self,i):

        end_range = 0

        #if self.data[i][0] - self.data[self.point_arr[-1]][0] < self.min_step:
        self.logger.debug("-time between start ({0}) and end({1}) is under min_step {2}"
                    .format(self.data[self.point_arr[-1]][0],self.data[i][0],self.min_step))
        if abs(self.find_dif(self.data[i],self.data[self.point_arr[-1]])) >  self.tolerance:
            self.logger.info("--Allowed; concentration is greater than tolerance")
            return True
        if abs(self.diff_arr[i+1][3]) < Decimal('.01'):
            self.logger.info("--Skipped; differential between this step and next is below .01")
            return False
        else:
            if self.day_unit:
                end_range = int(self.min_step / Decimal(365.25)) + i
            else:
                end_range = int(self.min_step) + i
            if len(self.data) <= end_range:
                end_range = len(self.data) -1
            #Current Concentration
            c = self.data[i][1]
            for x in range(i,end_range):
                if ((self.data[x][1]-c) / c) < Decimal('.1'):
                    self.logger.debug("--skip point data does not increases or decreases outside of tolerance for several time periods.")
                    return False
                #find max one is found then cur record is not the max entry
                #if max and (c + (c * self.tolerance) < self.data[x][1]:
                #    return False
                #find the min, one is found hten cur record is not the min entry
                #elif not max and c > self.data[x][1]:
                #    return False
            self.logger.debug("--Allowed this is the highest peak within minimum steps")
        return True
    #---------------------------------------------------------------------------
    # find indexes to all peaks, valleys, and flat lines using self.noise as tolerance
    #   Peaks = max flux after a negative Differential or zero flux
    #   Valley = minumum flux after a positive Differential
    def find_p_v_ind(self):
        peak = 0
        valley = 0
        d_len = len(self.data)
        self.logger.info("building peaks and valleys from {0} time steps".format(d_len))
        for i in range(d_len):
            if i != self.diff_arr[i][0]:
                self.logger.critical("ERROR: self.data not aligned with self.diff_arr")
                raise
            # if it is the first record add it
            if i == 0:
                self.logger.info("first record: {0} ".format(self.data[i][0]))
                self.point_arr.append(i)
                valley = 0
                peak = 0
            # if it is the last record add it
            elif i == d_len -1:
                self.logger.info("last record: {0} ".format(self.data[i][0]))
                self.point_arr.append(i)
            elif self.data[i][1] <= 0:
                # if this is the last 0 add it as a point
                # this gives a time period for when the last zero in row happens
                if self.data[i+1][1] > 0:
                    self.logger.info("last zero found: {0} ".format(self.data[i][0]))
                    self.point_arr.append(i)
                    valley = 0
                    peak = 0

            elif self.noise > self.data[i][1] > 0:
                if self.data[i+1][1] == 0:
                    self.logger.info("end of noise prior to 0: {0} ".format(self.data[i][0]))
                    self.point_arr.append(i)
                    valley = 0
                    peak = 0
                elif self.data[i-1][1] == 0:
                    self.logger.info("noise found after last 0: {0} ".format(self.data[i][0]))
                    self.point_arr.append(i)
                    valley = 0
                    peak = 0
                elif self.data[i+1][1] > self.noise:
                    self.logger.info("last noise for segment: {0} ".format(self.data[i][0]))
                    self.point_arr.append(i)
                    valley = 0
                    peak = 0
            elif self.data[i][1] >= self.noise:

                #check difference if > 0 then it is building to peak
                if self.diff_arr[i][3] > 0:
                    #if time period < min_step then check if dif exceeds
                    #tolerance
                    if self.data[i][0] - self.data[self.point_arr[-1]][0] < self.min_step:
                        if self.is_min_max_within_min_step(i):
                            peak = i
                    else:
                        peak = i

                    # if vally > 0 then this is the first increment to Peaks
                    # so add the last valley as a point
                    if valley > 0 and peak > 0:
                        self.logger.info("is valley: {0}/{1}={2}"
                                   .format(self.diff_arr[valley][2],self.diff_arr[valley][1],self.diff_arr[valley][3]))
                        self.logger.info("adding valley: {0}   {1}"
                                   .format(self.data[valley][0],self.data[valley][1]))
                        self.point_arr.append(valley)
                        valley = 0

                #check difference if < 0 then it is falling to a valley
                elif self.diff_arr[i][3] < 0:
                    if self.data[i][0] - self.data[self.point_arr[-1]][0] < self.min_step:
                        if self.is_min_max_within_min_step(i):
                            valley = i
                    else:
                        valley = i
                    # if peak > 0 then this is the first increment to valley
                    # so add the last peak as a point
                    if peak > 0 and valley > 0:
                        self.logger.info("is peak: {0}/{1}={2}"
                                   .format(self.diff_arr[peak][2],self.diff_arr[peak][1],self.diff_arr[peak][3]))
                        self.logger.info("adding peak: {0}   {1}"
                                   .format(self.data[peak][0],self.data[peak][1]))
                        self.point_arr.append(peak)
                        peak = 0
                elif self.diff_arr[i][3] == 0:
                    if peak > 0:
                        peak = i
                    else:
                        valley = i
                elif i == d_len -1:
                    if peak > 0:
                        self.point_arr.append(peak)
                    else:
                        self.point_arr.append(valley)
                    self.point_arr.append(d_len-1)

    #---------------------------------------------------------------------------
    #
    def calc_cumulative(self, segs):
        prev = []
        cum = 0

        for i in range(len(segs)):
            cur = segs[i]
            if len(prev) > 0:
                cum += cur[1] * (cur[0]-prev[0])
            else:
                cum = cur[1]
            prev = cur
            segs[i].append(cum)
        self.logger.info("Cumulative over full time period: {0}".format(cum))
        return segs
    #--------------------------------------------------------------------------
    #
    def re_calc_segments(self,segs):
        self.logger.debug("before:{0}-{1} ({2})\n".format(self.iSource,self.jSource, len(self.data)))
        self.data.clear()
        self.logger.debug("cleared:{0}-{1} ({2})\n".format(self.iSource,self.jSource, len(self.data)))
        self.data = segs
        self.logger.debug("new:{0}-{1} ({2})\n".format(self.iSource,self.jSource, len(self.data)))
        return self.calc_segments()
        #return segs
    #--------------------------------------------------------------------------
    #
    def calc_segments(self):
        #if less than 1E-12 then consider it noise
        self.logger.debug(self.data)
        self.logger.info("-------------------------------------------------")
        self.logger.info("--------Define Peaks and Valleys in data---------")
        self.logger.info("---{0}-{1}".format(self.site_name,self.copc))
        self.find_difs()

        #step = int(self.max_step / Decimal('365.25'))
        #temp = np.arange(step,int(len(self.data))-step, step)
        #self.point_arr = np.concatenate((self.point_arr, temp))
        #self.point_arr.sort(kind='mergesort')
        #self.logger.info("valley and peak array:{0}".format(self.point_arr))
        #for i in self.point_arr:
        #    temp.append(self.data[i])
        #self.logger.info("valley and peak array:{0}".format(temp))

        seg_arr = []
        start = -1
        self.logger.info("number of peaks/valleys found({1},{2}): {0}".format(len(self.point_arr), self.site_name,self.copc))
        for i in self.point_arr:
            if i == 0:
                seg_arr.append(self.data[i])
            else:
                seg_arr.extend(self.refine_seg(start,i))
            start = i

        return self.calc_cumulative(seg_arr)
