using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using stomp_extrap_modflow.data;
namespace stomp_extrap_modflow.framework
{
    class interpolate_data
    {
        public Dictionary<string, SortedDictionary<decimal, decimal>> f_data;
        public Dictionary<string, SortedDictionary<decimal, decimal>> c_data;
        public Dictionary<string, Dictionary<int, decimal>> year_data;
        public void convert_time_yearly(Dictionary<int,decimal[]> data, List<columns> column_def,bool useCumulative)
        {
            f_data = new Dictionary<string, SortedDictionary<decimal, decimal>>();
            c_data = new Dictionary<string, SortedDictionary<decimal, decimal>>();
            List<int> ind = data.Keys.ToList();
            int time = column_def.Where(c => c.definition.ToLower() == "time").Select(c => c.column_num-1).FirstOrDefault();
            decimal start_year = column_def.Where(c => c.definition.ToLower() == "time").Select(c => c.conv_factor).FirstOrDefault();
            if (start_year < 1000)
                start_year = 0;
            int first = -1;
            foreach (int i in ind)
            {
                foreach (columns col in column_def)
                {
                    //Time is used in the key, if "" then skip
                    if (!col.time && col.definition != "")
                    {
                        //check key exists in new data
                        if (f_data.ContainsKey(col.definition))
                        {
                            
                            //if definition has multiple columns to be added together
                            if (f_data[col.definition].ContainsKey(data[i][time]))
                            {
                                //only grab the first row of a unique year (so if there are 3 rows marked as 2006 only 
                                //process the first row and skip the other two).  2006 and 2006.001 are both unique when
                                //compared against each other.
                                if (first == i)
                                {
                                    f_data[col.definition][data[i][time]] += (data[i][col.column_num - 1] * col.conv_factor);
                                }
                            }
                            else
                            {
                                f_data[col.definition].Add(data[i][time]+start_year, (data[i][col.column_num - 1] * col.conv_factor));
                                first = i;
                            }
                        }
                        else
                        {
                            f_data.Add(col.definition, new SortedDictionary<decimal, decimal>());
                            f_data[col.definition].Add(data[i][time]+start_year, (data[i][col.column_num - 1] * col.conv_factor));
                            first = i;
                        }
                        if (useCumulative)
                        {
                            //check key exists in new data
                            if (c_data.ContainsKey(col.definition))
                            {

                                //if definition has multiple columns to be added together
                                if (c_data[col.definition].ContainsKey(data[i][time]))
                                {
                                    //only grab the first row of a unique year (so if there are 3 rows marked as 2006 only 
                                    //process the first row and skip the other two).  2006 and 2006.001 are both unique when
                                    //compared against each other.
                                    if (first == i)
                                    {
                                        c_data[col.definition][data[i][time]] += (data[i][col.column_num] * col.conv_factor);
                                    }
                                }
                                else
                                {
                                    c_data[col.definition].Add(data[i][time] + start_year, (data[i][col.column_num] * col.conv_factor));
                                    first = i;
                                }
                            }
                            else
                            {
                                c_data.Add(col.definition, new SortedDictionary<decimal, decimal>());
                                c_data[col.definition].Add(data[i][time] + start_year, (data[i][col.column_num] * col.conv_factor));
                                first = i;
                            }
                        }
                    }
                }
                //foreach (columns col in column_def)
               // {

                    
                    //Time is used in the key, if "" then skip
                   // if (!col.time && col.definition != "")
                    //{
                        //if(data[i][time] == 2059 && col.column_num == 18)
                        //{
                        //    decimal x = 0;
                        //}
                        //decimal time_dif = 1; 
                        //decimal temp = 0;
                        ////if column does not exist create it
                        //if (!c_data.ContainsKey(col.definition))
                        //{ 
                        //    c_data.Add(col.definition, new Dictionary<decimal, decimal>());
                        //}

                        ////if time step already exists add new data to it otherwise create it
                        //if (c_data[col.definition].ContainsKey(data[i][time]) )
                        //{
                        //    //then do nothing, 
                        //    if (i > 1)
                        //    {
                        //        time_dif = data[i][time] - data[i - 1][time];
                        //    }
                        //    c_data[col.definition][data[i][time]] += data[i][col.column_num - 1] * time_dif;
                        //}
                        //else
                        //{
                        //    //if previous year exists retrieve its value
                        //    if (i > 1 )
                        //    {
                        //        //time_dif = data[i][time] - data[i - 1][time];
                        //        if (c_data[col.definition].ContainsKey(data[i - 1][time]))
                        //        {
                        //            temp = c_data[col.definition][data[i - 1][time]];
                        //        }
                        //    }
                        //    c_data[col.definition].Add(data[i][time], temp + (data[i][col.column_num - 1] * time_dif));
                        //}
                        ////get previous data value and add new data value to it.
                        //if (c_data[col.definition].Keys.Count > 0)
                        //{
                        //    temp = c_data[col.definition][data[i - 1][time]] + data[i][col.column_num - 1];
                        //}
                        //else
                        //{
                        //    temp = data[i][col.column_num - 1];
                        //}
                        //if(!c_data[col.definition].ContainsKey(data[i][time]))
                        //{
                        //    c_data[col.definition].Add(data[i][time], temp);
                        //}
                        //else
                        //{
                        //    c_data[col.definition][data[i][time]] = c_data[col.definition][data[i][time]] + data[i][col.column_num - 1];
                        //}
                   // }
                //}
            }
            if (!useCumulative)
            {
                process_cumulative();
            }
            interpolate_years();
        }
        private void process_cumulative()
        {
            foreach(string key in f_data.Keys)
            {
                c_data.Add(key, new SortedDictionary<decimal, decimal>());
                decimal last_yr = -1;
                foreach(decimal yr in f_data[key].Keys)
                {
                    if (last_yr > -1)
                    {
                        decimal dif = yr - last_yr;
                        decimal x = c_data[key][last_yr] + (f_data[key][yr] * dif);
                        c_data[key].Add(yr, x);
                        last_yr = yr;
                    }
                    else
                    {
                        c_data[key].Add(yr, f_data[key][yr]);
                        last_yr = yr;
                    }
                }
            }
        }
        private void interpolate_years()
        {
            year_data = new Dictionary<string, Dictionary<int, decimal>>();
            foreach (string key in f_data.Keys)
            {
                SortedDictionary<decimal, decimal> data = f_data[key];
                year_data.Add(key, new Dictionary<int, decimal>());
                int max = (int)Math.Floor(data.Keys.ToList().Max());
                if(max > 15000)
                {
                    max = 15000;
                }
                int min = (int)Math.Floor(data.Keys.ToList().Min());
                for(int i = min; i <= max; i++)
                {
                    if(data.ContainsKey(i))
                    {
                        if (i == min || i == max)
                            year_data[key].Add(i, data[i]);
                        else
                        {
                            decimal year1 = c_data[key].Keys.ToList().Where(k => k < i).Max();
                            if (c_data[key].ContainsKey(i - 1))
                            {
                                year1 = i - 1;
                            }
                            decimal val1 = c_data[key][year1];
                            decimal val2 = c_data[key][i];
                            decimal x = val2 - val1;
                            year_data[key].Add(i, x);
                        }
                    }
                    else
                    {
                        decimal year1 = i;
                        
                        if (i != min)
                            year1 = c_data[key].Keys.ToList().Where(k => k < i).Max();

                        
                        if(c_data[key].ContainsKey(i-1))
                        {
                            year1 = i-1;
                        }

                        decimal val1 = 0;
                        if (i != min)
                        {
                            val1 = c_data[key][year1];
                        }
                        decimal year2 = c_data[key].Keys.ToList().Where(k => k > i).Min();
                        decimal val2 = c_data[key][year2];
                        decimal x = 0;
                        //if (i == 12011)
                        //    x = x;
                        if (val1 != 0 || val2 != 0)
                        {
                            
                            x = val1 + (((i - year1) / (year2 - year1)) * (val2 - val1));
                            c_data[key].Add(i, x);
                            x -= val1;
                            //decimal x1 = i - year1;
                            //decimal x2 = year2 - year1;
                            //decimal x3 = x1 / x2;
                            //decimal x4 = val2 - val1;
                            //decimal x5 = x4 * x3;
                            //decimal x6 = val1 + x5;
                            //decimal x7 = val1 + (x1 / x2) * x4;
                        }

                        year_data[key].Add(i, x);
                    }
                }
                //int max = (int)Math.Round(data.Keys.ToList().Max(), 0);
                //int min = (int)Math.Floor(data.Keys.ToList().Min());
                //decimal last_year = min;
                //foreach(decimal year in data.Keys.ToList().OrderBy(d => d))
                //{
                //    if (Math.Round(year,0) == min)
                //    {
                //        if (Math.Round(last_year, 0) == Math.Round(year, 0) && year_data[key].ContainsKey(min))
                //        {

                    //            year_data[key][min] += data[year];
                    //        }
                    //        else
                    //        {
                    //            year_data[key].Add(min, data[year]);
                    //            last_year = year;
                    //            min++;
                    //        }
                    //    }                    
                    //    else if (min < year)
                    //    {
                    //        decimal dif = year - last_year;
                    //        //if(dif >= 1)
                    //        //{
                    //        while (min <= year)
                    //        {
                    //            year_data[key].Add(min, data[year] / dif);
                    //            last_year = year;
                    //            min++;
                    //        }
                    //    }
                    //}
            }

        }

    }
}
